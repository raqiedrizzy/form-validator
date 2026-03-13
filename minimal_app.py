#!/usr/bin/env python3
"""Minimal Flask App for Render"""
import os
import sys
import subprocess
import logging
from datetime import datetime
from flask import Flask, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'survey-validator'
    })

@app.route('/status')
def status():
    """Get current status"""
    return jsonify({
        'service': 'survey-validator',
        'status': 'ready',
        'timestamp': datetime.now().isoformat(),
        'environment': 'render'
    })

@app.route('/test')
def test():
    """Test endpoint"""
    try:
        form1_url = os.environ.get('FORM_1_URL')
        form2_url = os.environ.get('FORM_2_URL')
        
        return jsonify({
            'status': 'test_passed',
            'timestamp': datetime.now().isoformat(),
            'environment': {
                'form1_url_set': bool(form1_url),
                'form2_url_set': bool(form2_url),
                'python_version': sys.version,
                'working_directory': os.getcwd()
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'test_failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/')
def trigger_burst():
    """Trigger minimal survey validator"""
    try:
        logger.info("Triggering MINIMAL Survey Validator execution...")
        
        # Execute minimal_main.py
        process = subprocess.run(
            [sys.executable, 'minimal_main.py'],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        # Log output
        if process.stdout:
            for line in process.stdout.strip().split('\n'):
                if line.strip():
                    logger.info("MAIN: " + line.strip())
        
        if process.stderr:
            for line in process.stderr.strip().split('\n'):
                if line.strip():
                    logger.error("MAIN_ERROR: " + line.strip())
        
        if process.returncode == 0:
            logger.info("MINIMAL Survey Validator completed successfully")
            return jsonify({
                'status': 'success',
                'message': 'Minimal execution completed',
                'timestamp': datetime.now().isoformat(),
                'return_code': 0
            })
        else:
            logger.error("MINIMAL Survey Validator failed with code " + str(process.returncode))
            return jsonify({
                'status': 'error',
                'message': 'Minimal execution failed',
                'timestamp': datetime.now().isoformat(),
                'return_code': process.returncode
            }), 500
            
    except subprocess.TimeoutExpired:
        logger.error("MINIMAL Survey Validator timed out")
        return jsonify({
            'status': 'timeout',
            'message': 'Minimal execution timed out',
            'timestamp': datetime.now().isoformat()
        }), 500
    except Exception as e:
        logger.error("Unexpected error: " + str(e))
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info("Starting MINIMAL Flask app on port " + str(port))
    app.run(host='0.0.0.0', port=port, debug=False)
