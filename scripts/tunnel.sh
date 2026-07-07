#!/usr/bin/env bash
TUNNEL_PORT="${TUNNEL_PORT:-7860}"
TUNNEL_HOST="${TUNNEL_HOST:-serveo.net}"
LOG_FILE="/tmp/tunnel.log"
URL_FILE="/tmp/tunnel.url"

start() {
  echo "Starting SSH tunnel → $TUNNEL_HOST (local port $TUNNEL_PORT)..."

  # Accept host key first if needed
  ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "$TUNNEL_HOST" true 2>/dev/null || true

  # Start tunnel with nohup (not autossh — simpler, fewer moving parts)
  nohup ssh -o StrictHostKeyChecking=no \
    -o ExitOnForwardFailure=yes \
    -o ServerAliveInterval=30 \
    -o ServerAliveCountMax=3 \
    -o ConnectTimeout=15 \
    -R 80:localhost:"$TUNNEL_PORT" \
    "$TUNNEL_HOST" \
    > "$LOG_FILE" 2>&1 &
  SSH_PID=$!
  echo "$SSH_PID" > /tmp/tunnel.pid
  echo "  PID: $SSH_PID"
  echo "  Waiting for URL..."

  for i in $(seq 1 120); do
    URL=$(grep -oP 'https?://[^\s]+' "$LOG_FILE" 2>/dev/null | grep -v '\.log$' | grep -v 'console.serveo' | head -1)
    if [ -n "$URL" ]; then
      echo "$URL" > "$URL_FILE"
      echo "  Public URL: $URL"
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
  if [ -f /tmp/tunnel.pid ]; then
    kill "$(cat /tmp/tunnel.pid)" 2>/dev/null || true
    rm -f /tmp/tunnel.pid
  fi
  pkill -f "ssh.*$TUNNEL_HOST" 2>/dev/null || true
  rm -f "$URL_FILE"
  echo "  Stopped"
}

status() {
  if [ -f /tmp/tunnel.pid ] && kill -0 "$(cat /tmp/tunnel.pid)" 2>/dev/null; then
    echo "Tunnel running (PID: $(cat /tmp/tunnel.pid))"
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
