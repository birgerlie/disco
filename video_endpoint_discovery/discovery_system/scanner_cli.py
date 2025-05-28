#!/usr/bin/env python3
"""
Video Endpoint Scanner CLI
--------------------------
Command-line tool to scan the local network for video conferencing endpoints.
"""

import argparse
import json
import sys
import os
from pathlib import Path

# Add parent directory to path if running as a script
if __name__ == "__main__":
    parent_dir = str(Path(__file__).parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

# Import the necessary functions
from discovery_system.discover import find_endpoints
from discovery_system.network_utils import get_local_network_range


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Scan for video conferencing endpoints on the network"
    )
    parser.add_argument(
        "--range", 
        dest="ip_range", 
        help="IP range to scan in CIDR notation (e.g., 192.168.1.0/24)"
    )
    parser.add_argument(
        "--json", 
        action="store_true", 
        help="Output results in JSON format"
    )
    parser.add_argument(
        "--simple", 
        action="store_true", 
        help="Show simplified output (less detail)"
    )
    parser.add_argument(
        "--force-endpoint",
        dest="force_endpoints",
        action="append",
        help="Force specific IP to be classified as a video endpoint (can be used multiple times)"
    )
    # Removed --optimized flag as all scans now use the optimized approach by default
    parser.add_argument(
        "--username",
        dest="username",
        help="Username for authenticating with endpoints (default: admin)"
    )
    parser.add_argument(
        "--password",
        dest="password",
        help="Password for authenticating with endpoints (default: TANDBERG)"
    )
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Set default values for username and password if not provided
    if args.username is None:
        args.username = "admin"
    if args.password is None:
        args.password = "TANDBERG"
        
    return args


def display_endpoints(endpoints, json_output=False):
    """Display the found endpoints in the specified format"""
    if not endpoints:
        print("No video endpoints found on the network.")
        return
    
    if json_output:
        # Output only the JSON data with no other text
        print(json.dumps(endpoints, indent=2))
    else:
        # Output in human-readable format
        print(f"Found {len(endpoints)} video endpoint(s):")
        print("-" * 50)
        
        for i, endpoint in enumerate(endpoints, 1):
            print(f"Endpoint {i}:")
            print(f"  Name: {endpoint['name']}")
            print(f"  IP: {endpoint['ip']}")
            
            if 'hostname' in endpoint:
                print(f"  Hostname: {endpoint['hostname']}")
                
            if 'open_ports' in endpoint:
                print(f"  Open Ports: {', '.join(map(str, endpoint['open_ports']))}")
                
            if 'model' in endpoint:
                print(f"  Model: {endpoint['model']}")
                
            if 'status' in endpoint:
                print(f"  Status: {endpoint['status']}")
                
            if 'capabilities' in endpoint:
                print(f"  Capabilities: {', '.join(endpoint['capabilities'])}")
                
            print("-" * 50)


def main():
    """Main entry point for the scanner CLI"""
    args = parse_arguments()
    
    # If no IP range specified, auto-detect the local network range
    ip_range = args.ip_range
    if not ip_range:
        ip_range = get_local_network_range()
        print(f"Auto-detected network range: {ip_range}")
        
    # All scans now use the optimized approach by default
    print("Using two-phase scanning (checking SIP ports first for better performance)")

    
    # Scan for endpoints
    print(f"Scanning for video endpoints on {ip_range}...")
    
    # For testing compatibility, we need to make sure we're using the correct import
    # This allows our mock patches to work correctly
    import discovery_system.discover
    endpoints = discovery_system.discover.find_endpoints(
        ip_range=ip_range, 
        include_details=not args.simple,
        force_endpoints=args.force_endpoints,
        username=args.username,
        password=args.password
    )
    
    # Display results
    display_endpoints(endpoints, json_output=args.json)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
