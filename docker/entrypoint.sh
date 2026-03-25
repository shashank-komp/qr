#!/bin/bash
set -e
 
# Configuration with defaults
SERVICE=${1:-web}
WORKERS=${GUNICORN_WORKERS:-2}
CELERY_CONCURRENCY=${CELERY_CONCURRENCY:-1}
LOG_LEVEL=${LOG_LEVEL:-info}
MAX_RETRIES=${MAX_RETRIES:-30}
RETRY_INTERVAL=${RETRY_INTERVAL:-2}
MODULE_NAME=${MODULE_NAME:-core}
 
echo "========================================"
echo "Service: $SERVICE"
echo "Environment: ${DJANGO_SETTINGS_MODULE}"
echo "========================================"
 
# Function: Wait for a service to be ready
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local retries=0
   
    # Validate parameters
    if [ -z "$host" ] || [ -z "$port" ] || [ -z "$service_name" ]; then
        echo "ERROR: wait_for_service requires host, port, and service_name"
        return 1
    fi
   
    # Use defaults for global variables if not set
    local max_retries=${MAX_RETRIES:-30}
    local retry_interval=${RETRY_INTERVAL:-2}
 
    echo "Waiting for $service_name at $host:$port..."
   
    # Check if we have the necessary tools
    local has_nc=false
    local has_timeout=false
    command -v nc >/dev/null 2>&1 && has_nc=true
    command -v timeout >/dev/null 2>&1 && has_timeout=true
   
    if [ "$has_nc" = false ] && [ "$has_timeout" = false ]; then
        echo "ERROR: Neither 'nc' nor 'timeout' command is available"
        return 1
    fi
   
    while [ $retries -lt $max_retries ]; do
        # Try with available tools
        if [ "$has_nc" = true ]; then
            if nc -z "$host" "$port" 2>/dev/null; then
                echo "$service_name is ready!"
                return 0
            fi
        elif [ "$has_timeout" = true ]; then
            if timeout 1 bash -c "cat < /dev/null > /dev/tcp/$host/$port" 2>/dev/null; then
                echo "$service_name is ready!"
                return 0
            fi
        fi
       
        retries=$((retries + 1))
        echo "Waiting for $service_name... (attempt $retries/$max_retries)"
        sleep $retry_interval
    done
   
    echo "ERROR: $service_name at $host:$port is not available after $max_retries attempts"
    return 1  # Return error code instead of exit
}
 
