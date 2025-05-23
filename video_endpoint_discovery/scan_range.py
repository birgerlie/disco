#!/usr/bin/env python3
"""
Script to scan a range of IP addresses for video endpoints
and output detailed information in JSON format
"""

import sys
import json
from pathlib import Path

# Add parent directory to path if running as a script
parent_dir = str(Path(__file__).parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from discovery_system.discover import find_endpoints
from discovery_system.endpoint_details import extract_endpoint_details

def scan_ip_range(start_ip, end_ip, username="admin", password="TANDBERG"):
    """Scan a range of IP addresses and force them to be classified as endpoints"""
    # Generate the list of IPs to scan
    ip_prefix = ".".join(start_ip.split(".")[:3])
    start_octet = int(start_ip.split(".")[-1])
    end_octet = int(end_ip.split(".")[-1])
    
    force_endpoints = []
    for octet in range(start_octet, end_octet + 1):
        force_endpoints.append(f"{ip_prefix}.{octet}")
    
    print(f"Scanning and forcing classification of IPs: {force_endpoints}")
    
    # Run the scan with forced endpoint classification
    endpoints = find_endpoints(
        ip_range=f"{ip_prefix}.{start_octet}/29",  # Use CIDR that covers the range
        include_details=True,
        force_endpoints=force_endpoints,
        username=username,
        password=password
    )
    
    # Enhance each endpoint with detailed information if available
    enhanced_endpoints = []
    for endpoint in endpoints:
        # If we didn't get detailed information from the initial scan,
        # try to extract it directly
        if 'manufacturer' not in endpoint or endpoint['manufacturer'] == 'Unknown':
            print(f"Extracting detailed information for {endpoint['ip']}...")
            details = extract_endpoint_details(endpoint, username, password)
            enhanced_endpoints.append(details)
        else:
            enhanced_endpoints.append(endpoint)
    
    # Output the enhanced endpoints in JSON format
    print(json.dumps(enhanced_endpoints, indent=2))
    
    return enhanced_endpoints

if __name__ == "__main__":
    # Set default username and password
    username = "admin"
    password = "TANDBERG"
    
    # Parse command line arguments if provided
    if len(sys.argv) >= 3:
        start_ip = sys.argv[1]
        end_ip = sys.argv[2]
        if len(sys.argv) >= 5:
            username = sys.argv[3]
            password = sys.argv[4]
    else:
        # Default to scanning 172.17.20.70 to 172.17.20.75
        start_ip = "172.17.20.70"
        end_ip = "172.17.20.75"
    
    scan_ip_range(start_ip, end_ip, username, password)
