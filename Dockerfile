# syntax=docker/dockerfile:1.5
# STAGE 1: Builder
FROM python:3.11.0-slim AS builder
 
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_HOME=/app
 
WORKDIR $APP_HOME
 
# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
 
# Upgrade pip and create a Virtual Environment
RUN python -m pip install --upgrade pip setuptools wheel
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
 
# Copy requirements and install dependencies
COPY requirements.txt .
 
# Use Secret to install private dependencies
RUN --mount=type=secret,id=github_pat \
    export GITHUB_TOKEN=$(cat /run/secrets/github_pat) && \
    git config --global url."https://${GITHUB_TOKEN}:x-oauth-basic@github.com/".insteadOf "https://github.com/" && \
    pip install --no-cache-dir -r requirements.txt
 
# STAGE 2: Final Runtime
FROM python:3.11.0-slim
 
ARG ENVIRONMENT=dev
ARG WEB_SERVER_PORT=9000
 
# Set environment variables
ENV ENVIRONMENT=${ENVIRONMENT} \
    WEB_SERVER_PORT=${WEB_SERVER_PORT} \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE="core.settings.${ENVIRONMENT}"
 
# Install only runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libreoffice \
    wkhtmltopdf \
    libxrender1 \
    libxext6 \
    libfontconfig1 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libharfbuzz0b \
    libfribidi0 \
    openssh-client \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*
 
# Create a non-privileged user
RUN addgroup --system app && adduser --system --ingroup app app
WORKDIR $APP_HOME
 
# Copy the virtual environment from builder
COPY --from=builder --chown=app:app /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
 
# Copy code with ownership assigned immediately
# This avoids the slow `chown -R` on the whole directory later
COPY --chown=app:app . .
 
# Entrypoint setup
COPY --chown=app:app docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
 
RUN chown -R app:app /app && chmod -R 755 /app
 
USER app
EXPOSE $WEB_SERVER_PORT
 
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["web"]
 