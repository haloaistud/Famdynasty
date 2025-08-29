#!/bin/bash

# MyFamilyDynasty Setup Script
# Automates environment setup, dependency installation, and initial configuration
# Usage: bash scripts/setup.sh [--prod] [--no-docker] [--help]

# Exit on errors
set -e

# Default configuration
USE_DOCKER=true
ENV_MODE="dev"
PROJECT_ROOT="$(pwd)"
CONFIG_DIR="$PROJECT_ROOT/config"
LOG_FILE="$PROJECT_ROOT/setup.log"

# Help message
show_help() {
    echo "Usage: $0 [--prod] [--no-docker] [--help]"
    echo "  --prod: Setup for production (skips dev server start)"
    echo "  --no-docker: Use local MongoDB instead of Docker"
    echo "  --help: Show this message"
    exit 0
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --prod)
            ENV_MODE="prod"
            shift
            ;;
        --no-docker)
            USE_DOCKER=false
            shift
            ;;
        --help)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
done

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check for required tools
check_requirements() {
    log "Checking requirements..."

    # Check Python version
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
    if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]; }; then
        log "ERROR: Python 3.8+ required, found $PYTHON_VERSION"
        exit 1
    fi
    log "Python: $PYTHON_VERSION"

    # Check Node.js version
    NODE_VERSION=$(node --version 2>&1 | cut -d. -f1 | tr -d 'v')
    if [ "$NODE_VERSION" -lt 16 ]; then
        log "ERROR: Node.js 16+ required, found $(node --version)"
        exit 1
    fi
    log "Node.js: $(node --version)"

    # Check Docker (if enabled)
    if [ "$USE_DOCKER" = true ]; then
        if ! command -v docker &>/dev/null; then
            log "ERROR: Docker required when --no-docker is not specified"
            exit 1
        fi
        log "Docker: $(docker --version)"
    fi
}

# Create directory structure
create_directories() {
    log "Creating directory structure..."
    if ! mkdir -p ai-services python-services backend frontend scripts config docs; then
        log "ERROR: Failed to create directories (check permissions)"
        exit 1
    fi
    touch config/env.yml docs/addons.txt docs/CODE_OF_CONDUCT.txt docs/CONTRIBUTING.txt
    log "Directory structure created"
}

# Install dependencies
install_dependencies() {
    log "Installing dependencies..."

    # Python dependencies
    if [ -f "requirements.txt" ]; then
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt || {
            log "ERROR: Failed to install Python dependencies"
            exit 1
        }
        deactivate
        log "Python dependencies installed"
    else
        log "Generating default requirements.txt"
        echo -e "fastapi==0.115.0\nuvicorn==0.30.6\npymongo==4.8.0" > requirements.txt
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        deactivate
        log "Default Python dependencies installed"
    fi

    # Node.js dependencies
    if [ -f "package.json" ]; then
        npm install || {
            log "ERROR: Failed to install Node.js dependencies"
            exit 1
        }
        log "Node.js dependencies installed"
    else
        log "Generating default package.json"
        echo '{"scripts":{"test":"echo \"Running tests\"","dev":"nodemon backend/server.js","build":"echo \"Building frontend\""},"dependencies":{"express":"^4.18.2"},"devDependencies":{"nodemon":"^3.0.1"}}' > package.json
        npm install
        log "Default Node.js dependencies installed"
    fi
}

# Initialize configuration
init_config() {
    log "Initializing configuration..."
    if [ -f "$CONFIG_DIR/env.yml" ]; then
        read -p "config/env.yml exists. Overwrite? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "Keeping existing config/env.yml"
            return
        fi
    fi
    cat > "$CONFIG_DIR/env.yml" <<EOL
# MyFamilyDynasty Configuration
environment: $ENV_MODE
database:
  mongo_uri: "mongodb://localhost:27017/myfamilydynasty"
api:
  port: 3000
ai_services:
  huggingface_token: "your_huggingface_token_here"
  openai_token: "your_openai_token_here"
redis:
  host: "localhost"
  port: 6379
EOL
    log "Configuration file created at $CONFIG_DIR/env.yml"
}

