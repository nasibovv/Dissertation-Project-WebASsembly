import subprocess
import mysql.connector
from datetime import datetime
import re
import time

# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="db_user",
    password="Salam123!",
    database="system_info"
)
cursor = db.cursor()

# Define a function to insert data into MySQL
def insert_execsnoop(event_time, comm, pid, ppid, ret, args):
    sql = "INSERT INTO execsnoop_kernel_monitoring (time, comm, pid, ppid, ret, args) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (event_time, comm, pid, ppid, ret, args)
    cursor.execute(sql, val)
    db.commit()

# Function to run a command and capture output
def run_command(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

# Function to skip headers
def skip_header(line):
    header_patterns = [
        r'PCOMM\s+PID\s+PPID\s+RET\s+ARGS',
        r'^$'
    ]
    for pattern in header_patterns:
        if re.match(pattern, line):
            return True
    return False

# Parse execsnoop output
def parse_execsnoop_output(line):
    if skip_header(line):
        return
    parts = line.split(maxsplit=4)
    if len(parts) < 5:
        return
    try:
        event_time = datetime.now()
        comm = parts[0]
        pid = int(parts[1])
        ppid = int(parts[2])
        ret = int(parts[3])
        args = parts[4]
        insert_execsnoop(event_time, comm, pid, ppid, ret, args)
    except (ValueError, IndexError) as e:
        print(f"Error parsing execsnoop output: {e}, line: {line}")

# Command to run execsnoop
command = "/usr/share/bcc/tools/execsnoop"

try:
    while True:
        print(f"Running command: {command}")
        process = run_command(f"{command}")

        while True:
            stdout_line = process.stdout.readline()
            if stdout_line:
                stdout_line = stdout_line.strip()
                print(f"execsnoop stdout: {stdout_line}")
                parse_execsnoop_output(stdout_line)

            if process.poll() is not None:
                break

        stderr_line = process.stderr.read()
        if stderr_line:
            print(f"execsnoop stderr: {stderr_line.strip()}")

        time.sleep(1)  # Sleep for a second before running the command again

except KeyboardInterrupt:
    process.terminate()

# Close the connection
cursor.close()
db.close()
