#!/usr/bin/env python3
import datetime

def format_leases(lease_file="/var/lib/misc/dnsmasq.leases"):
    """
    Parses a dnsmasq.leases file and prints a formatted table.
    Handles both IPv4 and IPv6 lease formats.
    """
    try:
        with open(lease_file, 'r') as f:
            leases = f.readlines()
    except FileNotFoundError:
        print(f"Error: Lease file not found at {lease_file}")
        return

    if not leases:
        print("Lease file is empty.")
        return

    # Header for the table (Lease Start and Lease Expiry swapped)
    header = ["Lease Start", "Lease Expiry", "IP Address", "MAC / DUID", "Hostname"]
    
    # Data rows
    data = []

    for line in leases:
        parts = line.strip().split()
        
        # Skip blank lines and lines that don't start with a number (like 'duid ...')
        if not parts or not parts[0].isdigit():
            continue

        try:
            expiry_ts_str = parts[0]
            
            # Differentiate based on second field (MAC for IPv4, IAID for IPv6)
            if ':' in parts[1]:  # IPv4 lease with MAC
                mac_duid = parts[1]
                ip = parts[2]
                host = parts[3]
            elif len(parts) >= 4: # IPv6 lease
                ip = parts[2]
                host = parts[3]
                # DUID is usually the last field, starting with '01:' or similar
                mac_duid = parts[-1] if len(parts) > 4 else '?'
            else:
                continue # Skip malformed lines

            expiry_time_dt = datetime.datetime.fromtimestamp(int(expiry_ts_str))
            
            # Calculate start time by subtracting lease duration (12 hours = 43200 seconds)
            # This assumes a fixed lease duration of 12 hours from dnsmasq config
            lease_duration_seconds = 12 * 3600 # 12 hours
            start_time_dt = expiry_time_dt - datetime.timedelta(seconds=lease_duration_seconds)

            expiry_time_str = expiry_time_dt.strftime('%Y-%m-%d %H:%M:%S')
            start_time_str = start_time_dt.strftime('%Y-%m-%d %H:%M:%S')

            # Append data in the new order: Lease Start, Lease Expiry
            data.append([start_time_str, expiry_time_str, ip, mac_duid, host])

        except (IndexError, ValueError) as e:
            # print(f"Skipping malformed line: {line.strip()} - Error: {e}")
            continue
            
    # --- Formatting and Printing Logic (same as before) ---
    if not data:
        print("No valid lease entries found.")
        return
        
    widths = [len(h) for h in header]
    for row in data:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    header_line = " | ".join(header[i].ljust(widths[i]) for i in range(len(header)))
    separator = "-+-".join("-" * widths[i] for i in range(len(widths)))
    print(header_line)
    print(separator)

    for row in data:
        row_line = " | ".join(str(row[i]).ljust(widths[i]) for i in range(len(row)))
        print(row_line)

if __name__ == "__main__":
    format_leases()