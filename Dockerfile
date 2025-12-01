# Utah Tourism AI Application
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

# Install uv for fast dependency management
RUN pip install uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy \
    uv pip install --system .

# Copy application code
COPY src/ ./src/
COPY static/ ./static/
COPY templates/ ./templates/

# Compile Python files
RUN python -m compileall -q .

# Create entrypoint script
COPY <<'EOF' /entrypoint.sh
#!/bin/sh
set -e

echo "Starting Utah Tourism AI Application..."
echo "LLM API URL: ${LLM_API_URL}"
echo "LLM Model: ${LLM_MODEL_NAME}"
echo "MCP Gateway: ${MCP_GATEWAY_ENDPOINT}"

# Set OpenAI-compatible environment variables for the LLM
export OPENAI_BASE_URL="${LLM_API_URL}"
export OPENAI_MODEL_NAME="${LLM_MODEL_NAME}"
export OPENAI_API_KEY="local-model-runner"

exec python -m uvicorn src.main:app --host 0.0.0.0 --port 8080
EOF

RUN chmod +x /entrypoint.sh

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app

USER app

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]
