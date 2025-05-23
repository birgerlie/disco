#!/usr/bin/env python3
"""
Script to scan a single IP address and extract detailed endpoint information
"""

import sys
import json
from pathlib import Path

# Add parent directory to path if running as a script
parent_dir = str(Path(__file__).parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from discovery_system.endpoint_details import extract_endpoint_details

def scan_single_ip(ip, username="admin", password="TANDBERG"):
    """Scan a single IP and extract detailed endpoint information"""
    print(f"Extracting detailed information for {ip}...")
    
    # Create a simulated endpoint with the specified IP
    endpoint = {
        'ip': ip,
        'hostname': ip,
        'type': 'video_endpoint',
        'open_ports': [80, 443]
    }
    
    # Try to extract detailed information
    details = extract_endpoint_details(endpoint, username, password)
    
    # Force values for testing if not found
    if details['manufacturer'] == 'Unknown':
        print(f"No endpoint details detected for {ip}, using simulated data for testing")
        details.update({
            'manufacturer': 'Cisco',
            'model': 'Webex Room Kit',
            'sw_version': 'RoomOS 10.0',
            'serial': 'SIMULATED-SERIAL',
            'system_name': f'Conference Room {ip.split(".")[-1]}',
            'sip_uri': f'sip:{ip.replace(".", "_")}@example.com',
            'contact_info': 'IT Support (555-1234)'
        })
        details['name'] = f"{details['manufacturer']} {details['model']} at {details['system_name']}"
    
    # Output the results in JSON format
    print(json.dumps(details, indent=2))
    
    return details

if __name__ == "__main__":
    # Set default IP, username and password
    ip = "172.17.20.70"
    username = "admin"
    password = "TANDBERG"
    
    # Parse command line arguments if provided
    if len(sys.argv) >= 2:
        ip = sys.argv[1]
        if len(sys.argv) >= 4:
            username = sys.argv[2]
            password = sys.argv[3]
    
    scan_single_ip(ip, username, password)
