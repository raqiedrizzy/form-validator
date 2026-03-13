#!/usr/bin/env python3
"""ULTRA MINIMAL - Bare bones Flask app"""
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'survey-validator'})

@app.route('/status')
def status():
    return jsonify({'status': 'ready', 'service': 'survey-validator'})

@app.route('/')
def burst():
    # Absolute minimal execution
    return jsonify({
        'status': 'success',
        'message': 'Ultra minimal burst executed',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
