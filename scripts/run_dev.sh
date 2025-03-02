#!/bin/bash
# Development server script for the multiagent system

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Please run scripts/setup.sh first."
    exit 1
fi

# Set development environment variables
export ENVIRONMENT="development"
export DEBUG="true"
export LOG_LEVEL="DEBUG"

# Check if the database needs to be initialized
if [ ! -d "data/chroma" ] || [ -z "$(ls -A data/chroma)" ]; then
    echo "Vector database appears to be empty. Would you like to initialize it with sample data? (y/n)"
    read -r init_db
    if [[ $init_db == "y" || $init_db == "Y" ]]; then
        python -m src.rag.init_db
    fi
fi

# Check for optional arguments
HOST="0.0.0.0"
PORT="8000"
RELOAD="--reload"

while [[ $# -gt 0 ]]; do
    case $1 in
        --host=*)
            HOST="${1#*=}"
            shift
            ;;
        --port=*)
            PORT="${1#*=}"
            shift
            ;;
        --no-reload)
            RELOAD=""
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run the development server
echo "Starting development server at http://$HOST:$PORT"
echo "Press Ctrl+C to stop the server"
python -m uvicorn src.main:app --host=$HOST --port=$PORT $RELOAD 