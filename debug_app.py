#!/usr/bin/env python3
"""DEBUG VERSION - Maximum logging"""
import os
import sys
import time
from datetime import datetime
from flask import Flask, jsonify

app = Flask(__name__)

# Simple print logging that goes to stdout
def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

@app.route('/health')
def health():
    log("HEALTH CHECK")
    return jsonify({'status': 'healthy', 'service': 'survey-validator'})

@app.route('/status')
def status():
    log("STATUS CHECK")
    return jsonify({'status': 'ready', 'service': 'survey-validator'})

@app.route('/debug')
def debug():
    log("DEBUG ENDPOINT CALLED")
    try:
        info = {
            'python_version': sys.version.split()[0],
            'working_dir': os.getcwd(),
            'files': os.listdir('.')[:5],
            'env_vars': {
                'PORT': os.environ.get('PORT', 'NOT_SET'),
                'FORM_1_URL': os.environ.get('FORM_1_URL', 'NOT_SET')[:20] + '...' if os.environ.get('FORM_1_URL') else 'NOT_SET',
                'FORM_2_URL': os.environ.get('FORM_2_URL', 'NOT_SET')[:20] + '...' if os.environ.get('FORM_2_URL') else 'NOT_SET'
            }
        }
        log(f"DEBUG INFO: {info}")
        return jsonify({'status': 'debug_ok', 'info': info})
    except Exception as e:
        log(f"DEBUG ERROR: {str(e)}")
        return jsonify({'status': 'debug_error', 'error': str(e)}), 500

@app.route('/')
def burst():
    log("BURST START")
    try:
        # Step 1
        log("Step 1: Getting URLs")
        form1 = os.environ.get('FORM_1_URL', 'default1')
        form2 = os.environ.get('FORM_2_URL', 'default2')
        log(f"Form URLs: {form1[:20]}..., {form2[:20]}...")
        
        # Step 2
        log("Step 2: Simulating submissions")
        for i in range(3):
            log(f"Submission {i+1}/3")
            time.sleep(0.1)  # Minimal delay
        
        # Step 3
        log("Step 3: Returning success")
        return jsonify({
            'status': 'success',
            'message': 'Debug burst executed',
            'timestamp': datetime.now().isoformat(),
            'submissions': 3
        })
    except Exception as e:
        log(f"BURST ERROR: {str(e)}")
        import traceback
        log(f"TRACEBACK: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    log(f"Starting debug app on port {port}")
    app.run(host='0.0.0.0', port=port)
