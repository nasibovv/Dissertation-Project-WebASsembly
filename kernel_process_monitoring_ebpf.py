import subprocess
import mysql.connector
from datetime import datetime
import re

# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="db_user",
    password="Salam123!",
    database="system_info"
)
cursor = db.cursor()

# Define functions to insert data into MySQL
def insert_opensnoop(event_time, pid, comm, fd, err, path):
    sql = "INSERT INTO opensnoop_kernel_monitoring (time, pid, comm, fd, err, path) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (event_time, pid, comm, fd, err, path)
    cursor.execute(sql, val)
    db.commit()

def insert_execsnoop(event_time, comm, pid, ppid, ret, args):
    sql = "INSERT INTO execsnoop_kernel_monitoring (time, comm, pid, ppid, ret, args) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (event_time, comm, pid, ppid, ret, args)
    cursor.execute(sql, val)
    db.commit()

def insert_funccount(event_time, func, count):
    sql = "INSERT INTO funccount_kernel_monitoring (time, func, count) VALUES (%s, %s, %s)"
    val = (event_time, func, count)
    cursor.execute(sql, val)
    db.commit()

# Function to run a command and capture output
def run_command(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Function to skip headers
def skip_header(line, header_pattern):
    return re.match(header_pattern, line) is not None

# Parse opensnoop output
def parse_opensnoop_output(line):
    if skip_header(line, r'^PID\s+COMM\s+FD\s+ERR\s+PATH'):
        return
    parts = line.split(maxsplit=5)
    if len(parts) < 6:
        return
    try:
        time = datetime.now()
        pid = int(parts[0])
        comm = parts[1]
        fd = int(parts[2])
        err = int(parts[3])
        path = parts[4]
        insert_opensnoop(time, pid, comm, fd, err, path)
    except (ValueError, IndexError) as e:
        print(f"Error parsing opensnoop output: {e}, line: {line}")

# Parse execsnoop output
def parse_execsnoop_output(line):
    if skip_header(line, r'^PCOMM\s+PID\s+PPID\s+RET\s+ARGS'):
        return
    parts = line.split(maxsplit=5)
    if len(parts) < 5:
        return
    try:
        time = datetime.now()
        comm = parts[0]
        pid = int(parts[1])
        ppid = int(parts[2])
        ret = int(parts[3])
        args = parts[4]
        insert_execsnoop(time, comm, pid, ppid, ret, args)
    except (ValueError, IndexError) as e:
        print(f"Error parsing execsnoop output: {e}, line: {line}")

# Parse funccount output
def parse_funccount_output(line):
    if skip_header(line, r'^FUNC\s+COUNT'):
        return
    parts = line.split()
    if len(parts) < 2:
        return
    try:
        time = datetime.now()
        func = parts[0]
        count = int(parts[1])
        insert_funccount(time, func, count)
    except (ValueError, IndexError) as e:
        print(f"Error parsing funccount output: {e}, line: {line}")

# Run commands and parse outputs
commands = {
    'opensnoop': ("/usr/sbin/opensnoop-bpfcc", parse_opensnoop_output),
    'execsnoop': ("/usr/sbin/execsnoop-bpfcc", parse_execsnoop_output),
    'funccount': ("/usr/sbin/funccount-bpfcc -i 10 't:sched:sched_switch'", parse_funccount_output)
}

processes = {}
for name, (cmd, parser) in commands.items():
    print(f"Running command: sudo {cmd}")
    processes[name] = (run_command(f"sudo {cmd}"), parser)

try:
    while True:
        for name, (process, parser) in processes.items():
            stdout_line = process.stdout.readline().strip()
            stderr_line = process.stderr.readline().strip()

            if stdout_line:
                if name == 'funccount' and stdout_line.startswith('FUNC'):
                    continue  # Skip the FUNC COUNT header line for funccount
                parser(stdout_line)
            if stderr_line:
                print(f"{name} stderr: {stderr_line}")

except KeyboardInterrupt:
    for process, _ in processes.values():
        process.terminate()

# Close the connection
cursor.close()
db.close()

