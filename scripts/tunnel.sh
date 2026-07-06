#!/usr/bin/env bash
set -euo pipefail

TUNNEL_PORT="${TUNNEL_PORT:-7860}"
TUNNEL_HOST="${TUNNEL_HOST:-serveo.net}"
LOG_FILE="/tmp/tunnel.log"
URL_FILE="/tmp/tunnel.url"

start() {
  echo "Starting autossh tunnel → $TUNNEL_HOST (local port $TUNNEL_PORT)..."
  autossh -M 0 \
    -o "ExitOnForwardFailure=yes" \
    -o "ServerAliveInterval=30" \
    -o "ServerAliveCountMax=3" \
    -o "StrictHostKeyChecking=no" \
    -R 80:localhost:"$TUNNEL_PORT" \
    "$TUNNEL_HOST" \
    > "$LOG_FILE" 2>&1 &
  AUTOSSH_PID=$!
  echo "$AUTOSSH_PID" > /tmp/tunnel.pid
  echo "  autossh pid: $AUTOSSH_PID"
  echo "  Waiting for URL..."
  for i in $(seq 1 60); do
    URL=$(grep -oP 'https?://[^\s]+' "$LOG_FILE" 2>/dev/null | grep -v '\.log$' | head -1)
    if [ -n "$URL" ]; then
      echo "$URL" > "$URL_FILE"
      echo "  Public URL: $URL"
      return 0
    fi
    sleep 1
  done
  echo "  Timed out — check $LOG_FILE for details"
  return 1
}

stop() {
  echo "Stopping tunnel..."
  if [ -f /tmp/tunnel.pid ]; then
    kill "$(cat /tmp/tunnel.pid)" 2>/dev/null || true
    rm -f /tmp/tunnel.pid
  fi
  pkill -f "autossh.*$TUNNEL_HOST" 2>/dev/null || true
  rm -f "$URL_FILE"
  echo "  Stopped"
}

status() {
  if [ -f /tmp/tunnel.pid ] && kill -0 "$(cat /tmp/tunnel.pid)" 2>/dev/null; then
    echo "Tunnel running (pid: $(cat /tmp/tunnel.pid))"
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
