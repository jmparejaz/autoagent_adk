#!/bin/bash
# Docker Entrypoint Script for Enterprise Agentic Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}  Enterprise Agentic Platform${NC}"
echo -e "${GREEN}  Powered by Google ADK${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Configuration from environment variables
COMPANY_NAME="${COMPANY_NAME:-Agent Platform}"
PROJECT_NAME="${PROJECT_NAME:-Enterprise Agentic Platform}"
PRIMARY_COLOR="${PRIMARY_COLOR:-#0066B3}"
SECONDARY_COLOR="${SECONDARY_COLOR:-#1E3A8A}"
ACCENT_COLOR="${ACCENT_COLOR:-#0EA5E9}"
MASCOT_NAME="${MASCOT_NAME:-Marina}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

# Print configuration
echo -e "${BLUE}Configuration:${NC}"
echo "  Company: ${COMPANY_NAME}"
echo "  Project: ${PROJECT_NAME}"
echo "  Primary Color: ${PRIMARY_COLOR}"
echo "  Mascot: ${MASCOT_NAME}"
echo "  Host: ${HOST}"
echo "  Port: ${PORT}"
echo ""

# Check for API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo -e "${RED}Warning: GOOGLE_API_KEY not set.${NC}"
    echo "  The system will use rule-based fallback mode."
else
    echo -e "${GREEN}GOOGLE_API_KEY is configured.${NC}"
fi
echo ""

# Update config.yaml with environment variables
if [ -f "/app/config.yaml" ]; then
    sed -i "s/company_name:.*/company_name: \"${COMPANY_NAME}\"/" /app/config.yaml 2>/dev/null || true
    sed -i "s/project_name:.*/project_name: \"${PROJECT_NAME}\"/" /app/config.yaml 2>/dev/null || true
    sed -i "s/primary_color:.*/primary_color: \"${PRIMARY_COLOR}\"/" /app/config.yaml 2>/dev/null || true
    sed -i "s/secondary_color:.*/secondary_color: \"${SECONDARY_COLOR}\"/" /app/config.yaml 2>/dev/null || true
    sed -i "s/accent_color:.*/accent_color: \"${ACCENT_COLOR}\"/" /app/config.yaml 2>/dev/null || true
    sed -i "s/mascot_name:.*/mascot_name: \"${MASCOT_NAME}\"/" /app/config.yaml 2>/dev/null || true
fi

# Start the server
echo -e "${BLUE}Starting server on http://${HOST}:${PORT}${NC}"
echo ""

cd /app
exec python -m uvicorn backend.main:app --host ${HOST} --port ${PORT}
