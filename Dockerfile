# Dockerfile for P4 and Mininet Environment
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Update and install basic tools including gnupg and curl
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gnupg2 \
    ca-certificates \
    iproute2 \
    net-tools \
    tcpdump \
    python-is-python3 \
    python3-pip \
    mininet \
    && rm -rf /var/lib/apt/lists/*

# Add P4 Repository and install P4 tools (Using trusted=yes to bypass expired GPG key)
RUN echo 'deb [trusted=yes] http://download.opensuse.org/repositories/home:/p4lang/xUbuntu_20.04/ /' | tee /etc/apt/sources.list.d/home:p4lang.list && \
    curl -fsSL https://download.opensuse.org/repositories/home:p4lang/xUbuntu_20.04/Release.key | gpg --dearmor | tee /etc/apt/trusted.gpg.d/home_p4lang.gpg > /dev/null && \
    apt-get update -y --allow-insecure-repositories || true && \
    apt-get install -y --no-install-recommends --allow-unauthenticated \
    p4lang-p4c \
    p4lang-bmv2 \
    && rm -rf /var/lib/apt/lists/*

# Install Scapy for packet generation
RUN pip3 install scapy

WORKDIR /app
COPY . /app

# Compile the P4 program by default when the container builds (optional, can be done at runtime)
RUN p4c-bm2-ss --p4v 16 -o /app/ddos_mitigation.json /app/p4-src/ddos_mitigation.p4

CMD ["/bin/bash"]
