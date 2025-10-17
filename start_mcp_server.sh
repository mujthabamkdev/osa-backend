#!/bin/bash
# OSA MCP Server Startup Script

echo "Starting OSA MCP Server..."
echo "Make sure your OSA backend is running on http://localhost:8001"
echo ""

# Set default environment variables
export OSA_BASE_URL="${OSA_BASE_URL:-http://localhost:8001}"
export OSA_API_KEY="${OSA_API_KEY:-}"

echo "Configuration:"
echo "  OSA_BASE_URL: $OSA_BASE_URL"
echo "  OSA_API_KEY: ${OSA_API_KEY:+'***SET***'}"
echo ""

# Check if backend is running
echo "Checking backend connectivity..."
if curl -s -f "$OSA_BASE_URL/health" > /dev/null 2>&1; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is not responding at $OSA_BASE_URL"
    echo "Please start your OSA backend first:"
    echo "  cd ../osa-backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001"
    exit 1
fi

echo ""
echo "Starting MCP Server..."
echo "Press Ctrl+C to stop"
echo ""

# Run the MCP server
cd "$(dirname "$0")"
/Users/mujthabamk/Desktop/real-world-projects/osa/OSA/osa-backend/venv/bin/python osa_mcp_server.py