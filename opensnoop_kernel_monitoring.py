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
def insert_opensnoop(event_time, pid, comm, fd, err, path):
    sql = "INSERT INTO opensnoop_kernel_monitoring (time, pid, comm, fd, err, path) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (event_time, pid, comm, fd, err, path)
    cursor.execute(sql, val)
    db.commit()

# Function to run a command and capture output
def run_command(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

# Function to skip headers
def skip_header(line):
    header_patterns = [
        r'PID\s+COMM\s+FD\s+ERR\s+PATH',
        r'^$'
    ]
    for pattern in header_patterns:
        if re.match(pattern, line):
            return True
    return False

# Parse opensnoop output
def parse_opensnoop_output(line):
    if skip_header(line):
        return
    parts = line.split()
    if len(parts) < 5:
        return
    try:
        event_time = datetime.now()
        pid = int(parts[0])
        comm = parts[1]
        fd = int(parts[2])
        err = int(parts[3])
        path = ' '.join(parts[4:])
        insert_opensnoop(event_time, pid, comm, fd, err, path)
    except (ValueError, IndexError) as e:
        print(f"Error parsing opensnoop output: {e}, line: {line}")

# Command to run opensnoop
command = "/usr/share/bcc/tools/opensnoop"

try:
    while True:
        print(f"Running command: {command}")
        process = run_command(f"{command}")

        while True:
            stdout_line = process.stdout.readline()
            if stdout_line:
                stdout_line = stdout_line.strip()
                print(f"opensnoop stdout: {stdout_line}")
                parse_opensnoop_output(stdout_line)

            if process.poll() is not None:
                break

        stderr_line = process.stderr.read()
        if stderr_line:
            print(f"opensnoop stderr: {stderr_line.strip()}")

        time.sleep(1)  # Sleep for a second before running the command again

except KeyboardInterrupt:
    process.terminate()

# Close the connection
cursor.close()
db.close()
