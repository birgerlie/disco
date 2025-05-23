#!/usr/bin/env python3
"""
Script to scan a specific endpoint and output enhanced JSON data
"""

import sys
import json
import requests
from pathlib import Path
import urllib3
import xml.etree.ElementTree as ET

# Add parent directory to path if running as a script
parent_dir = str(Path(__file__).parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from discovery_system.endpoint_details import extract_endpoint_details, access_cisco_xml_api

def test_direct_xml_api_access(ip, username="admin", password="TANDBERG"):
    """Test direct access to the XML API for debugging"""
    print(f"\nTesting direct XML API access at {ip}...")
    
    # First test direct HTTP/HTTPS access
    for protocol in ["https", "http"]:
        base_url = f"{protocol}://{ip}"
        try:
            print(f"Testing basic connectivity to {base_url}...")
            response = requests.get(
                base_url,
                auth=(username, password),
                timeout=5,
                verify=False
            )
            print(f"  Status code: {response.status_code}")
            print(f"  Content type: {response.headers.get('Content-Type', 'Unknown')}")
            print(f"  Content length: {len(response.text)} bytes")
        except Exception as e:
            print(f"  Error accessing {base_url}: {str(e)}")
    
    # Now try accessing the XML API directly
    for xml_file in ["status.xml", "config.xml"]:
        for protocol in ["https", "http"]:
            url = f"{protocol}://{ip}/{xml_file}"
            try:
                print(f"Testing direct access to {url}...")
                response = requests.get(
                    url,
                    auth=(username, password),
                    timeout=5,
                    verify=False
                )
                
                print(f"  Status code: {response.status_code}")
                
                if response.status_code == 200:
                    # Try parsing as XML
                    try:
                        root = ET.fromstring(response.text)
                        print(f"  Successfully parsed as XML, root tag: {root.tag}")
                        
                        # For status.xml, check for expected elements
                        if xml_file == "status.xml":
                            product_id = root.find('./SystemUnit/ProductId')
                            if product_id is not None:
                                print(f"  Found ProductId: {product_id.text}")
                            else:
                                print("  ProductId not found")
                    except ET.ParseError as pe:
                        print(f"  XML parsing error: {str(pe)}")
                        print(f"  Content preview: {response.text[:200]}...")
            except Exception as e:
                print(f"  Error accessing {url}: {str(e)}")

def scan_endpoint(ip, username="admin", password="TANDBERG"):
    """Scan a specific endpoint and output enhanced JSON data"""
    print(f"Scanning endpoint at {ip} with enhanced JSON output...")
    
    # Create a simulated endpoint with the specified IP
    endpoint = {
        'ip': ip,
        'hostname': ip,
        'type': 'video_endpoint',
        'open_ports': [443]
    }
    
    # Try to access XML API directly first (for debugging)
    print("\nAttempting to access XML API directly...")
    try:
        xml_details = access_cisco_xml_api(endpoint, username, password)
        print("XML API access result:")
        print(json.dumps(xml_details, indent=2))
    except Exception as e:
        print(f"Error accessing XML API: {str(e)}")
    
    # Extract detailed information using the standard method
    print("\nExtracting endpoint details using standard method...")
    details = extract_endpoint_details(endpoint, username, password)
    
    # Format and output the JSON with all available fields
    formatted_json = json.dumps(details, indent=2)
    
    print("\nEnhanced JSON Output:")
    print(formatted_json)
    
    # If standard method didn't get enhanced data, try direct XML API access
    if details.get('manufacturer') == "Unknown":
        print("\nStandard method didn't get enhanced data, testing direct XML API access...")
        test_direct_xml_api_access(ip, username, password)
    
    return details

if __name__ == "__main__":
    # Default to the endpoint we found earlier
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
    
    print(f"\nTesting endpoint at {ip} with credentials {username}:{password}")
    scan_endpoint(ip, username, password)
    
    print("\nDone!")

