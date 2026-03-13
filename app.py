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
        
        # Execute main.py as subprocess
        result = subprocess.run(
            [sys.executable, 'main.py'],
            capture_output=False,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        if result.returncode == 0:
            logger.info("Survey Validator burst completed successfully")
            return jsonify({
                'status': 'success',
                'message': 'Burst execution completed',
                'timestamp': datetime.now().isoformat()
            })
        else:
            logger.error("Survey Validator burst failed with code " + str(result.returncode))
            return jsonify({
                'status': 'error',
                'message': 'Burst execution failed',
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except subprocess.TimeoutExpired:
        logger.error("Survey Validator burst timed out")
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
