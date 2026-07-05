#!/usr/bin/env bash
set -e

TUNNEL_PORT=3000
TUNNEL_SESSION="tunnel"
LOG_FILE="/tmp/tunnel.log"

start() {
  echo "Starting autossh tunnel on port $TUNNEL_PORT..."
  autossh -M 0 \
    -o "ExitOnForwardFailure=yes" \
    -o "ServerAliveInterval=30" \
    -o "ServerAliveCountMax=3" \
    -o "StrictHostKeyChecking=no" \
    -R 80:localhost:$TUNNEL_PORT \
    nokey@localhost.run \
    > "$LOG_FILE" 2>&1 &
  AUTOSSH_PID=$!
  echo "$AUTOSSH_PID" > /tmp/tunnel.pid
  echo "autossh pid: $AUTOSSH_PID"
  echo "Waiting for URL..."
  for i in $(seq 1 30); do
    URL=$(grep -oP 'https?://[^\s]+lhr\.\w+' "$LOG_FILE" 2>/dev/null | head -1)
    if [ -n "$URL" ]; then
      echo "Tunnel URL: $URL"
      return 0
    fi
    sleep 1
  done
  echo "Timed out waiting for tunnel URL"
  return 1
}

stop() {
  echo "Stopping tunnel..."
  if [ -f /tmp/tunnel.pid ]; then
    kill "$(cat /tmp/tunnel.pid)" 2>/dev/null || true
    rm -f /tmp/tunnel.pid
  fi
  pkill -f "autossh.*localhost.run" 2>/dev/null || true
  echo "Stopped"
}

status() {
  if [ -f /tmp/tunnel.pid ] && kill -0 "$(cat /tmp/tunnel.pid)" 2>/dev/null; then
    echo "Tunnel running (pid: $(cat /tmp/tunnel.pid))"
    URL=$(grep -oP 'https?://[^\s]+lhr\.\w+' "$LOG_FILE" 2>/dev/null | head -1)
    [ -n "$URL" ] && echo "URL: $URL" || echo "URL: (waiting...)"
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
