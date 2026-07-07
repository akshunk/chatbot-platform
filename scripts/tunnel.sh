#!/usr/bin/env bash
TUNNEL_PORT="${TUNNEL_PORT:-7860}"
TUNNEL_PORT2="${TUNNEL_PORT2:-8188}"
TUNNEL_HOST="${TUNNEL_HOST:-serveo.net}"
LOG_FILE="/tmp/tunnel.log"
URL_FILE="/tmp/tunnel.url"

start() {
  echo "Starting SSH tunnel → $TUNNEL_HOST (local port $TUNNEL_PORT)..."

  # Accept host key first if needed
  ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "$TUNNEL_HOST" true 2>/dev/null || true

  # Start tunnel in tmux session (persistent, independent of shell)
  tmux kill-session -t tunnel 2>/dev/null || true
  tmux new-session -d -s tunnel \
    "ssh -o StrictHostKeyChecking=no \
      -o ExitOnForwardFailure=yes \
      -o ServerAliveInterval=30 \
      -o ServerAliveCountMax=3 \
      -o ConnectTimeout=15 \
      -R 80:localhost:\"$TUNNEL_PORT\" \
      \"$TUNNEL_HOST\" \
      2>&1 | tee $LOG_FILE"
  sleep 3
  echo "  Waiting for URLs..."

  for i in $(seq 1 120); do
    URLS=$(grep -oP 'https?://[a-zA-Z0-9.-]+(serveousercontent\.com|lhr\.life|serveo\.net|localhost\.run)[^\s]*' "$LOG_FILE" 2>/dev/null | grep -v 'console\.' | head -3)
    if [ -n "$URLS" ]; then
      PRIMARY=$(echo "$URLS" | head -1)
      echo "  Primary URL (chat):  $PRIMARY"
      echo "$PRIMARY" > "$URL_FILE"
      SECONDARY=$(echo "$URLS" | sed -n '2p')
      if [ -n "$SECONDARY" ]; then
        echo "  ComfyUI URL:        $SECONDARY"
        echo "$SECONDARY" > /tmp/tunnel_comfyui.url
      fi
      return 0
    fi
    # Check if process is still alive
    if ! kill -0 "$SSH_PID" 2>/dev/null; then
      echo "  SSH process died — check $LOG_FILE"
      return 1
    fi
    sleep 1
  done
  echo "  Timed out waiting for URL. Check $LOG_FILE"
  return 1
}

stop() {
  echo "Stopping tunnel..."
  tmux kill-session -t tunnel 2>/dev/null || true
  pkill -f "ssh.*$TUNNEL_HOST" 2>/dev/null || true
  rm -f "$URL_FILE"
  echo "  Stopped"
}

status() {
  if tmux has-session -t tunnel 2>/dev/null; then
    echo "Tunnel running"
    if [ -f "$URL_FILE" ]; then
      echo "  URL: $(cat "$URL_FILE")"
    else
      echo "  URL: (waiting...)"
    fi
    return 0
  else
    echo "Tunnel not running"
    return 1
  fi
}

case "${1:-status}" in
  start) start ;;
  stop)  stop ;;
  restart) stop; sleep 1; start ;;
  status|*) status ;;
esac
