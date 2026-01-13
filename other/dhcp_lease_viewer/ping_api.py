#!/usr/bin/env python3
from flask import Flask, jsonify
import subprocess
import re

app = Flask(__name__)

def is_valid_ip(ip):
    """Basic validation for an IP address."""
    return re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip)

@app.route('/api/ping/<ip_address>')
def ping_ip(ip_address):
    if not is_valid_ip(ip_address):
        return jsonify({"error": "Invalid IP address format"}), 400

    # Security: Ensure the IP is on the same subnet to prevent abuse
    if not ip_address.startswith('192.168.1.'):
        return jsonify({"error": "Pinging this IP is not allowed"}), 403

    try:
        # Using -c 4 for 4 pings and -W 1 for a 1-second timeout per ping
        result = subprocess.run(
            ['ping', '-c', '4', '-W', '1', ip_address],
            capture_output=True,
            text=True,
            timeout=5  # A total timeout for the command
        )
        return jsonify({
            "ip": ip_address,
            "output": result.stdout,
            "error": result.stderr
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": f"Ping command timed out for {ip_address}"}), 504
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # Listen on all interfaces on port 5000
    app.run(host='0.0.0.0', port=5000)