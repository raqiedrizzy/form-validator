
#!/bin/bash
# Dual-Form Survey Validator Launcher with Persistence

echo "Starting Dual-Form Survey Validator in background..."
echo "Logs will be written to mission.log"
echo "Use 'tail -f mission.log' to monitor progress"
echo "Use 'pkill -f survey_validator.py' to stop"

# Launch in background with nohup for persistence
nohup python3 survey_validator.py > mission.log 2>&1 &

# Get the process ID
PID=$!
echo "Process started with PID: $PID"
echo "Mission is running autonomously..."

# Optional: Save PID to file for easy management
echo $PID > survey_validator.pid

echo "To stop: kill $PID or pkill -f survey_validator.py"
echo "To monitor: tail -f mission.log"
