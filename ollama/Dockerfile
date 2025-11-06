# Use the official Ollama image
FROM ollama/ollama:latest

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Expose the Ollama API port
EXPOSE 11434

# Use bash -c to run commands
ENTRYPOINT ["bash", "-c", "\
    echo 'Starting Ollama server...' && \
    ollama serve & \
    OLLAMA_PID=$! && \
    echo 'Waiting for Ollama to be ready...' && \
    until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do \
        echo 'Waiting for Ollama API...' && \
        sleep 2; \
    done && \
    echo 'Ollama is ready. Pulling model: '${OLLAMA_MODEL:-gemma:3b} && \
    ollama pull ${OLLAMA_MODEL:-gemma:3b} && \
    echo 'Model ready. Ollama API available at http://localhost:11434' && \
    wait $OLLAMA_PID \
"]