# Wait for MongoDB to be ready
wait_for_mongo() {
    local max_attempts=30
    local attempt=1
    log "Waiting for MongoDB to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if [ "$USE_DOCKER" = true ]; then
            docker exec myfamilydynasty-mongo mongosh --eval "db.adminCommand('ping')" &>/dev/null && return 0
        else
            mongosh --eval "db.adminCommand('ping')" &>/dev/null && return 0
        fi
        log "MongoDB not ready, retrying ($attempt/$max_attempts)..."
        sleep 2
        ((attempt++))
    done
    log "ERROR: MongoDB not ready after $max_attempts attempts"
    exit 1
}

# Setup MongoDB
setup_database() {
    log "Setting up MongoDB..."
    if [ "$USE_DOCKER" = true ]; then
        if ! docker ps | grep -q "myfamilydynasty-mongo"; then
            docker run -d --name myfamilydynasty-mongo -p 27017:27017 mongo:latest
            log "MongoDB started via Docker"
        else
            log "MongoDB container already running"
        fi
        wait_for_mongo
    else
        if ! mongod --version &>/dev/null; then
            log "ERROR: MongoDB not installed locally and --no-docker was specified"
            exit 1
        fi
        wait_for_mongo
    fi

    # Seed sample data
    log "Seeding sample data..."
    cat > seed.js <<EOL
use myfamilydynasty;
db.families.insertOne({ name: "Sample Dynasty", created: new Date() });
EOL
    if [ "$USE_DOCKER" = true ]; then
        docker cp seed.js myfamilydynasty-mongo:/seed.js
        docker exec myfamilydynasty-mongo mongosh /seed.js
    else
        mongosh < seed.js
    fi
    rm seed.js
    log "Database seeded"
}

# Build frontend and backend
build_project() {
    log "Building project..."
    if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
        cd frontend
        npm run build || {
            log "ERROR: Failed to build frontend"
            exit 1
        }
        cd ..
        log "Frontend built"
    else
        log "No frontend directory found, skipping build"
    fi
}

# Run tests
run_tests() {
    log "Running tests..."
    local test_failed=false
    if [ -f "package.json" ]; then
        npm test || {
            log "WARNING: Node.js tests failed"
            test_failed=true
        }
        log "Node.js tests completed"
    fi
    if [ -f "requirements.txt" ]; then
        source venv/bin/activate
        pytest python-services || {
            log "WARNING: Python tests failed"
            test_failed=true
            deactivate
        }
        deactivate
        log "Python tests completed"
    fi
    if [ "$ENV_MODE" = "prod" ] && [ "$test_failed" = true ]; then
        log "ERROR: Tests failed in production mode"
        exit 1
    fi
}

# Check port availability
check_port() {
    local port=$1
    if lsof -i :$port &>/dev/null; then
        log "ERROR: Port $port is in use"
        exit 1
    fi
}

# Start development server
start_server() {
    if [ "$ENV_MODE" = "dev" ]; then
        log "Starting development server..."
        check_port 3000
        if [ -f "backend/server.js" ]; then
            npm run dev &
            log "Node.js server started"
        fi
        if [ -f "python-services/main.py" ]; then
            source venv/bin/activate
            uvicorn python-services.main:app --reload &
            deactivate
            log "Python server started"
        fi
    else
        log "Production mode selected, skipping server start (use deploy.sh)"
    fi
}

# Main execution
main() {
    log "Starting MyFamilyDynasty setup (mode: $ENV_MODE, docker: $USE_DOCKER)"
    check_requirements
    create_directories
    install_dependencies
    init_config
    setup_database
    build_project
    run_tests
    start_server
    log "Setup complete! Check $CONFIG_DIR/env.yml for configuration."
    log "Run 'npm start' or 'uvicorn python-services.main:app' for manual server start."
}

main
