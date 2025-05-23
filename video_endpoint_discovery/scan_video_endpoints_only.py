#!/usr/bin/env python3
"""
Script to scan the network and only print information for devices classified as video endpoints
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

from discovery_system.discover import find_endpoints
from discovery_system.network_utils import get_local_network_range

def scan_network_for_video_endpoints(ip_range=None, username="admin", password="TANDBERG"):
    """
    Scan the network for video endpoints and only print information for devices
    classified as video endpoints
    """
    if not ip_range:
        # Auto-detect local network range
        ip_range = get_local_network_range()
        print(f"Auto-detected network range: {ip_range}")
    
    print(f"Scanning for video endpoints on {ip_range}...")
    # Find all endpoints (video and non-video)
    endpoints = find_endpoints(
        ip_range=ip_range,
        include_details=True,
        username=username,
        password=password
    )
    
    # Filter for video endpoints only
    video_endpoints = [ep for ep in endpoints if ep.get('type') == 'video_endpoint']
    
    print(f"Found {len(video_endpoints)} video endpoint(s):")
    print("--------------------------------------------------")
    
    # Print details for each video endpoint
    for i, endpoint in enumerate(video_endpoints):
        print(f"Video Endpoint #{i+1}: {endpoint.get('ip')}")
        print(f"  Manufacturer: {endpoint.get('manufacturer', 'Unknown')}")
        print(f"  Model: {endpoint.get('model', 'Unknown')}")
        print(f"  Software: {endpoint.get('sw_version', 'Unknown')}")
        
        # Print additional details if available
        if 'serial' in endpoint:
            print(f"  Serial: {endpoint.get('serial')}")
        if 'mac_address' in endpoint:
            print(f"  MAC: {endpoint.get('mac_address')}")
        if 'system_name' in endpoint:
            print(f"  System Name: {endpoint.get('system_name')}")
        if 'sip_uri' in endpoint:
            print(f"  SIP URI: {endpoint.get('sip_uri')}")
        
        print("--------------------------------------------------")
    
    return video_endpoints

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Scan for video endpoints only")
    parser.add_argument("--ip-range", "-r", help="IP range to scan (CIDR format)")
    parser.add_argument("--username", "-u", default="admin", help="Username for authentication")
    parser.add_argument("--password", "-p", default="TANDBERG", help="Password for authentication")
    parser.add_argument("--json", "-j", action="store_true", help="Output in JSON format")
    
    args = parser.parse_args()
    
    # Scan for video endpoints
    video_endpoints = scan_network_for_video_endpoints(
        ip_range=args.ip_range,
        username=args.username,
        password=args.password
    )
    
    # If JSON output is requested
    if args.json:
        print("\nJSON Output:")
        print(json.dumps(video_endpoints, indent=2))
