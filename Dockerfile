# Unified Agent Zero + Ollama + n8n Container
FROM agent0ai/agent-zero-base:latest

ARG BRANCH=main
ENV BRANCH=$BRANCH

# Install zstd (required by Ollama installer) and Ollama
RUN apt-get update && apt-get install -y zstd && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://ollama.com/install.sh | sh

# Install PostgreSQL
RUN apt-get update && apt-get install -y \
    postgresql \
    postgresql-contrib \
    && rm -rf /var/lib/apt/lists/*

# Install n8n globally
RUN npm install -g n8n

# Copy filesystem files if they exist
COPY --from=agent0ai/agent-zero:latest / /tmp/agent-zero-base/
RUN if [ -d /tmp/agent-zero-base/ins ]; then cp -r /tmp/agent-zero-base/ins /; fi
RUN if [ -d /tmp/agent-zero-base/exe ]; then cp -r /tmp/agent-zero-base/exe /; fi

# Create supervisord config directory
RUN mkdir -p /etc/supervisor/conf.d

# Copy supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/unified.conf

# Copy initialization scripts
COPY init-db.sh /usr/local/bin/init-db.sh
RUN chmod +x /usr/local/bin/init-db.sh

# Expose all necessary ports
EXPOSE 22 80 5678 11434 5432 9000-9009

# Initialize and start all services via supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]