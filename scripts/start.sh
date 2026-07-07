#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
APP="$PROJECT_DIR/apps/ollama-chat/main.py"
GRADIO_PORT=7860

echo "=== Chatbot Platform Launcher ==="

# 1. System dependencies
echo "[1/7] Checking system dependencies..."
MISSING=()
for CMD in ollama ssh curl python3; do
  if ! command -v "$CMD" &>/dev/null; then
    MISSING+=("$CMD")
  fi
done
if [ ${#MISSING[@]} -gt 0 ]; then
  echo "  Missing: ${MISSING[*]}"
  echo "  Install: apt-get install ssh curl python3  &&  (install ollama from https://ollama.ai)"
  exit 1
fi

# 2. Python deps
REQ_FILE="$PROJECT_DIR/apps/ollama-chat/requirements.txt"
if [ -f "$REQ_FILE" ]; then
  echo "[2/7] Checking Python dependencies..."
  pip install -r "$REQ_FILE" -q 2>/dev/null || pip install -r "$REQ_FILE"
fi

# 3. Ollama
if ! pgrep -x ollama > /dev/null; then
  echo "[3/7] Starting Ollama..."
  tmux kill-session -t ollama 2>/dev/null || true
  tmux new-session -d -s ollama 'ollama serve'
  sleep 3
  if ! pgrep -x ollama > /dev/null; then
    echo "  ERROR: Ollama failed to start. Check 'tmux attach -t ollama'"
    exit 1
  fi
  echo "  Ollama started"
else
  echo "[3/7] Ollama already running"
fi

# 4. Models
MODELS=("llama3.2:3b" "dolphin-llama3:8b")
echo "[4/7] Checking required models..."
for MODEL in "${MODELS[@]}"; do
  if ! ollama list 2>/dev/null | grep -q "$MODEL"; then
    echo "  Pulling $MODEL (first time — may take a while)..."
    ollama pull "$MODEL"
  else
    echo "  $MODEL already available"
  fi
done

# 5. ComfyUI
COMFYUI_DIR="/workspace/ComfyUI"
COMFYUI_MODEL="$COMFYUI_DIR/models/checkpoints/ponyDiffusionV6XL_v6StartWithThisOne.safetensors"
COMFYUI_VENV_PYTHON="$COMFYUI_DIR/.venv/bin/python3"
echo "[5/7] Starting ComfyUI..."
if [ ! -f "$COMFYUI_MODEL" ]; then
  echo "  WARNING: Pony Diffusion XL model not found at:"
  echo "    $COMFYUI_MODEL"
  echo "  Image generation won't work until the model is downloaded."
fi
COMFYUI_PYTHON="$COMFYUI_VENV_PYTHON"
if [ ! -f "$COMFYUI_PYTHON" ]; then
  COMFYUI_PYTHON="python3"
fi
if ! tmux has-session -t comfyui 2>/dev/null; then
  echo "  Starting..."
  tmux kill-session -t comfyui 2>/dev/null || true
  tmux new-session -d -s comfyui -c "$COMFYUI_DIR" "$COMFYUI_PYTHON main.py --listen --port 8188"
  for i in $(seq 1 150); do
    if curl -s -o /dev/null -w "" --max-time 2 "http://127.0.0.1:8188" 2>/dev/null; then
      echo "  Ready after ${i}s"
      break
    fi
    if [ "$i" -eq 150 ]; then
      echo "  WARNING: ComfyUI not responding after 150s — check 'tmux attach -t comfyui'"
    fi
    sleep 1
  done
else
  echo "  Already running"
fi

# 6. Gradio
echo "[6/7] Starting Gradio chat on port $GRADIO_PORT..."
tmux kill-session -t gradio 2>/dev/null || true
tmux new-session -d -s gradio -c "$PROJECT_DIR" "python3 $APP"
for i in $(seq 1 60); do
  if curl -s -o /dev/null -w "" --max-time 2 "http://127.0.0.1:$GRADIO_PORT" 2>/dev/null; then
    echo "  Ready after ${i}s"
    break
  fi
  if [ "$i" -eq 60 ]; then
    echo "  WARNING: Gradio not responding after 60s — check 'tmux attach -t gradio'"
  fi
  sleep 1
done
echo "  Local:    http://localhost:$GRADIO_PORT"

# 7. Tunnel (optional — won't abort if it fails)
echo "[7/7] Starting SSH tunnel via serveo.net..."
"$SCRIPT_DIR/tunnel.sh" start || echo "  Tunnel failed (non-fatal — local access still works)"

echo ""
echo "=== All services running ==="
echo "  Chat UI:  http://localhost:$GRADIO_PORT"
echo "  ComfyUI:  http://localhost:8188"
TUNNEL_URL=$(cat /tmp/tunnel.url 2>/dev/null || echo "(no tunnel)")
echo "  Public:   $TUNNEL_URL"
echo ""
echo "Manage services (tmux sessions):"
echo "  Gradio:  tmux kill-session -t gradio; tmux new-session -d -s gradio -c $PROJECT_DIR 'python3 $APP'"
echo "  ComfyUI: tmux kill-session -t comfyui; tmux new-session -d -s comfyui -c $COMFYUI_DIR '$COMFYUI_PYTHON main.py --listen --port 8188'"
echo "  Tunnel:  $SCRIPT_DIR/tunnel.sh start|stop|restart"
echo "  Ollama:  tmux kill-session -t ollama; tmux new-session -d -s ollama 'ollama serve'"
echo "  Attach:  tmux attach -t <name>"
