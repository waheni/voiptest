# VoIPTest Docker Image - Development Environment
# Contains Python 3.10+, SIPp, and Python dependencies
# Mount your code as a volume for live development!

FROM ubuntu:22.04

# Prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies and Python
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    build-essential \
    cmake \
    libncurses5-dev \
    libssl-dev \
    libpcap-dev \
    libsctp-dev \
    && rm -rf /var/lib/apt/lists/*

# Build and install SIPp from source
RUN git clone --depth 1 --branch v3.7.3 https://github.com/SIPp/sipp.git /tmp/sipp && \
    cd /tmp/sipp && \
    cmake . -DUSE_SSL=1 -DUSE_SCTP=1 -DUSE_PCAP=1 && \
    make && \
    make install && \
    cd / && rm -rf /tmp/sipp

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# Create app directory for dependencies installation
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt ./

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel && \
    pip3 install --no-cache-dir -r requirements.txt

# Copy project files for installation
COPY setup.py pyproject.toml ./
COPY voiptest/ ./voiptest/

# Install voiptest package
RUN pip3 install --no-cache-dir .

# Copy entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Set working directory for mounted code
WORKDIR /work

# Set Python path to include /work for module imports (dev mode)
ENV PYTHONPATH=/work:$PYTHONPATH

# Use wrapper script as entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["--help"]

# Default command (show help)
CMD ["--help"]
