
#!/bin/bash
# Background Service Launcher for Dual-Form Survey Validator
# Ensures automatic startup and continuous operation

echo "=== Dual-Form Survey Validator Background Service ==="
echo "Starting automatic background service..."

# Check if script is already running
if pgrep -f "survey_validator.py" > /dev/null; then
    echo "Survey validator is already running."
    echo "PID: $(pgrep -f survey_validator.py)"
    echo "To stop: pkill -f survey_validator.py"
    exit 0
fi

# Create auto-restart script
cat > auto_restart.sh << 'EOF'
#!/bin/bash
# Auto-restart wrapper for survey validator

while true; do
    echo "=== Starting Dual-Form Survey Validator ==="
    echo "$(date): Starting survey validator..."
    
    # Run the main script
    python3 survey_validator.py
    
    exit_code=$?
    echo "$(date): Survey validator exited with code $exit_code"
    
    if [ $exit_code -eq 130 ]; then
        echo "User interrupted (Ctrl+C). Stopping auto-restart."
        break
    fi
    
    echo "Restarting in 30 seconds..."
    sleep 30
done
EOF

chmod +x auto_restart.sh

# Function to check and restart if needed
watchdog() {
    local main_pid=$1
    echo "Watchdog started for PID: $main_pid"
    
    while true; do
        sleep 60  # Check every minute
        
        # Check if main process is still running
        if ! kill -0 $main_pid 2>/dev/null; then
            echo "$(date): Main process died. Restarting automatically..."
            
            # Start new process
            nohup python3 survey_validator.py > mission.log 2>&1 &
            main_pid=$!
            echo "$(date): Restarted with new PID: $main_pid"
            
            # Update PID file
            echo $main_pid > survey_validator.pid
        fi
    done
}

# Start the main process in background
echo "Starting main process..."
nohup python3 survey_validator.py > mission.log 2>&1 &
main_pid=$!

# Save PID for management
echo $main_pid > survey_validator.pid

echo "Background service started!"
echo "Main Process PID: $main_pid"
echo "Log File: $(pwd)/mission.log"
echo "PID File: survey_validator.pid"
echo "Auto-restart script: auto_restart.sh"
echo ""

# Start watchdog in background
watchdog $main_pid &
watchdog_pid=$!

echo "Watchdog PID: $watchdog_pid"
echo ""

echo "=== SERVICE STATUS ==="
echo "Main Process PID: $main_pid"
echo "Watchdog PID: $watchdog_pid"
echo "Log File: $(pwd)/mission.log"
echo ""
echo "To stop service:"
echo "1. kill $main_pid $watchdog_pid"
echo "2. pkill -f survey_validator.py"
echo "3. kill \$(cat survey_validator.pid)"
echo ""
echo "To monitor logs:"
echo "tail -f mission.log"

# Create signal handlers for graceful shutdown
cleanup() {
    echo ""
    echo "Stopping background service..."
    
    # Kill main process and watchdog
    kill $main_pid 2>/dev/null
    kill $watchdog_pid 2>/dev/null
    
    # Clean up any remaining processes
    pkill -f survey_validator.py 2>/dev/null
    
    # Remove PID file
    rm -f survey_validator.pid
    
    echo "Background service stopped."
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Keep service running and monitor
while true; do
    # Check if main process is running
    if ! kill -0 $main_pid 2>/dev/null; then
        echo "Main process not found. Exiting..."
        break
    fi
    
    # Check if watchdog is running
    if ! kill -0 $watchdog_pid 2>/dev/null; then
        echo "Watchdog not found. Restarting..."
        watchdog $main_pid &
        watchdog_pid=$!
    fi
    
    sleep 300  # Check every 5 minutes
done

# Final cleanup
cleanup
