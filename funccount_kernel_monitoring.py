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
def insert_funccount(event_time, func, count):
    sql = "INSERT INTO funccount_kernel_monitoring (time, func, count) VALUES (%s, %s, %s)"
    val = (event_time, func, count)
    cursor.execute(sql, val)
    db.commit()

# Function to run a command and capture output
def run_command(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

# Function to skip headers
def skip_header(line):
    header_patterns = [
        r'^FUNC\s+COUNT',
        r'^Tracing\s+\d+\s+functions',
        r'^$'
    ]
    for pattern in header_patterns:
        if re.match(pattern, line):
            return True
    return False

# Parse funccount output
def parse_funccount_output(line):
    if skip_header(line):
        return
    parts = line.split()
    if len(parts) < 2:
        return
    try:
        event_time = datetime.now()
        func = parts[0]
        count = int(parts[1])
        insert_funccount(event_time, func, count)
    except (ValueError, IndexError) as e:
        print(f"Error parsing funccount output: {e}, line: {line}")

# Command to run funccount
command = "/usr/sbin/funccount-bpfcc -d 10 't:sched:sched_switch'"

try:
    while True:
        print(f"Running command: {command}")
        process = run_command(f"{command}")

        while True:
            stdout_line = process.stdout.readline()
            if stdout_line:
                stdout_line = stdout_line.strip()
                print(f"funccount stdout: {stdout_line}")
                parse_funccount_output(stdout_line)

            if process.poll() is not None:
                break

        stderr_line = process.stderr.read()
        if stderr_line:
            print(f"funccount stderr: {stderr_line.strip()}")

        time.sleep(1)  # Sleep for a second before running the command again

except KeyboardInterrupt:
    process.terminate()

# Close the connection
cursor.close()
db.close()
