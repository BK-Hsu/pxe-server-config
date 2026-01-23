#!/usr/bin/env python3
from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for the entire app

def is_valid_ip(ip):
    """Basic validation for an IP address."""
    return re.match(r"^[0-9a-fA-F:.]+$", ip)

@app.route('/api/status/<ip_address>')
def get_status(ip_address):
    if not is_valid_ip(ip_address):
        return jsonify({"status": "invalid"}), 400

    # --- Method 1: Try to ping (ICMP) ---
    try:
        ping_command = ['ping', '-c', '1', '-W', '1', ip_address]
        if ':' in ip_address:
            ping_command = ['ping', '-6', '-c', '1', '-W', '1', ip_address]
        
        result = subprocess.run(ping_command, capture_output=True, timeout=1.5)
        if result.returncode == 0:
            return jsonify({"status": "online"})
    except (subprocess.TimeoutExpired, Exception):
        # Ping failed, proceed to nc check
        pass

    # --- Method 2: Try to check common TCP ports if ping fails ---
    ports_to_check = [22, 80, 443]
    for port in ports_to_check:
        try:
            nc_command = ['nc', '-vz', '-w', '1', ip_address, str(port)]
            # nc's output for success/failure is on stderr
            result = subprocess.run(nc_command, capture_output=True, timeout=1.5)
            # A successful connection will have "succeeded" in stderr
            if "succeeded" in result.stderr.decode().lower():
                return jsonify({"status": "online"})
        except (subprocess.TimeoutExpired, Exception):
            # nc command failed, try next port
            continue

    # If all methods fail, return offline
    return jsonify({"status": "offline"})

if __name__ == '__main__':
    # Listen on all interfaces on port 5000
    app.run(host='0.0.0.0', port=5000)
