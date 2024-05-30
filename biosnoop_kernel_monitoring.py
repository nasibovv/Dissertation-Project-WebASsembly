import subprocess
import mysql.connector
from datetime import datetime
import re
import time

# Connect to MySQL database
try:
    db = mysql.connector.connect(
        host="localhost",
        user="db_user",
        password="Salam123!",
        database="system_info"
    )
    cursor = db.cursor()
    print("Connected to the database.")
except mysql.connector.Error as err:
    print(f"Error: {err}")
    exit(1)

# Define a function to insert data into MySQL
def insert_biosnoop(event_time, comm, pid, disk, type, sector, bytes, latency_ms):
    try:
        sql = """
        INSERT INTO biosnoop_kernel_monitoring (
            event_time, comm, pid, disk, type, sector, bytes, latency_ms
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        val = (
            event_time,
            comm if comm else None,
            pid if pid is not None else None,
            disk if disk else None,
            type if type else None,
            sector if sector is not None else None,
            bytes if bytes is not None else None,
            latency_ms if latency_ms is not None else None
        )
        cursor.execute(sql, val)
        db.commit()
        print(f"Inserted into database: {val}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        print(f"Failed to insert: {val}")


# Function to run a command and capture output
def run_command(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

# Function to skip headers
def skip_header(line):
    header_patterns = [
        r'TIME\(s\)\s+COMM\s+PID\s+DISK\s+T\s+SECTOR\s+BYTES\s+LAT\(ms\)',
        r'^$'
    ]
    for pattern in header_patterns:
        if re.match(pattern, line):
            return True
    return False

# Parse biosnoop output
def parse_biosnoop_output(line):
    if skip_header(line):
        return

    parts = re.split(r'\s+', line.strip())
    if len(parts) == 7:
        parts.insert(3, '')  # Insert an empty string for the missing disk field

    if len(parts) == 8:
        try:
            event_time = datetime.now()
            comm = parts[1]
            pid = int(parts[2]) if parts[2] and parts[2].isdigit() else None
            disk = parts[3] if parts[3] else None
            type = parts[4]
            sector = int(parts[5]) if parts[5].isdigit() else None
            bytes = int(parts[6]) if parts[6].isdigit() else None
            latency_ms = float(parts[7]) if parts[7] and re.match(r'^\d+(\.\d+)?$', parts[7]) else None

            print(f"Parts: {parts}")
            print(f"Parsed values: time={event_time}, comm={comm}, pid={pid}, disk={disk}, type={type}, sector={sector}, bytes={bytes}, latency_ms={latency_ms}")
            insert_biosnoop(event_time, comm, pid, disk, type, sector, bytes, latency_ms)
        except (ValueError, IndexError) as e:
            print(f"Error parsing biosnoop output: {e}, line: {line}")


# Command to run biosnoop
command = "/usr/share/bcc/tools/biosnoop"

try:
    while True:
        print(f"Running command: {command}")
        process = run_command(f"{command}")

        while True:
            stdout_line = process.stdout.readline()
            if stdout_line:
                stdout_line = stdout_line.strip()
                print(f"biosnoop stdout: {stdout_line}")
                parse_biosnoop_output(stdout_line)

            if process.poll() is not None:
                break

        stderr_line = process.stderr.read()
        if stderr_line:
            print(f"biosnoop stderr: {stderr_line.strip()}")

        time.sleep(1)  # Sleep for a second before running the command again

except KeyboardInterrupt:
    process.terminate()

# Close the connection
cursor.close()
db.close()
