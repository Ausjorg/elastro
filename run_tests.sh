#!/bin/bash

# Default test mode
RUN_UNIT=false
RUN_INTEGRATION=false
KEEP_ES_UP=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --unit)
      RUN_UNIT=true
      shift
      ;;
    --integration)
      RUN_INTEGRATION=true
      shift
      ;;
    --all)
      RUN_UNIT=true
      RUN_INTEGRATION=true
      shift
      ;;
    --keep-es-up)
      KEEP_ES_UP=true
      shift
      ;;
    *)
      echo "Unknown option: $key"
      echo "Usage: $0 [--unit] [--integration] [--all] [--keep-es-up]"
      exit 1
      ;;
  esac
done

# If no options specified, default to unit tests
if [[ "$RUN_UNIT" == "false" && "$RUN_INTEGRATION" == "false" ]]; then
  RUN_UNIT=true
fi

# Set up virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -e ".[test]"

# Run unit tests if requested
if [ "$RUN_UNIT" == "true" ]; then
    echo "Running unit tests with coverage..."
    python -m pytest tests/unit/ --cov=elastro --cov-report=term --cov-report=html
fi

# Deactivate virtual environment for integration tests
deactivate

# Run integration tests if requested
if [ "$RUN_INTEGRATION" == "true" ]; then
    echo "Running integration tests..."
    
    # Check if Docker is running
    docker info > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Start Elasticsearch container
    echo "Starting Elasticsearch container..."
    docker compose up -d elasticsearch
    
    # Wait for Elasticsearch to be ready
    echo "Waiting for Elasticsearch to be ready..."
    until $(curl --output /dev/null --silent --head --fail -u elastic:elastic_password http://localhost:9200); do
        printf '.'
        sleep 5
    done
    echo " Elasticsearch is ready!"
    
    # Set environment variables for authentication
    export TEST_ES_USERNAME="elastic"
    export TEST_ES_PASSWORD="elastic_password"
    
    # Generate API key for testing
    echo "Generating API key for testing..."
    API_KEY_RESPONSE=$(curl -s -X POST "http://localhost:9200/_security/api_key" \
      -H "Content-Type: application/json" \
      -u "elastic:elastic_password" \
      -d '{
        "name": "test-api-key",
        "expiration": "1d",
        "role_descriptors": {
          "role1": {
            "cluster": ["all"],
            "indices": [{
              "names": ["*"],
              "privileges": ["all"]
            }]
          }
        }
      }')
    
    # Extract API key
    API_KEY_ID=$(echo $API_KEY_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
    API_KEY_VALUE=$(echo $API_KEY_RESPONSE | grep -o '"api_key":"[^"]*' | cut -d'"' -f4)
    
    if [ -n "$API_KEY_ID" ] && [ -n "$API_KEY_VALUE" ]; then
        export TEST_ES_API_KEY=$(echo -n "$API_KEY_ID:$API_KEY_VALUE" | base64)
        echo "API key generated successfully"
    else
        echo "Failed to generate API key. Some tests may be skipped."
    fi
    
    # Run integration tests directly with system Python
    echo "Running integration tests with system Python..."
    python -m pytest tests/integration/ -m integration -v
    
    # Stop Elasticsearch container by default, unless --keep-es-up flag is set
    if [ "$KEEP_ES_UP" == "true" ]; then
        echo "Keeping Elasticsearch container running as requested."
    else
        echo "Stopping Elasticsearch container..."
        docker compose down
    fi
fi

# Reactivate virtual environment for coverage report
if [ "$RUN_UNIT" == "true" ]; then
    source venv/bin/activate
    
    echo "Coverage report summary:"
    python -m coverage report
    echo "HTML coverage report generated in htmlcov/ directory"
    echo "Run 'open htmlcov/index.html' to view it in your browser"
    
    deactivate
fi 