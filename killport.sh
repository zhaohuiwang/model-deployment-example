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
        echo "Attempting to kill process with PID $pid (SIGTERM)..."
        kill -TERM "$pid" 2>/dev/null
        # Wait briefly to allow process to terminate
        sleep 1
        # Check if process still holds the port
        if lsof -t -i :"$PORT" >/dev/null 2>&1; then
            echo "SIGTERM failed for PID $pid. Trying SIGKILL..."
            sudo kill -KILL "$pid" 2>/dev/null
            # Wait again and verify
            sleep 1
            if lsof -t -i :"$PORT" >/dev/null 2>&1; then
                echo "Failed to kill process with PID $pid on port $PORT."
                return 1
            else
                echo "Process with PID $pid on port $PORT killed successfully (SIGKILL)."
            fi
        else
            echo "Process with PID $pid on port $PORT killed successfully (SIGTERM)."
        fi
    done
    return 0
}

# Iterate over all provided ports
EXIT_STATUS=0
for port in "$@"; do
    check_and_kill_port "$port"
    # Track if any port fails to free
    [ $? -ne 0 ] && EXIT_STATUS=1
done

exit $EXIT_STATUS

# run in the current dir to kill port 8000
# $ ./killport.sh 8000
# run from a child dir to kill port 8000
# $ ../killport.sh 8000
# To check and kill a variable number of ports eg. 8000 8010 8022
# $ ./killport.sh 8000 8010 8022