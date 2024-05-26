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


--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
wget https://github.com/iovisor/bcc/releases/download/v0.25.0/bcc-src-with-submodule.tar.gz

tar xf bcc-src-with-submodule.tar.gz

cd bcc/

apt install -y python-is-python3

apt install -y bison build-essential cmake flex git libedit-dev libllvm11 llvm-11-dev libclang-11-dev zlib1g-dev libelf-dev libfl-dev python3-distutils

apt install -y checkinstall

mkdir build

cd build/



sudo apt-get install llvm-11 llvm-11-dev clang-11

export LLVM_DIR=/usr/lib/llvm-11

export C_INCLUDE_PATH=/usr/include/llvm-11

export CPLUS_INCLUDE_PATH=/usr/include/llvm-11

export LIBRARY_PATH=/usr/lib/llvm-11/lib



vim /home/ubuntu_server/bcc/src/cc/frontends/clang/b_frontend_action.cc

starts_with --> startswith (326, 378, 892, 1402)


vim /home/ubuntu_server/bcc/CMakeLists.txt

include_directories("/usr/include/llvm-11" "/usr/include/llvm-11/llvm-c")

link_directories("/usr/lib/llvm-11/lib")



cmake -DCMAKE_CXX_FLAGS="-I/usr/include/llvm-11 -I/usr/include/llvm-11/llvm-c" -DCMAKE_EXE_LINKER_FLAGS="-L/usr/lib/llvm-11/lib" -DLLVM_DIR=/usr/lib/llvm-11/cmake/llvm ..

make

checkinstall


(if needed 

make clean

rm -rf * )
