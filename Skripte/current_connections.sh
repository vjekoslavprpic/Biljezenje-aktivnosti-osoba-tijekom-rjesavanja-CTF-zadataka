#!/bin/bash

ES_HOST="10.8.0.2"
ES_PORT="6002"
INDEX_NAME="outbound_connections"
INTERVAL=10

LAST_CONNECTIONS=""

while true; do
    CURRENT_CONNECTIONS=$(sudo lsof -iTCP -sTCP:ESTABLISHED -nP)

    if [[ "$CURRENT_CONNECTIONS" != "$LAST_CONNECTIONS" ]]; then
        echo "$CURRENT_CONNECTIONS" | while read -r connection; do
            COMMAND=$(echo "$connection" | awk '{print $1}')
            PID=$(echo "$connection" | awk '{print $2}')
            USER=$(echo "$connection" | awk '{print $3}')
            FD=$(echo "$connection" | awk '{print $4}')
            TYPE=$(echo "$connection" | awk '{print $5}')
            DEVICE=$(echo "$connection" | awk '{print $6}')
            SIZE_OFF=$(echo "$connection" | awk '{print $7}')
            NODE=$(echo "$connection" | awk '{print $8}')
            NAME=$(echo "$connection" | awk '{print $9}')
            
            TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

            JSON_DATA=$(cat <<EOF
{
    "timestamp": "$TIMESTAMP",
    "command": "$COMMAND",
    "pid": "$PID",
    "user": "$USER",
    "fd": "$FD",
    "type": "$TYPE",
    "device": "$DEVICE",
    "size_off": "$SIZE_OFF",
    "node": "$NODE",
    "name": "$NAME"
}
EOF
            )

            curl -X POST "http://$ES_HOST:$ES_PORT/$INDEX_NAME/_doc" \
                 -H 'Content-Type: application/json' \
                 -d "$JSON_DATA"
        done

        LAST_CONNECTIONS="$CURRENT_CONNECTIONS"
    fi

    sleep $INTERVAL
done
