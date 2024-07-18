# Use CentOS 8 as the base image
FROM centos:8

# Update repository configuration to use vault.centos.org
RUN sed -i 's/mirrorlist=/#mirrorlist=/g' /etc/yum.repos.d/*.repo && \
    sed -i 's/#baseurl=/baseurl=/g' /etc/yum.repos.d/*.repo && \
    sed -i 's/mirror.centos.org/vault.centos.org/g' /etc/yum.repos.d/*.repo

# Install necessary build tools, Python, pip, and development libraries
RUN yum update -y && \
    yum install -y epel-release && \
    yum install -y python3 python3-pip gcc gcc-c++ make && \
    yum clean all

# Upgrade pip and install wheel and pyinstaller
RUN pip3 install --upgrade pip && \
    pip3 install wheel && \
    pip3 install pyinstaller && \
    pip3 install requests

# Set up the working directory and copy the application code
RUN mkdir /power_app
WORKDIR /power_app
COPY . /power_app

# Generate the binary using PyInstaller
RUN pyinstaller --onefile main.py

# Set the entry point command to run the generated binary
CMD ["./dist/main"]
