# Redis population script
# SPDX - License - Identifier: LGPL - 3.0 - or -later
# Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2026

#!/bin/bash
set -e

redis-server &
REDIS_PID=$!

sleep 2

# Only load if database is empty
DBSIZE=$(redis-cli DBSIZE | grep -oE '[0-9]+')
if [ "$DBSIZE" -eq 0 ]; then
  echo "Loading .redis files..."
  for file in /commands/*.redis; do
    [ -f "$file" ] && redis-cli < "$file"
  done
fi

wait $REDIS_PID