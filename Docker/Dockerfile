# Use Ubuntu 24.04 LTS as the base image
FROM ubuntu:24.04

# Install BIND9, Python, and Prometheus Bind Exporter
RUN apt-get update && \
    apt-get install -y dnsutils bind9 bind9utils bind9-doc python3 python3-pip python3-venv wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create directories for BIND configuration
RUN mkdir -p /etc/bind/zones

# Set up the Flask app
WORKDIR /app
COPY app.py /app
COPY requirements.txt /app
RUN python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt

# Copy BIND configuration files
COPY named.conf /etc/bind/named.conf

# Install and configure Prometheus Bind Exporter
RUN wget https://github.com/prometheus-community/bind_exporter/releases/download/v0.5.0/bind_exporter-0.5.0.linux-amd64.tar.gz && \
    tar -xzf bind_exporter-0.5.0.linux-amd64.tar.gz && \
    mv bind_exporter-0.5.0.linux-amd64/bind_exporter /usr/local/bin/ && \
    rm -rf bind_exporter-0.5.0.linux-amd64*

# Expose ports
EXPOSE 53/udp 53/tcp 5000 9119

# Copy and set up the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Start the services
CMD ["/entrypoint.sh"]
