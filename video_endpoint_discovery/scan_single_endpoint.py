#!/usr/bin/env python3
"""
Script to scan and extract detailed information from a single endpoint
Focuses on using the enhanced Cisco XML API detection
"""

import sys
import json
from pathlib import Path
import urllib3
import argparse

# Add parent directory to path if running as a script
parent_dir = str(Path(__file__).parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from discovery_system.endpoint_details import extract_endpoint_details
from discovery_system.network_utils import scan_ip

def scan_single_endpoint(ip, username="admin", password="TANDBERG", verbose=False):
    """
    Scan a single endpoint and extract detailed information
    """
    print(f"Scanning endpoint at {ip}...")
    
    # Suppress requests/urllib3 warnings about insecure requests
    if not verbose:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # First, scan the IP to check if it's a video endpoint
    scan_result = scan_ip(
        ip=ip,
        timeout=5,
        force_endpoint=True,  # Force it to be treated as an endpoint
        username=username,
        password=password
    )
    
    if not scan_result or scan_result.get('type') != 'video_endpoint':
        print(f"No video endpoint detected at {ip}")
        return None
    
    # If it is a video endpoint, extract detailed information
    print(f"Video endpoint detected at {ip}. Extracting details...")
    
    # Try different common credentials if needed
    credentials_to_try = [
        (username, password),  # User-provided credentials first
        ("admin", "TANDBERG"),  # Default Cisco credentials
        ("admin", "admin"),     # Common alternative
        ("admin", ""),          # Empty password
        ("", ""),               # No credentials
    ]
    
    # Try each set of credentials
    best_details = None
    for cred_username, cred_password in credentials_to_try:
        if cred_username == username and cred_password == password and best_details:
            # Skip user-provided credentials if already tried
            continue
            
        print(f"Trying credentials: {cred_username}:{cred_password}")
        details = extract_endpoint_details(scan_result, cred_username, cred_password)
        
        # If we got some useful information, keep it
        if details and details.get('manufacturer') != 'Unknown' or details.get('model') != 'Unknown':
            best_details = details
            print(f"Successfully extracted details using {cred_username}:{cred_password}")
            break
        else:
            print(f"Failed to extract meaningful details with {cred_username}:{cred_password}")
    
    # If no credentials worked well, use the last attempt
    if not best_details:
        best_details = details
    
    # No need to restore verbosity as we're not using urllib3.get_logger()
    
    # Format and print the detailed output
    print("\nEndpoint Details:")
    print("--------------------------------------------------")
    print(f"IP Address: {best_details.get('ip')}")
    print(f"Manufacturer: {best_details.get('manufacturer', 'Unknown')}")
    print(f"Model: {best_details.get('model', 'Unknown')}")
    print(f"Software Version: {best_details.get('sw_version', 'Unknown')}")
    
    # Print additional details if available
    if 'serial' in best_details:
        print(f"Serial Number: {best_details.get('serial')}")
    if 'mac_address' in best_details:
        print(f"MAC Address: {best_details.get('mac_address')}")
    if 'system_name' in best_details:
        print(f"System Name: {best_details.get('system_name')}")
    if 'sip_uri' in best_details:
        print(f"SIP URI: {best_details.get('sip_uri')}")
    if 'sip_status' in best_details:
        print(f"SIP Status: {best_details.get('sip_status')}")
    if 'product_type' in best_details:
        print(f"Product Type: {best_details.get('product_type')}")
    if 'ip_address' in best_details:
        print(f"IP Address (from XML): {best_details.get('ip_address')}")
    if 'gateway' in best_details:
        print(f"Gateway: {best_details.get('gateway')}")
    if 'subnet_mask' in best_details:
        print(f"Subnet Mask: {best_details.get('subnet_mask')}")
    if 'system_time' in best_details:
        print(f"System Time: {best_details.get('system_time')}")
    
    # Print camera information if available
    if 'cameras' in best_details:
        print("\nConnected Cameras:")
        for i, camera in enumerate(best_details['cameras']):
            print(f"  Camera #{i+1}:")
            print(f"    Model: {camera.get('model', 'Unknown')}")
            if 'serial_number' in camera:
                print(f"    Serial: {camera.get('serial_number')}")
            print(f"    Connected: {camera.get('connected', False)}")
    
    print("--------------------------------------------------")
    
    # Return the complete details as JSON
    print("\nComplete JSON Output:")
    print(json.dumps(best_details, indent=2))
    
    return best_details

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Scan a single endpoint and extract detailed information")
    parser.add_argument("ip", help="IP address of the endpoint to scan")
    parser.add_argument("--username", "-u", default="admin", help="Username for authentication")
    parser.add_argument("--password", "-p", default="TANDBERG", help="Password for authentication")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Scan the specified endpoint
    scan_single_endpoint(
        ip=args.ip,
        username=args.username,
        password=args.password,
        verbose=args.verbose
    )
