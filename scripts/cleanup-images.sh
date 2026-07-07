#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="/workspace/ComfyUI/output"
KEEP=50
MAX_AGE_HOURS=48
DRY_RUN=false

while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run) DRY_RUN=true; shift ;;
        --keep) KEEP="$2"; shift 2 ;;
        --max-age) MAX_AGE_HOURS="$2"; shift 2 ;;
        --help|-h)
            echo "Usage: $0 [--keep N] [--max-age HOURS] [--dry-run]"
            echo "  --keep N       Keep N newest images (default: 50)"
            echo "  --max-age H    Delete images older than H hours (default: 48)"
            echo "  --dry-run      Show what would be deleted without deleting"
            exit 0
            ;;
        *) echo "Unknown: $1"; exit 1 ;;
    esac
done

[ -d "$OUTPUT_DIR" ] || { echo "Not found: $OUTPUT_DIR"; exit 1; }

BEFORE=$(find "$OUTPUT_DIR" -name '*.png' -type f | wc -l)
echo "Before: $BEFORE images (limit $KEEP, max age ${MAX_AGE_HOURS}h)"
$DRY_RUN && echo "--- DRY RUN ---"

# Delete by age
find "$OUTPUT_DIR" -name '*.png' -type f -mmin "+$((MAX_AGE_HOURS * 60))" -print0 |
    while IFS= read -r -d '' f; do
        $DRY_RUN && echo "  [age] $f" || rm -f "$f"
    done

# Cap count
COUNT=$(find "$OUTPUT_DIR" -name '*.png' -type f | wc -l)
if [ "$COUNT" -gt "$KEEP" ]; then
    EXCESS=$((COUNT - KEEP))
    echo "Capping: $COUNT → $KEEP (remove $EXCESS)"
    find "$OUTPUT_DIR" -name '*.png' -type f -printf '%T@ %p\0' | sort -zrn | tail -zn "$EXCESS" |
        while IFS= read -r -d '' entry; do
            f="${entry#* }"
            $DRY_RUN && echo "  [cap] $f" || rm -f "$f"
        done
fi

AFTER=$(find "$OUTPUT_DIR" -name '*.png' -type f | wc -l)
REMOVED=$((BEFORE - AFTER))
echo "After: $AFTER images (removed $REMOVED)"
