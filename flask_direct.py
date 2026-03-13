#!/usr/bin/env python3
"""FLASK DIRECT - Use Flask's built-in server instead of Gunicorn"""
import os
import sys
from datetime import datetime
from flask import Flask, jsonify

app = Flask(__name__)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Not found', 'timestamp': datetime.now().isoformat()}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error', 'timestamp': datetime.now().isoformat()}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'survey-validator', 'timestamp': datetime.now().isoformat()})

@app.route('/status')
def status():
    return jsonify({'status': 'ready', 'service': 'survey-validator', 'timestamp': datetime.now().isoformat()})

@app.route('/')
def burst():
    try:
        return jsonify({
            'status': 'success',
            'message': 'Flask direct burst executed',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask direct server on port {port}", flush=True)
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
