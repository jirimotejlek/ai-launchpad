FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Build argument for LLM provider
ARG LLM_PROVIDER=local

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install base Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Conditionally install LLM provider packages
RUN if [ "$LLM_PROVIDER" = "openai" ]; then \
        pip install --no-cache-dir openai==1.97.1; \
    elif [ "$LLM_PROVIDER" = "anthropic" ]; then \
        pip install --no-cache-dir anthropic==0.57.1; \
    elif [ "$LLM_PROVIDER" = "mistral" ]; then \
        pip install --no-cache-dir mistralai==1.9.2; \
    fi

# Copy application code
COPY . .

# Expose port
EXPOSE 5100

# Run the application
CMD ["python", "app.py"]