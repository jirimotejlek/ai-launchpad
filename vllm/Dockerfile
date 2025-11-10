# Use the official vLLM OpenAI-compatible server image
FROM vllm/vllm-openai:latest

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Expose the vLLM API port (OpenAI-compatible)
EXPOSE 8000

# Set environment variables with defaults
ENV VLLM_MODEL=${VLLM_MODEL:-"facebook/opt-125m"}
ENV VLLM_HOST="0.0.0.0"
ENV VLLM_PORT="8000"
ENV VLLM_GPU_MEMORY_UTILIZATION=${VLLM_GPU_MEMORY_UTILIZATION:-"0.85"}
ENV HUGGING_FACE_HUB_TOKEN=${HUGGING_FACE_HUB_TOKEN:-""}

# Use bash -c to run vLLM with OpenAI-compatible API
ENTRYPOINT ["bash", "-c", "\
    echo 'Starting vLLM server with OpenAI-compatible API...' && \
    echo 'Model: '${VLLM_MODEL} && \
    if [ -n \"${HUGGING_FACE_HUB_TOKEN}\" ]; then \
        echo 'Using HuggingFace authentication token' && \
        export HUGGING_FACE_HUB_TOKEN=${HUGGING_FACE_HUB_TOKEN}; \
    fi && \
    python3 -m vllm.entrypoints.openai.api_server \
        --model ${VLLM_MODEL} \
        --host ${VLLM_HOST} \
        --port ${VLLM_PORT} \
        --dtype auto \
        --gpu-memory-utilization ${VLLM_GPU_MEMORY_UTILIZATION} \
        --max-model-len 2048 \
"]