# Function: Parse DATABASE_URL and wait for PostgreSQL
wait_for_postgres() {
    # Prefer explicit DB_HOST/DB_PORT if set
    if [ -n "$DB_HOST" ]; then
        wait_for_service "${DB_HOST}" "${DB_PORT:-5432}" "PostgreSQL"
    elif [ -n "$DATABASE_URL" ]; then
        # Fallback to parsing DATABASE_URL
        DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
        DB_PORT=$(echo "$DATABASE_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
       
        if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
            wait_for_service "$DB_HOST" "$DB_PORT" "PostgreSQL"
        fi
    fi
}
 
# Function: Parse CELERY_BROKER_URL and wait for Redis
wait_for_redis() {
    if [ -n "$CELERY_BROKER_URL" ]; then
        # Extract host and port from redis://host:port/db
        REDIS_HOST=$(echo "$CELERY_BROKER_URL" | sed -n 's|redis://\([^:]*\):.*|\1|p')
        REDIS_PORT=$(echo "$CELERY_BROKER_URL" | sed -n 's|redis://[^:]*:\([0-9]*\).*|\1|p')
       
        if [ -n "$REDIS_HOST" ] && [ -n "$REDIS_PORT" ]; then
            wait_for_service "$REDIS_HOST" "$REDIS_PORT" "Redis"
        fi
    elif [ -n "$REDIS_HOST" ]; then
        wait_for_service "${REDIS_HOST}" "${REDIS_PORT:-6379}" "Redis"
    fi
}
 
# Function: Run Django migrations
run_migrations() {
    echo "Running database migrations..."
    python manage.py migrate --noinput || {
        echo "ERROR: Database migration failed"
        exit 1
    }
    echo "Migrations completed successfully"
}
 
# Function: Check for multiple beat instances
check_beat_lock() {
    if [ -f /tmp/celerybeat.pid ]; then
        echo "WARNING: Found existing celerybeat.pid file"
        echo "Removing stale PID file..."
        rm -f /tmp/celerybeat.pid
    fi
}
 
# Service-specific startup logic
case "$SERVICE" in
  web)
    echo "=== Starting Gunicorn Web Server ==="
   
    # Wait for dependencies
    wait_for_postgres
   
    # Run migrations (only for web service to avoid race conditions)
    if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
        run_migrations
    fi
   
    echo "Starting Gunicorn with $WORKERS workers..."
    exec gunicorn ${MODULE_NAME}.asgi:application \
        --workers "$WORKERS" \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind "0.0.0.0:${WEB_SERVER_PORT:-8011}" \
        --timeout "${GUNICORN_TIMEOUT:-120}" \
        --access-logfile - \
        --error-logfile - \
        --log-level "$LOG_LEVEL" \
        --worker-tmp-dir /dev/shm \
        --forwarded-allow-ips='*' \
        --access-logformat '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
    ;;
   
    celery-worker)
    echo "=== Starting Celery Worker ==="
   
    # Wait for dependencies
    wait_for_postgres
    wait_for_redis
   
    # Get hostname for worker naming
    HOSTNAME=${HOSTNAME:-$(hostname)}
    # Don't use CELERY_WORKER_NAME from env to avoid collisions with replicas
    WORKER_NAME="worker@$HOSTNAME"
 
    echo "Starting Celery worker: $WORKER_NAME"
    echo "Concurrency: $CELERY_CONCURRENCY"
    echo "Pool: ${CELERY_POOL:-solo}"
 
    exec celery -A $MODULE_NAME worker --loglevel=$LOG_LEVEL
    ;;
       
    celery-beat)
    echo "=== Starting Celery Beat Scheduler ==="
   
    # Wait for dependencies
    wait_for_redis
   
    # Ensure only one beat instance
    check_beat_lock
   
    # Warning if scaling is detected
    if [ -n "$CELERY_BEAT_REPLICA_WARNING" ]; then
        echo "⚠️  WARNING: Celery Beat should NEVER be scaled beyond 1 replica!"
        echo "⚠️  Multiple beat instances will cause duplicate task execution!"
    fi
   
    echo "Starting Celery beat scheduler..."
    exec celery -A $MODULE_NAME beat --loglevel=$LOG_LEVEL
    ;;
 
  celery-flower)
    echo "=== Starting Celery Flower Monitoring ==="
   
    # Wait for Redis
    wait_for_redis
   
    echo "Starting Celery Flower on port ${FLOWER_PORT:-5555}..."
    exec celery -A $MODULE_NAME flower --port="${FLOWER_PORT:-5555}" --address=0.0.0.0 --loglevel=$LOG_LEVEL
    ;;
 
  migrate)
    echo "=== Running Migrations Only ==="
    wait_for_postgres
    run_migrations
    echo "Migration complete. Exiting."
    exit 0
    ;;
 
  shell)
    echo "=== Starting Django Shell ==="
    wait_for_postgres
    exec python manage.py shell
    ;;
 
  *)
    echo "❌ Unknown service: $SERVICE"
    echo ""
    echo "Available services:"
    echo "  web            - Gunicorn web server"
    echo "  celery-worker  - Celery async worker"
    echo "  celery-beat    - Celery periodic scheduler"
    echo "  celery-flower  - Celery monitoring UI"
    echo "  migrate        - Run migrations and exit"
    echo "  shell          - Django shell"
    echo ""
    exit 1
    ;;
esac