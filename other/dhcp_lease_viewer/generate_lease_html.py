#!/usr/bin/env python3
import datetime

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
                if len(parts) >= 4:
                    expiry_timestamp = int(parts[0])
                    mac_address = parts[1]
                    ip_address = parts[2]
                    hostname = parts[3]
                    
                    expiry_time = datetime.datetime.fromtimestamp(expiry_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    
                    leases.append({
                        'expiry': expiry_time,
                        'mac': mac_address,
                        'ip': ip_address,
                        'hostname': hostname if hostname != '*' else 'N/A'
                    })
    except FileNotFoundError:
        pass

    table_rows = ""
    if not leases:
        table_rows = '<tr><td colspan="5">No active leases found.</td></tr>'
    else:
        for lease in sorted(leases, key=lambda x: [int(octet) for octet in x['ip'].split('.')]):
            table_rows += f"""
            <tr>
                <td>{lease['ip']}</td>
                <td>{lease['mac']}</td>
                <td>{lease['hostname']}</td>
                <td>{lease['expiry']}</td>
                <td><button class="ping-btn" onclick="pingIp('{lease['ip']}')">Ping</button></td>
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

if __name__ == '__main__':
    main()