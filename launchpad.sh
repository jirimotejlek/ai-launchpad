#!/bin/bash
# Docker Compose management script

# Get current directory name as project name
PROJECT_NAME=$(basename "$PWD" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g')

BASE_FILES="-f docker-compose.base.yml"
LOCAL_FILES="$BASE_FILES -f docker-compose.local.yml"
EXTERNAL_FILES="$BASE_FILES -f docker-compose.external.yml"
COMPOSE_ARGS="-p $PROJECT_NAME"

# Read local LLM backend from config file
LOCAL_LLM_BACKEND="ollama"
if [ -f local-llm.config ]; then
    LOCAL_LLM_BACKEND=$(grep -v '^#' local-llm.config | grep 'LOCAL_LLM_BACKEND' | cut -d'=' -f2 | tr -d ' ')
    if [ -z "$LOCAL_LLM_BACKEND" ]; then
        LOCAL_LLM_BACKEND="ollama"
    fi
fi

# Read optional services from services.config
SERVICE_FILES=""
if [ -f services.config ]; then
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        if [[ ! "$key" =~ ^#.* ]] && [ -n "$key" ]; then
            # Trim whitespace
            key=$(echo "$key" | tr -d ' ')
            value=$(echo "$value" | tr -d ' ')
            
            # Check if service is enabled (true)
            if [ "$value" = "true" ]; then
                # Extract service name from ENABLE_SERVICENAME
                service_name="${key#ENABLE_}"
                # Convert to lowercase
                service_name=$(echo "$service_name" | tr '[:upper:]' '[:lower:]')
                # Add service compose file
                SERVICE_FILES="$SERVICE_FILES -f docker-compose.${service_name}.yml"
            fi
        fi
    done < services.config
fi

# Append service files to compose file lists
LOCAL_FILES="$LOCAL_FILES$SERVICE_FILES"
EXTERNAL_FILES="$EXTERNAL_FILES$SERVICE_FILES"

show_help() {
    echo "Usage: ./launchpad.sh [command]"
    echo ""
    echo "Commands:"
    echo "  run-local      Start services with local LLM (backend: $LOCAL_LLM_BACKEND)"
    echo "  run-external   Start services with external LLM provider"
    echo "  build-local    Build containers for local LLM"
    echo "  build-external Build containers for external LLM"
    echo "  stop           Stop services (containers remain)"
    echo "  restart        Restart stopped services"
    echo "  status         Show status of project containers"
    echo "  logs           Show logs from running services"
    echo "  remove         Remove all project containers and volumes"
    echo "  help           Show this help message"
    echo ""
    echo "Local LLM Backend:"
    echo "  Current: $LOCAL_LLM_BACKEND"
    echo "  Configure: Edit local-llm.config (options: ollama, vllm)"
    echo ""
    echo "Optional Services:"
    echo "  Configure: Edit services.config to enable/disable services"
    echo "  Example: ENABLE_POSTGRES=true"
    echo ""
    echo "Examples:"
    echo "  ./launchpad.sh run-local"
    echo "  ./launchpad.sh run-local -d     # Run in detached mode"
    echo "  ./launchpad.sh stop             # Stop but keep containers"
    echo "  ./launchpad.sh restart          # Restart stopped containers"
    echo "  ./launchpad.sh logs llm-dispatcher"
}

check_env_file() {
    if [ ! -f .env ]; then
        echo "Error: .env file not found!"
        echo ""
        echo "To use an external LLM provider:"
        echo "1. Copy a template: cp env-templates/openai .env"
        echo "2. Edit .env and add your API key"
        echo "3. Run this script again"
        exit 1
    fi
}

case "$1" in
    run-local)
        echo "Starting services with local LLM ($LOCAL_LLM_BACKEND)..."
        echo ""
        echo ""
        echo "==============================================="
        echo "==============================================="
        echo ""
        echo "     🚀 AI LAUNCHPAD STARTING"
        echo "     Backend: $LOCAL_LLM_BACKEND"
        echo ""
        echo "     📱 Once ready, open:"
        echo "     http://localhost:8501"
        echo ""
        echo "==============================================="
        echo "==============================================="
        echo ""
        echo ""
        shift
        export COMPOSE_PROFILES="$LOCAL_LLM_BACKEND"
        docker compose $COMPOSE_ARGS --profile "$LOCAL_LLM_BACKEND" $LOCAL_FILES up "$@"
        ;;
    run-external)
        check_env_file
        echo "Starting services with external LLM provider..."
        echo ""
        echo ""
        echo "==============================================="
        echo "==============================================="
        echo ""
        echo "     🚀 AI LAUNCHPAD STARTING"
        echo ""
        echo "     📱 Once ready, open:"
        echo "     http://localhost:8501"
        echo ""
        echo "==============================================="
        echo "==============================================="
        echo ""
        echo ""
        shift
        docker compose $COMPOSE_ARGS $EXTERNAL_FILES up "$@"
        ;;
    build-local)
        echo "Building services with local LLM ($LOCAL_LLM_BACKEND)..."
        shift
        export COMPOSE_PROFILES="$LOCAL_LLM_BACKEND"
        docker compose $COMPOSE_ARGS --profile "$LOCAL_LLM_BACKEND" $LOCAL_FILES build "$@"
        ;;
    build-external)
        echo "Building services for external LLM provider..."
        shift
        docker compose $COMPOSE_ARGS $EXTERNAL_FILES build "$@"
        ;;
    stop)
        echo "Stopping services..."
        shift
        # Just stop containers, don't remove them
        docker compose $COMPOSE_ARGS $LOCAL_FILES stop "$@" 2>/dev/null || docker compose $COMPOSE_ARGS $EXTERNAL_FILES stop "$@" 2>/dev/null
        ;;
    restart)
        echo "Restarting services..."
        shift
        # Restart whichever configuration is currently stopped
        docker compose $COMPOSE_ARGS $LOCAL_FILES restart "$@" 2>/dev/null || docker compose $COMPOSE_ARGS $EXTERNAL_FILES restart "$@" 2>/dev/null
        ;;
    status)
        echo "Project containers status:"
        # Try both configurations to show all project containers
        docker compose $COMPOSE_ARGS $LOCAL_FILES ps 2>/dev/null || docker compose $COMPOSE_ARGS $EXTERNAL_FILES ps 2>/dev/null || echo "No active compose configuration found"
        ;;
    logs)
        shift
        # Check which compose files have running containers
        if docker compose $COMPOSE_ARGS $LOCAL_FILES ps -q 2>/dev/null | grep -q .; then
            docker compose $COMPOSE_ARGS $LOCAL_FILES logs -f "$@"
        elif docker compose $COMPOSE_ARGS $EXTERNAL_FILES ps -q 2>/dev/null | grep -q .; then
            docker compose $COMPOSE_ARGS $EXTERNAL_FILES logs -f "$@"
        else
            echo "No running services found"
        fi
        ;;
    remove)
        echo "WARNING: This will remove all containers and volumes for this project!"
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            shift
            echo "Detecting project containers..."
            
            # First try graceful shutdown with compose
            echo "Stopping services..."
            docker compose $COMPOSE_ARGS $LOCAL_FILES down --remove-orphans 2>/dev/null || true
            LLM_API_KEY=dummy LLM_API_ENDPOINT=dummy LLM_PROVIDER=dummy docker compose $COMPOSE_ARGS $EXTERNAL_FILES down --remove-orphans 2>/dev/null || true
            
            # List and remove only containers from this project
            echo "Removing project containers..."
            docker ps -a --filter "label=com.docker.compose.project=${PROJECT_NAME}" --format "{{.ID}}" | xargs -r docker rm -f 2>/dev/null || true
            
            # Remove only volumes from this project
            echo "Removing project volumes..."
            docker volume ls --filter "label=com.docker.compose.project=${PROJECT_NAME}" -q | xargs -r docker volume rm -f 2>/dev/null || true
            
            # Also try with explicit volume names from this project
            docker volume rm -f "${PROJECT_NAME}_chroma_data" "${PROJECT_NAME}_ollama_data" 2>/dev/null || true
            
            echo "Project containers and volumes removed"
        else
            echo "Cancelled"
        fi
        ;;
    help|"")
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac