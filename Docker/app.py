import os
import subprocess
import re
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

ZONE_DIR = "/etc/bind/zones"
NAMED_CONF = "/etc/bind/named.conf"

@app.route('/add_record', methods=['POST'])
def add_record():
    """Add a DNS record."""
    domain = request.json.get('domain')
    record_type = request.json.get('type')
    name = request.json.get('name')
    value = request.json.get('value')

    # Validate input
    if not all([domain, record_type in ["A", "CNAME", "MX", "TXT"], name, value]):
        return jsonify({"error": "Invalid input"}), 400

    zone_file = f"{ZONE_DIR}/db.{domain}"

    # Create zone file if it doesn't exist
    if not os.path.exists(zone_file):
        create_zone_file(domain)
        add_zone_to_named_conf(domain)

    # Add the DNS record to the zone file
    with open(zone_file, 'a') as file:
        file.write(f"{name} IN {record_type} {value}\n")

    # Increment the serial number and reload BIND
    increment_serial_number(zone_file)
    reload_bind(domain)

    return jsonify({"message": "Record added successfully"}), 200

@app.route('/delete_record', methods=['POST'])
def delete_record():
    """Delete a DNS record."""
    domain = request.json.get('domain')
    name = request.json.get('name')

    # Validate input
    if not all([domain, name]):
        return jsonify({'error': 'Missing domain or name'}), 400

    zone_file_path = f"{ZONE_DIR}/db.{domain}"

    try:
        # Read and filter records from the zone file
        with open(zone_file_path, 'r') as file:
            lines = file.readlines()

        with open(zone_file_path, 'w') as file:
            for line in lines:
                if name not in line:
                    file.write(line)

        # Increment the serial number and reload BIND
        increment_serial_number(zone_file_path)
        reload_bind(domain)

        return jsonify({'message': 'Record deleted successfully'}), 200

    except FileNotFoundError:
        return jsonify({'error': f'Zone file for {domain} not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/check_record', methods=['POST'])
def check_record():
    """Check DNS records using the dig command."""
    domain = request.json.get('domain')

    if not domain:
        return jsonify({'error': 'Missing domain'}), 400

    try:
        result = subprocess.run(['dig', f'@localhost', domain], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            return jsonify({'error': 'Failed to execute dig command', 'details': result.stderr}), 500

        return jsonify({'output': result.stdout}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def reload_bind(domain):
    """Reload the BIND configuration."""
    subprocess.run(["/entrypoint.sh", "reload_bind", domain])

def create_zone_file(domain):
    """Create a zone file for the given domain."""
    zone_file = f"{ZONE_DIR}/db.{domain}"
    with open(zone_file, 'w') as file:
        file.write(f"""
$TTL 86400
@   IN  SOA ns1.{domain}. admin.{domain}. (
            2023101901  ; Serial number
            3600        ; Refresh (1 hour)
            1800        ; Retry (30 minutes)
            604800      ; Expire (1 week)
            86400       ; Minimum TTL (1 day)
        )

@   IN  NS  ns1.{domain}.
@   IN  NS  ns2.{domain}.

ns1 IN  A   192.168.1.10
ns2 IN  A   192.168.1.11
""")
    print(f"Created zone file for {domain}")

def add_zone_to_named_conf(domain):
    """Add the zone configuration to named.conf."""
    zone_config = f"""
zone "{domain}" {{
    type master;
    file "{ZONE_DIR}/db.{domain}";
}};
"""
    with open(NAMED_CONF, 'a') as file:
        file.write(zone_config)
    print(f"Added zone for {domain} to named.conf")

def increment_serial_number(zone_file):
    """Increment the serial number in the SOA record of the zone file."""
    with open(zone_file, 'r') as file:
        zone_data = file.readlines()

    soa_index = next((i for i, line in enumerate(zone_data) if "SOA" in line), -1)
    if soa_index == -1:
        print(f"No SOA record found in {zone_file}.")
        return

    serial_line = zone_data[soa_index + 1]
    current_serial = int(re.search(r"\d{10}", serial_line).group(0))
    new_serial = increment_serial(current_serial)

    zone_data[soa_index + 1] = serial_line.replace(str(current_serial), str(new_serial)) + "\n"

    with open(zone_file, 'w') as file:
        file.writelines(zone_data)

    print(f"Updated serial number for {zone_file} to {new_serial}.")

def increment_serial(current_serial):
    """Increment the serial number based on the current date."""
    today = datetime.now().strftime("%Y%m%d")
    base_serial = int(today + "00")
    return base_serial if current_serial < base_serial else current_serial + 1

# Sample curl commands for API usage
def print_curl_examples():
    print("Sample CURL requests:")
    print("\nAdd Record:")
    print(f"curl -X POST http://localhost:5000/add_record -H \"Content-Type: application/json\" -d '{{\"domain\": \"test.com\", \"type\": \"A\", \"name\": \"test.test.com\", \"value\": \"192.168.1.10\"}}'")
    
    print("\nDelete Record:")
    print(f"curl -X POST http://localhost:5000/delete_record -H \"Content-Type: application/json\" -d '{{\"domain\": \"test.com\", \"name\": \"test.test.com\"}}'")
    
    print("\nCheck Record:")
    print(f"curl -X POST http://localhost:5000/check_record -H \"Content-Type: application/json\" -d '{{\"domain\": \"test.com\"}}'")

if __name__ == '__main__':
    print_curl_examples()
    app.run(host='0.0.0.0', port=5000)
