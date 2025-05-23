#!/usr/bin/env python3
"""
Script to check XML configuration for a specific endpoint
"""

import sys
import json
from pathlib import Path

# Add parent directory to path if running as a script
parent_dir = str(Path(__file__).parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import requests
import urllib3
from discovery_system.endpoint_details import access_cisco_xml_api

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_endpoint_xml(ip, username="admin", password="TANDBERG"):
    """Check XML configuration for a specific endpoint"""
    print(f"Checking XML configuration for endpoint at {ip}")
    
    # Create endpoint dictionary
    endpoint = {
        'ip': ip,
        'hostname': ip,
        'type': 'video_endpoint',
        'open_ports': [443]  # Based on scan results
    }
    
    # Try to access status.xml
    status_url = f"https://{ip}/status.xml"
    print(f"Attempting to access {status_url}")
    try:
        status_response = requests.get(
            status_url,
            auth=(username, password),
            timeout=10,
            verify=False
        )
        
        if status_response.status_code == 200:
            print(f"Successfully accessed status.xml")
            print("Content:")
            print(status_response.text[:1000])  # Show first 1000 characters
            print("...")
        else:
            print(f"Failed to access status.xml: Status code {status_response.status_code}")
    except Exception as e:
        print(f"Error accessing status.xml: {str(e)}")
    
    # Try to access config.xml
    config_url = f"https://{ip}/config.xml"
    print(f"\nAttempting to access {config_url}")
    try:
        config_response = requests.get(
            config_url,
            auth=(username, password),
            timeout=10,
            verify=False
        )
        
        if config_response.status_code == 200:
            print(f"Successfully accessed config.xml")
            print("Content:")
            print(config_response.text[:1000])  # Show first 1000 characters
            print("...")
        else:
            print(f"Failed to access config.xml: Status code {config_response.status_code}")
    except Exception as e:
        print(f"Error accessing config.xml: {str(e)}")
    
    # Try using our XML API function
    print("\nAttempting to use the access_cisco_xml_api function:")
    try:
        xml_details = access_cisco_xml_api(endpoint, username, password)
        if xml_details:
            print("Successfully extracted details using XML API:")
            print(json.dumps(xml_details, indent=2))
        else:
            print("No details could be extracted using the XML API")
    except Exception as e:
        print(f"Error using access_cisco_xml_api: {str(e)}")

if __name__ == "__main__":
    # IP address of the detected endpoint
    ip = "172.17.41.19"
    
    # Parse command line arguments if provided
    if len(sys.argv) >= 2:
        ip = sys.argv[1]
    
    # Default credentials
    username = "admin"
    password = "TANDBERG"
    
    # Parse credentials if provided
    if len(sys.argv) >= 4:
        username = sys.argv[2]
        password = sys.argv[3]
    
    check_endpoint_xml(ip, username, password)
