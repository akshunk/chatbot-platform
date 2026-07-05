#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Resetting development data..."
rm -rf "$PROJECT_DIR/data/conversations/"*
rm -rf "$PROJECT_DIR/data/feedback/"*
rm -rf "$PROJECT_DIR/data/logs/"*
rm -rf "$PROJECT_DIR/data/cache/"*
rm -rf "$PROJECT_DIR/knowledge/processed/"*
rm -rf "$PROJECT_DIR/knowledge/embeddings/"*
rm -rf "$PROJECT_DIR/knowledge/collections/"*

echo "Done. All dev data has been reset."
