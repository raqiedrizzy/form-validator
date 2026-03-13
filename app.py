#!/usr/bin/env python3
"""Flask Entry Point for Render Deployment"""
import os
import sys
import subprocess
import logging
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

@app.route('/health')
def health_check():
    """Render health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'survey-validator'
    })

@app.route('/')
def trigger_burst():
    """Trigger survey validator burst execution"""
    try:
        logger.info("Triggering Survey Validator burst execution...")
        
        # Execute main.py as subprocess with better error handling
        import subprocess
        import threading
        import queue
        
        # Use a queue to capture output
        output_queue = queue.Queue()
        
        def read_output(process, queue):
            """Read process output and put in queue"""
            try:
                for line in iter(process.stdout.readline, ''):
                    queue.put(('stdout', line.rstrip()))
                for line in iter(process.stderr.readline, ''):
                    queue.put(('stderr', line.rstrip()))
                process.stdout.close()
                process.stderr.close()
            except:
                pass
        
        # Start the subprocess
        process = subprocess.Popen(
            [sys.executable, 'main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Start thread to read output
        reader_thread = threading.Thread(target=read_output, args=(process, output_queue))
        reader_thread.daemon = True
        reader_thread.start()
        
        # Wait for process to complete with timeout
        try:
            return_code = process.wait(timeout=1800)  # 30 minutes timeout
            
            # Read remaining output
            while not output_queue.empty():
                stream, line = output_queue.get()
                if stream == 'stdout':
                    logger.info(line)
                else:
                    logger.error(line)
            
            if return_code == 0:
                logger.info("Survey Validator burst completed successfully")
                return jsonify({
                    'status': 'success',
                    'message': 'Burst execution completed',
                    'timestamp': datetime.now().isoformat()
                })
            else:
                logger.error("Survey Validator burst failed with code " + str(return_code))
                return jsonify({
                    'status': 'error',
                    'message': 'Burst execution failed',
                    'timestamp': datetime.now().isoformat()
                }), 500
                
        except subprocess.TimeoutExpired:
            logger.error("Survey Validator burst timed out")
            process.kill()
            return jsonify({
                'status': 'timeout',
                'message': 'Burst execution timed out',
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        logger.error("Unexpected error: " + str(e))
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/status')
def status():
    """Get current status"""
    return jsonify({
        'service': 'survey-validator',
        'status': 'ready',
        'timestamp': datetime.now().isoformat(),
        'environment': 'render'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info("Starting Flask app on port " + str(port))
    app.run(host='0.0.0.0', port=port, debug=False)
