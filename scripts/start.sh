#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
APP="$PROJECT_DIR/apps/ollama-chat/main.py"
GRADIO_PORT=7860

echo "=== Chatbot Platform Launcher ==="

# 1. System dependencies
echo "[1/6] Checking system dependencies..."
MISSING=()
for CMD in ollama ssh curl; do
  if ! command -v "$CMD" &>/dev/null; then
    MISSING+=("$CMD")
  fi
done
if [ ${#MISSING[@]} -gt 0 ]; then
  echo "  Missing: ${MISSING[*]}"
  echo "  Install: apt-get install ssh curl  &&  (install ollama from https://ollama.ai)"
  exit 1
fi

# 2. Python deps
REQ_FILE="$PROJECT_DIR/apps/ollama-chat/requirements.txt"
if [ -f "$REQ_FILE" ]; then
  echo "[2/6] Checking Python dependencies..."
  pip install -r "$REQ_FILE" -q 2>/dev/null || pip install -r "$REQ_FILE"
fi

# 3. Ollama
if ! pgrep -x ollama > /dev/null; then
  echo "[3/6] Starting Ollama..."
  nohup ollama serve > /tmp/ollama.log 2>&1 &
  sleep 3
  if ! pgrep -x ollama > /dev/null; then
    echo "  ERROR: Ollama failed to start. Check /tmp/ollama.log"
    exit 1
  fi
  echo "  Ollama started"
else
  echo "[3/6] Ollama already running"
fi

# 4. Models
MODELS=("llama3.2:3b" "dolphin-llama3:8b")
echo "[4/6] Checking required models..."
for MODEL in "${MODELS[@]}"; do
  if ! ollama list 2>/dev/null | grep -q "$MODEL"; then
    echo "  Pulling $MODEL (first time — may take a while)..."
    ollama pull "$MODEL"
  else
    echo "  $MODEL already available"
  fi
done

# 5. Gradio
echo "[5/6] Starting Gradio chat on port $GRADIO_PORT..."
pkill -f "main.py" 2>/dev/null || true
sleep 1
nohup python3 "$APP" > /tmp/gradio.log 2>&1 &
GRADIO_PID=$!
echo "  PID: $GRADIO_PID"
for i in $(seq 1 60); do
  if curl -s -o /dev/null -w "" --max-time 2 "http://127.0.0.1:$GRADIO_PORT" 2>/dev/null; then
    echo "  Ready after ${i}s"
    break
  fi
  if [ "$i" -eq 60 ]; then
    echo "  WARNING: Gradio not responding after 60s — check /tmp/gradio.log"
  fi
  sleep 1
done
echo "  Local:    http://localhost:$GRADIO_PORT"

# 6. Tunnel (optional — won't abort if it fails)
echo "[6/6] Starting SSH tunnel via serveo.net..."
"$SCRIPT_DIR/tunnel.sh" start || echo "  Tunnel failed (non-fatal — local access still works)"

echo ""
echo "=== All services running ==="
echo "  Local URL: http://localhost:$GRADIO_PORT"
TUNNEL_URL=$(cat /tmp/tunnel.url 2>/dev/null || echo "(no tunnel)")
echo "  Public:    $TUNNEL_URL"
echo ""
echo "Manage services individually:"
echo "  Gradio: pkill -f main.py && nohup python3 $APP &"
echo "  Tunnel: $SCRIPT_DIR/tunnel.sh start|stop|restart"
echo "  Ollama: ollama serve"
