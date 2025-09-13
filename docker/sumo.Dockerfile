FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV SUMO_HOME=/usr/share/sumo
ENV PATH=$PATH:$SUMO_HOME/bin

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    wget \
    curl \
    git \
    libxerces-c-dev \
    libproj-dev \
    libgdal-dev \
    libfox-1.6-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libosmesa6-dev \
    && rm -rf /var/lib/apt/lists/*

# Install SUMO
RUN wget https://sumo.dlr.de/releases/1.18.0/sumo-src-1.18.0.tar.gz \
    && tar -xzf sumo-src-1.18.0.tar.gz \
    && cd sumo-1.18.0 \
    && ./configure \
    && make \
    && make install \
    && cd .. \
    && rm -rf sumo-1.18.0 sumo-src-1.18.0.tar.gz

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Set working directory
WORKDIR /app

# Copy application code
COPY simulation/ ./simulation/
COPY config/ ./config/
COPY data/ ./data/

# Create necessary directories
RUN mkdir -p /app/logs /app/data/sumo /app/data/traffic

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python3 -c "import traci; print('SUMO is ready')" || exit 1

# Run the application
CMD ["python3", "simulation/sumo_controller.py"]
