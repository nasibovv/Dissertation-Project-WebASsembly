# Dissertation-Project-WebASsembly
Central Monitoring system leveraging WebAssembly

For running the system, just execute command one-by-one as written below:

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3 python3-pip
pip3 install mysql-connector-python
sudo apt-get install bpfcc-tools libbpfcc-dev linux-headers-$(uname -r)
sudo apt-get install mysql-server
sudo mysql_secure_installation

# MySQL commands
sudo mysql -u root -p

CREATE DATABASE system_info;
USE system_info;

CREATE TABLE IF NOT EXISTS execsnoop_kernel_monitoring (
            id INT AUTO_INCREMENT PRIMARY KEY,
            time TIMESTAMP,
            comm VARCHAR(255),
            pid INT,
            ppid INT,
            ret INT,
            args VARCHAR(1024)
        );
		
CREATE TABLE IF NOT EXISTS funccount_kernel_monitoring (
            id INT AUTO_INCREMENT PRIMARY KEY,
            time TIMESTAMP,
            func VARCHAR(255),
            count BIGINT
        );

CREATE TABLE IF NOT EXISTS biosnoop_kernel_monitoring (
            id INT AUTO_INCREMENT PRIMARY KEY,
            time TIMESTAMP,
            comm VARCHAR(255),
            pid INT,
            type CHAR(1),
            dev VARCHAR(255),
            block BIGINT,
            bytes BIGINT,
            latency_ms FLOAT
        );
		
CREATE TABLE opensnoop_kernel_monitoring (
            id INT AUTO_INCREMENT PRIMARY KEY,
            time TIMESTAMP,
            pid INT,
            comm VARCHAR(255),
            fd INT,
            err INT,
            path VARCHAR(255)
        );


CREATE USER 'db_user'@'%' IDENTIFIED BY 'Salam123!';
GRANT ALL PRIVILEGES ON system_info.* TO 'db_user'@'%';
FLUSH PRIVILEGES;

exit;

sudo python3 <python_file.py>
