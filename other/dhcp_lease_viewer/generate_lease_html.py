#!/usr/bin/env python3
import datetime
import ipaddress

def main():
    lease_file_path = '/var/lib/misc/dnsmasq.leases'
    template_path = '/etc/leases_template.html'
    html_output_path = '/var/www/html/leases.html'

    # Step 1: Read the lease file and generate table rows
    leases = []
    try:
        with open(lease_file_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                
                # Skip blank lines and lines that don't start with a number (like 'duid ...')
                if not parts or not parts[0].isdigit():
                    continue

                try:
                    expiry_ts_str, ip, mac_duid, host = parts[0], '?', '?', '*'

                    # Differentiate based on second field (MAC for IPv4, IAID for IPv6)
                    if ':' in parts[1]:  # IPv4 lease with MAC
                        mac_duid = parts[1]
                        ip = parts[2]
                        host = parts[3]
                    elif len(parts) >= 4: # IPv6 lease
                        ip = parts[2]
                        host = parts[3]
                        # DUID is usually the last field
                        mac_duid = parts[-1] if len(parts) > 4 else '?'
                    else:
                        continue # Skip malformed lines
                    
                    expiry_time_dt = datetime.datetime.fromtimestamp(int(expiry_ts_str))
                    # Calculate start time assuming a 12-hour lease
                    lease_duration = datetime.timedelta(hours=12)
                    start_time_dt = expiry_time_dt - lease_duration
                    
                    leases.append({
                        'start': start_time_dt.strftime('%Y-%m-%d %H:%M:%S'),
                        'expiry': expiry_time_dt.strftime('%Y-%m-%d %H:%M:%S'),
                        'mac': mac_duid,
                        'ip': ip,
                        'hostname': host if host != '*' else 'N/A'
                    })
                except (IndexError, ValueError):
                    continue
    except FileNotFoundError:
        pass

    table_rows = ""
    if not leases:
        # Update colspan to 6 to match the new header
        table_rows = '<tr><td colspan="6">No active leases found.</td></tr>'
    else:
        # Sort leases by IP version first, then by the IP address itself
        for lease in sorted(leases, key=lambda x: (ipaddress.ip_address(x['ip']).version, ipaddress.ip_address(x['ip']))):
            table_rows += f"""
            <tr>
                <td>{lease['ip']}</td>
                <td>{lease['start']}</td>
                <td>{lease['mac']}</td>
                <td>{lease['hostname']}</td>
                <td>{lease['expiry']}</td>
                <td data-ip="{lease['ip']}"><span class="status-dot status-checking"></span>Checking...</td>
            </tr>"""
    
    # Step 2: Read the template file
    try:
        with open(template_path, 'r') as f:
            template_content = f.read()
    except FileNotFoundError:
        print(f"Error: Template file not found at {template_path}")
        return

    # Step 3: Replace placeholders
    final_html = template_content.replace('<!--LEASE_ROWS-->', table_rows)
    final_html = final_html.replace('<!--LAST_UPDATED-->', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # Step 4: Write the final HTML file
    with open(html_output_path, 'w') as f:
        f.write(final_html)
    print(f"Successfully generated {html_output_path}")

if __name__ == '__main__':
    main()
