#!/usr/bin/env python3
from flask import Flask, jsonify
import subprocess
import re

app = Flask(__name__)

def is_valid_ip(ip):
    """Basic validation for an IP address."""
    return re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip)

@app.route('/api/status/<ip_address>')
def get_status(ip_address):
    if not is_valid_ip(ip_address):
        return jsonify({"status": "invalid"}), 400

    # Security: Ensure the IP is on the same subnet to prevent abuse
    if not ip_address.startswith('192.168.1.'):
        return jsonify({"status": "disallowed"}), 403

    try:
        # Using -c 1 for a single ping and -W 1 for a 1-second timeout.
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '1', ip_address],
            capture_output=True, # stdout and stderr are suppressed
            timeout=2  # A total timeout for the command
        )
        if result.returncode == 0:
            return jsonify({"status": "online"})
        else:
            return jsonify({"status": "offline"})
    except subprocess.TimeoutExpired:
        return jsonify({"status": "offline"})
    except Exception:
        return jsonify({"status": "error"})

if __name__ == '__main__':
    # Listen on all interfaces on port 5000
    app.run(host='0.0.0.0', port=5000)