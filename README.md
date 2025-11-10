# AI Launchpad

A minimal Streamlit AI application template that supports both **local LLM** (via Ollama) and **external LLM providers** (OpenAI, Anthropic, etc.). Perfect for quickly building AI-powered web applications with Docker.

## Features

- **Fully Dockerized** - No local Python installation required
- **Hot Reload** - Code changes appear instantly during development
- **Local LLM Support** - Run Ollama models without API costs
- **External LLM Support** - Connect to OpenAI, Anthropic, Mistral, and more
- **VS Code Dev Containers** - Seamless development experience
- **Production Ready** - Easy switch between dev and prod configurations

---

## Architecture

This template consists of three Docker containers:

- **client** - Streamlit web interface (Python)
- **llm-dispatcher** - API gateway for LLM services (Flask)
- **ollama-llm** - Local LLM runtime with Ollama (only for local mode)
- **vllm** - Alternative local LLM runtime with vLLM (only for local mode)

```
┌─────────────┐
│   Client    │  Streamlit UI (Port 8501)
│  (Streamlit)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│LLM Dispatcher│  API Gateway (Port 5100)
│   (Flask)   │
└──────┬──────┘
       │
       ├──────────┬──────────┐
       ▼          ▼          ▼
  ┌────────┐  ┌──────┐  ┌──────────┐
  │ Ollama │  │ vLLM │  │ External │
  │Port    │  │Port  │  │LLM (API) │
  │11434   │  │8000  │  │          │
  └────────┘  └──────┘  └──────────┘
   (config)    (config)
```

---

## Quick Start

### Local LLM (Default - No API Key Required)

Run everything locally with Ollama:

```bash
# Windows
launchpad build-local
launchpad run-local

# macOS/Linux
chmod +x launchpad.sh
./launchpad.sh build-local
./launchpad.sh run-local
```

Visit `http://localhost:8501`.

