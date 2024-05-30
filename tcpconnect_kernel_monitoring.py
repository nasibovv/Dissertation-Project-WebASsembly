import subprocess
import mysql.connector
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
def insert_tcpconnect(pid, comm, ip_version, saddr, daddr, dport):
    sql = "INSERT INTO tcpconnect_kernel_monitoring (pid, comm, ip_version, saddr, daddr, dport) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (pid, comm, ip_version, saddr, daddr, dport)
    cursor.execute(sql, val)
    db.commit()

# Function to run a command and capture output
def run_command(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

# Function to skip headers
def skip_header(line):
    header_patterns = [
        r'^PID\s+COMM\s+IP\s+SADDR\s+DADDR\s+DPORT',
        r'^Tracing\s+connect',
        r'^$'
    ]
    for pattern in header_patterns:
        if re.match(pattern, line):
            return True
    return False

# Parse tcpconnect output
def parse_tcpconnect_output(line):
    if skip_header(line):
        return
    parts = line.split()
    if len(parts) < 6:
        return
    try:
        pid = int(parts[0])
        comm = parts[1]
        ip_version = parts[2]
        saddr = parts[3]
        daddr = parts[4]
        dport = int(parts[5])
        insert_tcpconnect(pid, comm, ip_version, saddr, daddr, dport)
    except (ValueError, IndexError) as e:
        print(f"Error parsing tcpconnect output: {e}, line: {line}")

# Command to run tcpconnect
command = "/usr/share/bcc/tools/tcpconnect"

try:
    while True:
        print(f"Running command: sudo {command}")
        process = run_command(f"sudo {command}")

        while True:
            stdout_line = process.stdout.readline()
            if stdout_line:
                stdout_line = stdout_line.strip()
                print(f"tcpconnect stdout: {stdout_line}")
                parse_tcpconnect_output(stdout_line)

            if process.poll() is not None:
                break

        stderr_line = process.stderr.read()
        if stderr_line:
            print(f"tcpconnect stderr: {stderr_line.strip()}")

        time.sleep(1)  # Sleep for a second before running the command again

except KeyboardInterrupt:
    process.terminate()

# Close the connection
cursor.close()
db.close()
