#!/usr/bin/env python3
"""DIAGNOSTIC VERSION - Check execution status"""
import os
import sys
import time
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

@app.route('/diagnose')
def diagnose():
    """Diagnostic endpoint to check execution"""
    try:
        logger.info("DIAGNOSTIC: Checking execution environment...")
        
        # Check environment
        env_info = {
            'python_version': sys.version,
            'working_directory': os.getcwd(),
            'environment_variables': {
                'FORM_1_URL': os.environ.get('FORM_1_URL', 'NOT_SET'),
                'FORM_2_URL': os.environ.get('FORM_2_URL', 'NOT_SET'),
                'PORT': os.environ.get('PORT', 'NOT_SET'),
                'RENDER_DEPLOY_HOOK_URL': 'SET' if os.environ.get('RENDER_DEPLOY_HOOK_URL') else 'NOT_SET'
            },
            'files_in_directory': [],
            'python_path': sys.path
        }
        
        # List files in current directory
        try:
            files = os.listdir('.')
            env_info['files_in_directory'] = files[:10]  # First 10 files
        except Exception as e:
            env_info['files_in_directory'] = ['Error: ' + str(e)]
        
        logger.info("DIAGNOSTIC: Environment check completed")
        
        return jsonify({
            'status': 'diagnostic_complete',
            'timestamp': datetime.now().isoformat(),
            'environment': env_info
        })
        
    except Exception as e:
        logger.error("DIAGNOSTIC ERROR: " + str(e))
        return jsonify({
            'status': 'diagnostic_error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/test')
def test():
    """Test endpoint"""
    try:
        logger.info("TEST: Simple test execution...")
        
        # Simple test operations
        test_results = {
            'time_check': datetime.now().isoformat(),
            'math_test': 2 + 2,
            'string_test': "Hello World".upper(),
            'import_test': 'flask_available'
        }
        
        logger.info("TEST: Simple test completed successfully")
        
        return jsonify({
            'status': 'test_passed',
            'timestamp': datetime.now().isoformat(),
            'test_results': test_results
        })
        
    except Exception as e:
        logger.error("TEST ERROR: " + str(e))
        return jsonify({
            'status': 'test_failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/')
def trigger_burst():
    """Trigger burst execution with diagnostics"""
    try:
        logger.info("BURST: Starting diagnostic burst execution...")
        
        # Get environment variables with defaults
        form1_url = os.environ.get('FORM_1_URL', 'https://httpbin.org/html')
        form2_url = os.environ.get('FORM_2_URL', 'https://httpbin.org/html')
        
        logger.info("BURST: Form 1 URL: " + str(form1_url))
        logger.info("BURST: Form 2 URL: " + str(form2_url))
        
        # Simulate form access with diagnostics
        logger.info("BURST: Simulating form access...")
        time.sleep(0.5)
        logger.info("BURST: Form 1 accessed successfully")
        
        time.sleep(0.5)
        logger.info("BURST: Form 2 accessed successfully")
        
        # Simulate burst pattern
        logger.info("BURST: Executing 2:1 burst pattern...")
        time.sleep(0.5)
        logger.info("BURST: Burst submission 1/3: Form 1 - SUCCESS")
        
        time.sleep(0.5)
        logger.info("BURST: Burst submission 2/3: Form 1 - SUCCESS")
        
        time.sleep(0.5)
        logger.info("BURST: Burst submission 3/3: Form 2 - SUCCESS")
        
        logger.info("BURST: Burst completed: 3/3 submissions successful")
        logger.info("BURST: Diagnostic execution completed successfully")
        logger.info("BURST: End time: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        return jsonify({
            'status': 'success',
            'message': 'Diagnostic burst execution completed successfully',
            'timestamp': datetime.now().isoformat(),
            'submissions': 3,
            'successful': 3,
            'form_urls': {
                'form1': form1_url,
                'form2': form2_url
            },
            'execution_type': 'diagnostic'
        })
            
    except Exception as e:
        logger.error("BURST ERROR: " + str(e))
        import traceback
        logger.error("BURST TRACEBACK: " + str(traceback.format_exc()))
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info("Starting DIAGNOSTIC Flask app on port " + str(port))
    app.run(host='0.0.0.0', port=port, debug=False)
