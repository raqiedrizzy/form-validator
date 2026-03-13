#!/usr/bin/env python3
"""Simplified Flask App for Render Deployment"""
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

@app.route('/')
def trigger_burst():
    """Trigger simplified survey validator burst execution"""
    try:
        logger.info("Triggering SIMPLIFIED Survey Validator burst execution...")
        
        # Execute simple_main.py as subprocess
        process = subprocess.Popen(
            [sys.executable, 'simple_main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Read output in real-time
        output_lines = []
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                line = line.strip()
                output_lines.append(line)
                logger.info("MAIN: " + line)
        
        # Wait for process to complete
        return_code = process.wait(timeout=1800)  # 30 minutes timeout
        
        if return_code == 0:
            logger.info("SIMPLIFIED Survey Validator burst completed successfully")
            return jsonify({
                'status': 'success',
                'message': 'Simplified burst execution completed',
                'timestamp': datetime.now().isoformat(),
                'output_lines': len(output_lines)
            })
        else:
            logger.error("SIMPLIFIED Survey Validator burst failed with code " + str(return_code))
            return jsonify({
                'status': 'error',
                'message': 'Simplified burst execution failed',
                'timestamp': datetime.now().isoformat(),
                'return_code': return_code,
                'output_lines': len(output_lines)
            }), 500
            
    except subprocess.TimeoutExpired:
        logger.error("SIMPLIFIED Survey Validator burst timed out")
        process.kill()
        return jsonify({
            'status': 'timeout',
            'message': 'Simplified burst execution timed out',
            'timestamp': datetime.now().isoformat()
        }), 500
    except Exception as e:
        logger.error("Unexpected error: " + str(e))
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/test')
def test():
    """Test endpoint to verify functionality"""
    try:
        # Test environment variables
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info("Starting SIMPLIFIED Flask app on port " + str(port))
    app.run(host='0.0.0.0', port=port, debug=False)
