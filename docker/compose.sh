#!/bin/bash
 
PROJECT_NAME=${1:-eor_temp_emp_default}
 
# Function to find the next available port
get_free_port() {
    local port=$1
    # Keep incrementing if the port appears in the "Numeric Listen" list
    while ss -tuln | grep -q ":$port "; do
        port=$((port + 1))
    done
    echo "$port"
}
 
# Define your starting base ports
BASE_DB=5435
BASE_REDIS=6379
BASE_WEB=9000
BASE_FLOWER=5555
 
# Find free ports
export DB_PORT=$(get_free_port $BASE_DB)
export REDIS_PORT=$(get_free_port $BASE_REDIS)
export WEB_PORT=$(get_free_port $BASE_WEB)
export FLOWER_PORT=$(get_free_port $BASE_FLOWER)
 
echo "🛠  Starting project: $PROJECT_NAME"
echo "📡 Web: http://localhost:$WEB_PORT | DB: $DB_PORT"
 
docker compose -p "$PROJECT_NAME" up -d