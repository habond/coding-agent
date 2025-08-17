#!/bin/bash

# Claude CLI Runner Script
# Runs the application in Docker by default for security isolation

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [MESSAGE]"
    echo ""
    echo "OPTIONS:"
    echo "  --local     Run locally using venv instead of Docker"
    echo "  --help      Show this help message"
    echo ""
    echo "EXAMPLES:"
    echo "  $0                    # Interactive mode in Docker"
    echo "  $0 \"Hello Claude\"     # Single message in Docker"
    echo "  $0 --local            # Interactive mode locally"
    echo "  $0 --local \"Hello\"    # Single message locally"
}

# Check for help flag
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_usage
    exit 0
fi

# Check for local flag
if [[ "$1" == "--local" ]]; then
    shift  # Remove --local from arguments

    # Check if venv exists
    if [[ ! -d "$DIR/venv" ]]; then
        echo "Error: Virtual environment not found at $DIR/venv"
        echo "Please create it first with: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        exit 1
    fi

    # Run locally
    echo "Running locally with virtual environment..."
    "$DIR/venv/bin/python" "$DIR/src/main.py" "$@"
else
    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        echo "Error: Docker is not installed or not in PATH"
        echo "Install Docker or use --local flag to run without Docker"
        exit 1
    fi

    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null; then
        echo "Error: docker-compose is not installed or not in PATH"
        echo "Install docker-compose or use --local flag to run without Docker"
        exit 1
    fi

    # Check if .env file exists
    if [[ ! -f "$DIR/.env" ]]; then
        echo "Warning: .env file not found. Creating from template..."
        if [[ -f "$DIR/.env.example" ]]; then
            cp "$DIR/.env.example" "$DIR/.env"
            echo "Please edit .env file with your API key before running again."
            exit 1
        else
            echo "Error: No .env.example template found"
            exit 1
        fi
    fi

    # Run with Docker
    echo "Running in Docker container for security isolation..."
    cd "$DIR"

    if [[ $# -eq 0 ]]; then
        # Interactive mode
        docker-compose run --rm claude-cli
    else
        # Single message mode
        docker-compose run --rm claude-cli python src/main.py "$@"
    fi
fi