**Note:** By default, Ollama is used as the local LLM backend. To switch to vLLM, see [Choosing Local LLM Backend](#choosing-local-llm-backend-ollama-vs-vllm).

**vLLM with gated models:** If using vLLM with gated models (like Gemma or Llama), create a `.env` file with your HuggingFace token. See [Using Gated Models with vLLM](#using-gated-models-with-vllm).

### External LLM Provider

Use OpenAI, Anthropic, or other providers:

#### 1. Create your `.env` file

```bash
# Copy a template
cp env_templates/openai .env

# Or create manually
echo "LLM_PROVIDER=openai" > .env
echo "LLM_API_KEY=your-api-key-here" >> .env
echo "LLM_API_ENDPOINT=https://api.openai.com/v1" >> .env
echo "LLM_MODEL=gpt-3.5-turbo" >> .env
```

#### 2. Build and run

```bash
# Windows
launchpad build-external
launchpad run-external

# macOS/Linux
./launchpad.sh build-external
./launchpad.sh run-external
```

---

## Available Commands

### Windows (`launchpad.bat`)

```batch
launchpad build-local       # Build for local LLM
launchpad build-external    # Build for external LLM
launchpad run-local         # Start with local LLM
launchpad run-external      # Start with external LLM
launchpad stop              # Stop services (keep containers)
launchpad restart           # Restart stopped services
launchpad status            # Show container status
launchpad logs              # View all logs
launchpad logs client       # View specific service logs
launchpad remove            # Remove all containers and volumes
launchpad help              # Show help
```

### macOS/Linux (`launchpad.sh`)

```bash
./launchpad.sh build-local       # Build for local LLM
./launchpad.sh build-external    # Build for external LLM
./launchpad.sh run-local         # Start with local LLM
./launchpad.sh run-external      # Start with external LLM
./launchpad.sh stop              # Stop services (keep containers)
./launchpad.sh restart           # Restart stopped services
./launchpad.sh status            # Show container status
./launchpad.sh logs              # View all logs
./launchpad.sh logs client       # View specific service logs
./launchpad.sh remove            # Remove all containers and volumes
./launchpad.sh help              # Show help
```

---

## Choosing Local LLM Backend: Ollama vs vLLM

This template supports two local LLM backends that you can choose between:

### Ollama (Default)
- **Best for:** Ease of use, beginners, quick setup
- **Pros:** Simple, batteries-included, auto-downloads models
- **Cons:** Slightly slower than vLLM
- **Port:** 11434

### vLLM
- **Best for:** Performance, production workloads, serving at scale
- **Pros:** Faster inference, optimized for throughput, OpenAI-compatible API
- **Cons:** Requires more setup, manual model management, some models need authentication
- **Port:** 8000
- **Default Model:** `facebook/opt-125m` (ungated, no auth required)

### How to Switch

Edit the `local-llm.config` file in the project root:

```bash
# For Ollama (default)
LOCAL_LLM_BACKEND=ollama

# For vLLM
LOCAL_LLM_BACKEND=vllm
```

Then rebuild and restart:

```bash
# Windows
launchpad build-local
launchpad run-local

# macOS/Linux
./launchpad.sh build-local
./launchpad.sh run-local
```

### Model Configuration

**Ollama:** Models are specified in `docker-compose.local.yml` under the `llm` service:
```yaml
OLLAMA_MODEL: "gemma3n:e2b"  # Default
```

**vLLM:** Models are specified in `docker-compose.local.yml` (lines 39 & 73):
```yaml
VLLM_MODEL: ${VLLM_MODEL:-Qwen/Qwen3-4B-Instruct-2507-FP8}
```

You can override this in `.env` file without editing docker-compose:
```bash
VLLM_MODEL=your-preferred-model-name
```

**Note:** vLLM uses HuggingFace model names, while Ollama uses its own naming convention.

**Recommended vLLM Models (ungated, no authentication needed):**
- `facebook/opt-125m` - Very fast, tiny model (<1GB VRAM)
- `facebook/opt-350m` - Slightly larger, better quality (~1GB VRAM)
- `facebook/opt-1.3b` - Good balance of size and quality (~3GB VRAM)
- `TinyLlama/TinyLlama-1.1B-Chat-v1.0` - Efficient chat model (~2GB VRAM)
- `facebook/opt-2.7b` - High quality (~6GB VRAM)
- `microsoft/phi-2` - 2.7B, excellent quality (~6GB VRAM)

**For larger GPUs (16GB+):**
- `Qwen/Qwen2.5-7B-Instruct` - High quality 7B model
- `meta-llama/Llama-3.2-3B-Instruct` - Good 3B model (gated, needs token)

### Using Gated Models with vLLM

Some models (like `google/gemma-2b`, `meta-llama/Llama-2-7b-hf`) are gated and require authentication:

1. **Get a HuggingFace token:**
   - Visit https://huggingface.co/settings/tokens
   - Create a new access token
   - Accept the model's terms on the model page

2. **Create a `.env` file (safe from git):**
   ```bash
   # Option 1: Copy the template
   cp env_templates/vllm.env .env
   
   # Option 2: Create manually
   echo "HUGGING_FACE_HUB_TOKEN=hf_your_token_here" > .env
   echo "VLLM_MODEL=google/gemma-2b" >> .env
   ```
   
   **Note:** `.env` is already in `.gitignore` and won't be committed to git.

3. **Rebuild and restart:**
   ```bash
   launchpad build-local
   launchpad run-local
   ```

The `.env` file will be automatically loaded by docker-compose, keeping your token secure.

---

## Development Workflow

### Daily Development

```bash
# Start in background
launchpad run-local -d

# View logs if needed
launchpad logs

# Stop when done (containers preserved)
launchpad stop

# Resume next day
launchpad restart
```

### Making Changes

Your code is **bind-mounted** into containers, so changes appear immediately:

- Edit files in `client/` → Streamlit auto-reloads
- Edit files in `llm_dispatcher/` → Flask auto-reloads

**Custom Component/Widget Development:**

Streamlit's `developmentMode=true` has known bugs (404 errors, connection issues). For custom component development, use Streamlit's official component template instead:

```bash
# Install Streamlit component tools
pip install streamlit-component-lib

# Create a new component (one-time)
streamlit create my_component

# Or for this project, develop components alongside your app:
cd client
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run your app with hot reload (works reliably)
streamlit run app.py --server.runOnSave=true

# App available at: http://localhost:8501
```

**For Component Development Workflow:**
1. Create components in `client/components/` directory
2. Use the `streamlit.components.v1` API (does not require `developmentMode`)
3. Run with `--server.runOnSave=true` for hot reload
4. See: [Streamlit custom components](https://docs.streamlit.io/develop/concepts/custom-components)

**Why avoid `developmentMode=true`?**
- Known routing bugs (404 errors)
- Port binding issues
- Doesn't work in Docker
- Unreliable even locally
- Not needed for component development (use `streamlit.components.v1` instead)

**Benefits of this approach:**
- Reliable hot reload
- Works on standard port (8501)
- Full component development capabilities
- Same environment as Docker

### When to Rebuild

Rebuild only when you change:
- `requirements.txt` (new Python packages)
- `Dockerfile` (container configuration)
- LLM provider (switching between local and external)

```bash
launchpad build-local    # or build-external
```

---

## VS Code Dev Containers

For the best development experience:

1. Start your containers: `launchpad run-local -d`
2. Press **Ctrl+Shift+P** (Cmd+Shift+P on Mac)
3. Select **"Dev Containers: Attach to Running Container..."**
4. Choose the `client` container
5. Press **Ctrl+Shift+P** again
6. Select **"Dev Containers: Open Folder in Container..."**
7. Choose `/app/`

Now your IDE runs inside the container with full IntelliSense and linting!

---

## Supported LLM Providers

### Local
- **Ollama** - Run models locally (default: `gemma3n:e2b`)
  - No API costs
  - Full privacy
  - Works offline
  - Easy to use
- **vLLM** - High-performance local inference (default: `facebook/opt-125m`)
  - No API costs
  - Full privacy
  - Works offline (after model download)
  - Faster inference
  - OpenAI-compatible API
  - Supports many HuggingFace models

**Choose your backend:** See [Choosing Local LLM Backend](#choosing-local-llm-backend-ollama-vs-vllm)

### External
- **OpenAI** - GPT-4, GPT-3.5-turbo
- **Anthropic** - Claude 3 Opus, Sonnet, Haiku
- **Mistral** - Mistral Large, Medium
- **Custom** - Any OpenAI-compatible API

See `env_templates/` directory for configuration examples.

---

## Troubleshooting

### Container name conflicts

If you get "Conflict. The container name..." errors:

```bash
# Remove old containers
docker rm -f $(docker ps -aq --filter "name=ai-launchpad")

# Or use the remove command
launchpad remove

# Then rebuild
launchpad build-local
launchpad run-local
```

**Note:** Container names are automatically generated as `<directory-name>_<service>_1` (e.g., `ai-launchpad_client_1`). This allows running multiple instances by placing the template in different directories.

### Containers won't start

```bash
# Check status
launchpad status

# View logs
launchpad logs

# Complete reset
launchpad remove
launchpad build-local
launchpad run-local
```

### Port already in use

If port 8501, 5100, or 11434 is already taken:

```bash
# Stop conflicting services
launchpad stop

# Or change ports in docker-compose.base.yml
```

### Connection reset or refused

If you get "connection reset" or "unable to connect" errors:

1. Wait 5-10 seconds for Streamlit to fully start
2. Check if the container is running: `launchpad status`
3. View logs to confirm it's ready: `launchpad logs client`
4. Look for "You can now view your Streamlit app" in the logs
5. Try restarting: `launchpad restart`
6. Clear browser cache or try incognito mode

**Common cause:** Network misconfigurations or the container not being fully ready. Wait 5-10 seconds after starting, then check logs with `launchpad logs client`.

### External LLM not working

Check your `.env` file:
```bash
# Windows
type .env

# macOS/Linux
cat .env
```

Ensure all required variables are set:
- `LLM_PROVIDER` (openai, anthropic, etc.)
- `LLM_API_KEY` (your actual API key)
- `LLM_API_ENDPOINT` (provider's API URL)
- `LLM_MODEL` (model name)

### Local LLM slow or hanging

First run downloads the model (can take several minutes):
```bash
# Check if model is downloading (Ollama)
launchpad logs llm

# Check if model is loading (vLLM)
launchpad logs llm-vllm
```

**Note for vLLM:** Models are cached in a Docker volume (`vllm_cache`), so they only need to be downloaded once. If you need to clear the cache:
```bash
docker volume rm ai-launchpad_vllm_cache
```

### Switching between Ollama and vLLM

If you switch backends in `local-llm.config`, make sure to:
1. Stop the current containers: `launchpad stop`
2. Rebuild for the new backend: `launchpad build-local`
3. Start with the new backend: `launchpad run-local`

### vLLM "Free memory is less than desired" error

If you see "Free memory on device is less than desired GPU memory utilization" error:

**Solution 1: Reduce GPU memory usage (recommended)**
Add to your `.env` file:
```bash
VLLM_GPU_MEMORY_UTILIZATION=0.75
```
Or try even lower values like `0.7` or `0.6` if needed. Then rebuild:
```bash
launchpad build-local
launchpad run-local
```

**Solution 2: Use a smaller model**
Some models that work well on 12GB GPUs:
- `facebook/opt-125m` - Very small (default)
- `facebook/opt-1.3b` - Small but capable
- `microsoft/phi-2` - 2.7B, good quality
- `TinyLlama/TinyLlama-1.1B-Chat-v1.0` - Efficient chat model

**Solution 3: Close other GPU processes**
Check what's using your GPU:
```bash
nvidia-smi
```
Close unnecessary applications using GPU memory.

### vLLM "Cannot access gated repo" error

If you see "Access to model X is restricted" error, the model requires authentication:

**Quick fix:** Use an ungated model (default `facebook/opt-125m` works without authentication)

**To use gated models:**
1. Get a HuggingFace token from https://huggingface.co/settings/tokens
2. Accept the model's terms on its HuggingFace page
3. Create a `.env` file with your token:
   ```bash
   cp env_templates/vllm.env .env
   # Edit .env and add your actual token
   ```
4. Rebuild: `launchpad build-local && launchpad run-local`

**Note:** `.env` is in `.gitignore` so your token stays secure and won't be committed to git.

### vLLM model not found

vLLM requires HuggingFace model names. Make sure:
- The model name is correct (e.g., `facebook/opt-125m`)
- The model is not gated (or you've provided authentication)
- You have sufficient disk space for model download
- Your network can access HuggingFace
- Check logs: `launchpad logs llm-vllm`

---

## Project Structure

```
ai-launchpad/
├── client/                    # Streamlit web interface
│   ├── .streamlit/           # Streamlit configs
│   │   ├── config.dev.toml   # Development (Docker)
│   │   ├── config.prod.toml  # Production
│   │   └── config.widget-dev.toml  # Local widget development
│   ├── venv/                 # Virtual environment (local, not committed)
│   ├── app.py                # Main application
│   ├── Dockerfile            # Client container config
│   └── requirements.txt      # Python dependencies
├── llm_dispatcher/           # LLM API gateway
│   ├── app.py               # Flask API server
│   ├── Dockerfile           # Dispatcher container config
│   └── requirements.txt     # Python dependencies
├── ollama/                   # Ollama LLM configuration
│   └── Dockerfile           # Ollama container config
├── vllm/                     # vLLM configuration
│   └── Dockerfile           # vLLM container config
├── env_templates/           # Environment file templates
│   └── vllm.env            # vLLM with HuggingFace token template
├── .env                     # Your secrets (git-ignored, create from templates)
├── local-llm.config         # Local LLM backend selection (ollama/vllm)
├── Docker volumes:
│   ├── ollama_data          # Ollama models (persistent)
│   └── vllm_cache           # vLLM/HuggingFace models (persistent)
├── docker-compose.base.yml  # Base services
├── docker-compose.local.yml # Local LLM override
├── docker-compose.external.yml # External LLM override
├── launchpad.bat            # Windows management script
└── launchpad.sh             # macOS/Linux management script
```

---

## Running Multiple Instances

Want to run multiple projects based on this template simultaneously?

### Option 1: Different directories (Recommended)
```bash
# Each directory gets unique container names automatically
cp -r ai-launchpad my-project-1
cp -r ai-launchpad my-project-2

cd my-project-1
./launchpad.sh run-local -d

cd ../my-project-2
./launchpad.sh run-local -d  # Works! Different containers
```

### Option 2: Custom project name
```bash
# Use Docker Compose's -p flag for custom project names
docker compose -p my-custom-name -f docker-compose.base.yml -f docker-compose.local.yml up -d
```

**Note:** Each instance needs different ports if running simultaneously. Edit `docker-compose.base.yml` to change port mappings (e.g., `8502:8501` instead of `8501:8501`).

---

## Optional Services

The AI Launchpad supports a modular architecture that makes it easy to add optional services like databases, caching, and more. Services are managed through a simple configuration file.

### Enabling Services

1. **Edit `services.config`** in the project root
2. Set the service to `true`:
   ```bash
   ENABLE_POSTGRES=true
   ```
3. Rebuild and restart:
   ```bash
   # Windows
   launchpad build-local
   launchpad run-local

   # macOS/Linux
   ./launchpad.sh build-local
   ./launchpad.sh run-local
   ```

### Available Services

#### PostgreSQL Database

**Purpose:** User authentication, persistent data storage

**Setup:**

1. Enable in `services.config`:
   ```bash
   ENABLE_POSTGRES=true
   ```

2. Create `.env.postgres` file with database credentials:
   ```bash
   cp env_templates/postgres.env .env.postgres
   # Edit .env.postgres and set a secure password
   ```

3. Start the service:
   ```bash
   launchpad build-local
   launchpad run-local
   ```

**Connection Details:**
- Host: `postgres` (from containers) or `localhost` (from host)
- Port: `5432`
- Database: `ai_launchpad` (configurable in `.env.postgres`)
- User/Password: As configured in `.env.postgres`

**Example Usage (SQLAlchemy):**

Add to your service's `requirements.txt`:
```txt
Flask-SQLAlchemy==3.1.1
psycopg2-binary==2.9.9
```

Connect from `llm_dispatcher/app.py` or `client/app.py`:
```python
from flask_sqlalchemy import SQLAlchemy
import os

# Connection via standard environment variables
db_user = os.getenv('DB_USER', 'admin')
db_name = os.getenv('DB_NAME', 'ai_launchpad')
db_password = os.getenv('POSTGRES_PASSWORD')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@postgres:5432/{db_name}'
db = SQLAlchemy(app)

# Use the pre-created users table
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    preferences = db.Column(db.JSON)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
```

**Security Best Practices:**
- Never commit `.env.postgres` file (already in `.gitignore`)
- Keep it separate from your main `.env` (for LLM configuration)
- Use strong passwords (16+ characters)
- Always hash passwords before storing:
  ```python
  from werkzeug.security import generate_password_hash, check_password_hash
  
  # Creating user
  password_hash = generate_password_hash(password)
  
  # Authenticating
  is_valid = check_password_hash(stored_hash, provided_password)
  ```

**Pre-configured Schema:**

The database automatically initializes with a `users` table:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

For more details, see `postgres/README.md`.

### Adding New Services

The modular architecture makes it easy to add new services:

1. **Create service directory** (e.g., `redis/`) with:
   - `Dockerfile` - Service container configuration
   - `README.md` - Service documentation
   - Any initialization scripts

2. **Create `docker-compose.servicename.yml`**:
   ```yaml
   services:
     servicename:
       build: ./servicename
       image: ai-launchpad-servicename:latest
       restart: unless-stopped
       volumes:
         - servicename_data:/data
       networks:
         - backend

   volumes:
     servicename_data:

   networks:
     backend:
   ```

3. **Add to `services.config`**:
   ```bash
   ENABLE_SERVICENAME=false
   ```

4. **Add volume to `docker-compose.base.yml`**:
   ```yaml
   volumes:
     servicename_data:  # Service description
   ```

5. **Create env template** (if needed):
   ```bash
   echo "# Service Configuration" > env_templates/servicename.env
   ```

The launch scripts will automatically detect and include enabled services - no code changes needed!

---

## Next Steps

This template gives you a working AI application. Here's how to build on it:

### 1. Customize the UI (`client/app.py`)
- Add more Streamlit components
- Create multiple pages
- Add file uploads, charts, forms

### 2. Extend the API (`llm_dispatcher/app.py`)
- Add streaming responses
- Implement conversation history
- Add custom prompts or tools

### 3. Add More Services

The template now supports a **modular service architecture**! See the [Optional Services](#optional-services) section for:
- **PostgreSQL** - Already integrated and ready to enable
- **Add your own** - Easy pattern for Redis, MongoDB, Elasticsearch, etc.

Example services you can add:
- Vector stores (ChromaDB, Pinecone, Weaviate)
- Caching (Redis, Memcached)
- Background workers (Celery with RabbitMQ/Redis)
- Search engines (Elasticsearch, Meilisearch)
- Message queues (RabbitMQ, Kafka)

### 4. Deploy to Production

#### Switch to Production Configuration

Edit `docker-compose.base.yml` and swap the config file in the `client` volumes section:
```yaml
volumes:
  - ./client:/app
  # for development
  #- ./client/.streamlit/config.dev.toml:/app/.streamlit/config.toml
  # for deployment
  - ./client/.streamlit/config.prod.toml:/app/.streamlit/config.toml
```



**Production config changes:**
- XSRF protection enabled
- Error details hidden from users
- Minimal toolbar mode
- Warning-level logging only
- Fast reruns disabled for stability
- 200MB upload limit

Then rebuild:
```bash
launchpad stop
launchpad build-local
launchpad run-local
```

#### Additional Production Steps
- Add authentication/authorization
- Use managed LLM services
- Set up SSL/HTTPS
- Configure environment-specific secrets
- Set up monitoring and logging
- Use production-grade databases

---

## Environment Variables

### Client Container
- `LLM_DISPATCHER` - Hostname of LLM dispatcher (default: `llm-dispatcher`)
- `LLM_DISPATCHER_PORT` - Port of LLM dispatcher (default: `5100`)
- `LLM_PROVIDER` - Current LLM provider (ollama/vllm/openai/anthropic)

### LLM Dispatcher Container
- `LLM_PROVIDER` - Which LLM to use (ollama/vllm/openai/anthropic/mistral)
- `LLM_API_KEY` - API key for external providers
- `LLM_API_ENDPOINT` - API endpoint URL
- `LLM_MODEL` - Model name to use
- `LLM_HOST` - Ollama hostname (for ollama mode)
- `LLM_PORT` - Ollama port (for ollama mode)
- `VLLM_HOST` - vLLM hostname (for vllm mode)
- `VLLM_PORT` - vLLM port (for vllm mode)
- `VLLM_MODEL` - vLLM model name (HuggingFace format)
- `VLLM_GPU_MEMORY_UTILIZATION` - GPU memory to use (0.0-1.0, default 0.85)
- `HUGGING_FACE_HUB_TOKEN` - HuggingFace token (for gated models, store in `.env`)

---

## Contributing

This is a minimal template - feel free to fork and customize for your needs!

If you find bugs or have suggestions, please open an issue.

---

## License

See LICENSE file for details.

---

**Happy building!**
