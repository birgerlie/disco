from discovery_system.network_utils import scan_network
from discovery_system.endpoint_details import extract_endpoint_details
from discovery_system.endpoint_classification import classify_endpoints

def find_endpoints(ip_range=None, include_details=True, force_endpoints=None, username="admin", password="TANDBERG", num_workers=4):
    """
    Find video conferencing endpoints on the network
    
    Args:
        ip_range (str): CIDR notation of IP range to scan (e.g. '192.168.1.0/24')
                       If None, tries to determine the local network
        include_details (bool): Whether to include all device details or just basic info
        force_endpoints (list): List of IPs to force classify as video endpoints
        username (str): Username for authenticating with endpoints
        password (str): Password for authenticating with endpoints
        num_workers (int): Number of worker threads to use for classification
    
    Returns:
        list: List of dictionaries containing video endpoint information
    """
    print("Searching for video endpoints...")
    
    # Scan the network for all devices
    all_devices = scan_network(ip_range, force_endpoints=force_endpoints, username=username, password=password)
    
    # Filter for video endpoints only
    video_endpoints = [device for device in all_devices if device.get('type') == 'video_endpoint']
    
    if video_endpoints:
        print(f"Found {len(video_endpoints)} potential video endpoints, classifying...")
        
        # If details are requested, classify the endpoints using worker threads
        if include_details:
            print(f"Using {num_workers} worker threads for classification")
            video_endpoints = classify_endpoints(
                endpoints=video_endpoints,
                num_workers=num_workers,
                username=username,
                password=password
            )
        # Otherwise, simplify the output
        else:
            video_endpoints = [
                {
                    'ip': device['ip'],
                    'name': device['name'],
                    'type': 'video_endpoint'
                } 
                for device in video_endpoints
            ]
    else:
        print("No video endpoints found")
    
    return video_endpoints

def get_endpoint_details(endpoint_ip, username="admin", password="TANDBERG"):
    """
    Get detailed information about a specific endpoint
    
    Args:
        endpoint_ip (str): IP address of the endpoint to query
        username (str): Username for authenticating with the endpoint
        password (str): Password for authenticating with the endpoint
    
    Returns:
        dict: Detailed information about the endpoint, or None if not found
    """
    # First scan to detect the endpoint
    all_devices = scan_network(f"{endpoint_ip}/32", username=username, password=password)
    
    if not all_devices:
        return None
        
    basic_endpoint = all_devices[0]
    
    # Always try to extract detailed information for Cisco endpoints
    # This addresses the issue where some Cisco endpoints weren't being properly identified
    # and therefore not having their model extracted through the XML API
    if basic_endpoint.get('type') == 'video_endpoint' or (basic_endpoint.get('open_ports') and 443 in basic_endpoint.get('open_ports')):
        # If it has port 443 open, it might be a Cisco endpoint even if not classified as video_endpoint
        # Ensure it's marked as a video endpoint for proper extraction
        if basic_endpoint.get('type') != 'video_endpoint':
            print(f"Reclassifying endpoint at {endpoint_ip} as video_endpoint (has port 443 open)")
            basic_endpoint['type'] = 'video_endpoint'
            
        # Use the classification system to get detailed information
        print(f"Extracting detailed information from endpoint at {endpoint_ip}...")
        # Create a list with just this endpoint
        endpoints_to_classify = [basic_endpoint]
        
        # Use the classify_endpoints function with a single worker
        classified_endpoints = classify_endpoints(
            endpoints=endpoints_to_classify,
            num_workers=1,
            username=username,
            password=password
        )
        
        # If classification succeeded, return the first (and only) endpoint
        if classified_endpoints:
            return classified_endpoints[0]
        
        # Fallback to direct extraction if classification failed
        detailed_endpoint = extract_endpoint_details(basic_endpoint, username, password)
        
        # Add status and capabilities information
        detailed_endpoint['status'] = 'online'
        detailed_endpoint['last_meeting'] = None
        detailed_endpoint['capabilities'] = ['video', 'audio']
        
        return detailed_endpoint
    
    return basic_endpoint
