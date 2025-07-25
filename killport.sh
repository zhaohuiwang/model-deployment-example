#!/bin/bash

# Check if at least one port is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <port1> [port2 ...]"
    exit 1
fi

# Function to check and kill a single port
check_and_kill_port() {
    local PORT=$1
    # Check if port is in use
    PID=$(lsof -t -i :"$PORT" 2>/dev/null)
    
    if [ -z "$PID" ]; then
        echo "Port $PORT is not in use."
        return 0
    fi

    # Port is in use, attempt to kill each PID
    echo "Port $PORT is in use by PID(s): $PID"
    for pid in $PID; do
        echo "Killing process with PID $pid..."
        kill -TERM "$pid" 2>/dev/null
        # Verify if process was killed
        if lsof -t -i :"$PORT" >/dev/null 2>&1; then
            echo "Failed to kill process with PID $pid on port $PORT."
        else
            echo "Process with PID $pid on port $PORT killed successfully."
        fi
    done
}

# Iterate over all provided ports
for port in "$@"; do
    check_and_kill_port "$port"
done

exit 0

# run in the current dir to kill port 8000
# $ ./killport.sh 8000
# run from a child dir to kill port 8000
# $ ../killport.sh 8000
# To check and kill a variable number of ports eg. 8000 8010 8022
# $ ./killport.sh 8000 8010 8022