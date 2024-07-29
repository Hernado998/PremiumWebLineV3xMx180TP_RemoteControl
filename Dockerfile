# Stage 1: Build stage
FROM centos:8 AS builder

# Update repository configuration to use vault.centos.org
RUN sed -i 's/mirrorlist=/#mirrorlist=/g' /etc/yum.repos.d/*.repo && \
    sed -i 's/#baseurl=/baseurl=/g' /etc/yum.repos.d/*.repo && \
    sed -i 's/mirror.centos.org/vault.centos.org/g' /etc/yum.repos.d/*.repo

# Install necessary build tools, Python, pip, and development libraries
RUN yum update -y && \
    yum install -y epel-release && \
    yum install -y wget && \
    yum install -y python3 python3-pip gcc gcc-c++ make && \
    yum clean all && \
    rm -rf /var/cache/yum

# Upgrade pip and install wheel and pyinstaller
RUN pip3 install --upgrade pip && \
    pip3 install wheel pyinstaller requests bs4

# Set up the working directory and copy the application code
WORKDIR /power_app
COPY . /power_app

# Generate the binary using PyInstaller
RUN pyinstaller --onefile main.py

# Stage 2: Final image
FROM centos:8

# Update repository configuration to use vault.centos.org
RUN sed -i 's/mirrorlist=/#mirrorlist=/g' /etc/yum.repos.d/*.repo && \
    sed -i 's/#baseurl=/baseurl=/g' /etc/yum.repos.d/*.repo && \
    sed -i 's/mirror.centos.org/vault.centos.org/g' /etc/yum.repos.d/*.repo

# Install wget in the final image
RUN yum update -y && \
    yum install -y wget && \
    yum clean all && \
    rm -rf /var/cache/yum

# Copy only the necessary binary from the builder stage
COPY --from=builder /power_app/dist/main /usr/local/bin/main

# Set the entry point command to run the generated binary
ENTRYPOINT ["/usr/local/bin/main"]
