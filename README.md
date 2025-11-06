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
- **ollama-llm** - Local LLM runtime (only for local mode)

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
       ├──────────┐
       ▼          ▼
  ┌────────┐  ┌──────────┐
  │ Ollama │  │ External │
  │ (Local)│  │LLM (API) │
  └────────┘  └──────────┘
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
# Check if model is downloading
launchpad logs llm
```

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
├── ollama/                   # Local LLM configuration
│   └── Dockerfile           # Ollama container config
├── env_templates/           # Environment file templates
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
- Database (PostgreSQL, MongoDB)
- Vector store (ChromaDB, Pinecone)
- Background workers (Celery)

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
- `LLM_PROVIDER` - Current LLM provider (local/openai/anthropic)

### LLM Dispatcher Container
- `LLM_PROVIDER` - Which LLM to use (local/openai/anthropic/mistral)
- `LLM_API_KEY` - API key for external providers
- `LLM_API_ENDPOINT` - API endpoint URL
- `LLM_MODEL` - Model name to use
- `LLM_HOST` - Ollama hostname (for local mode)
- `LLM_PORT` - Ollama port (for local mode)

---

## Contributing

This is a minimal template - feel free to fork and customize for your needs!

If you find bugs or have suggestions, please open an issue.

---

## License

See LICENSE file for details.

---

**Happy building!**
