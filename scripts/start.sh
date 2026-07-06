#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
APP="$PROJECT_DIR/apps/ollama-chat/main.py"
GRADIO_PORT=7860
TUNNEL_SERVICE="serveo.net"

cleanup() {
  echo ""
  echo "Shutting down..."
  pkill -f "main.py" 2>/dev/null || true
  "$SCRIPT_DIR/tunnel.sh" stop 2>/dev/null || true
  echo "Done."
}
trap cleanup EXIT

echo "=== Chatbot Platform Launcher ==="
echo ""

# 1. Python deps
REQ_FILE="$PROJECT_DIR/apps/ollama-chat/requirements.txt"
if [ -f "$REQ_FILE" ]; then
  echo "[1/5] Checking Python dependencies..."
  pip install -r "$REQ_FILE" -q 2>/dev/null || pip install -r "$REQ_FILE"
fi

# 2. Ollama
if ! pgrep -x ollama > /dev/null; then
  echo "[2/5] Starting Ollama..."
  ollama serve > /tmp/ollama.log 2>&1 &
  sleep 2
else
  echo "[2/5] Ollama already running"
fi

# 3. Models
MODELS=("llama3.2:3b" "dolphin-llama3:8b")
echo "[2/5] Checking required models..."
for MODEL in "${MODELS[@]}"; do
  if ! ollama list 2>/dev/null | grep -q "$MODEL"; then
    echo "  Pulling $MODEL (first time — may take a while)..."
    ollama pull "$MODEL"
  else
    echo "  $MODEL already available"
  fi
done

# 4. Gradio
echo "[3/5] Starting Gradio chat on port $GRADIO_PORT..."
pkill -f "main.py" 2>/dev/null || true
sleep 1
python3 "$APP" > /tmp/gradio.log 2>&1 &
GRADIO_PID=$!
for i in $(seq 1 10); do
  if curl -s -o /dev/null -w "" --max-time 2 "http://127.0.0.1:$GRADIO_PORT" 2>/dev/null; then
    break
  fi
  sleep 1
done
echo "  Local:    http://localhost:$GRADIO_PORT"

# 5. Tunnel
echo "[4/5] Starting SSH tunnel via $TUNNEL_SERVICE..."
"$SCRIPT_DIR/tunnel.sh" start

echo ""
echo "=== All services running ==="
echo "  Local URL: http://localhost:$GRADIO_PORT"
TUNNEL_URL=$(cat /tmp/tunnel.url 2>/dev/null || echo "(waiting...)")
echo "  Public:    $TUNNEL_URL"
echo ""
echo "Press Ctrl+C to stop all services."

wait
