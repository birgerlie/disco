from discovery_system.network_utils import scan_network
from discovery_system.endpoint_details import extract_endpoint_details

def find_endpoints(ip_range=None, include_details=True, force_endpoints=None, username="admin", password="TANDBERG"):
    """
    Find video conferencing endpoints on the network
    
    Args:
        ip_range (str): CIDR notation of IP range to scan (e.g. '192.168.1.0/24')
                       If None, tries to determine the local network
        include_details (bool): Whether to include all device details or just basic info
        force_endpoints (list): List of IPs to force classify as video endpoints
        username (str): Username for authenticating with endpoints
        password (str): Password for authenticating with endpoints
    
    Returns:
        list: List of dictionaries containing video endpoint information
    """
    print("Searching for video endpoints...")
    
    # Scan the network for all devices
    all_devices = scan_network(ip_range, force_endpoints=force_endpoints, username=username, password=password)
    
    # Filter for video endpoints only
    video_endpoints = [device for device in all_devices if device.get('type') == 'video_endpoint']
    
    # Optionally simplify the output
    if not include_details:
        video_endpoints = [
            {
                'ip': device['ip'],
                'name': device['name'],
                'type': 'video_endpoint'
            } 
            for device in video_endpoints
        ]
    
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
    
    # Check if it's a video endpoint
    if basic_endpoint.get('type') == 'video_endpoint':
        # Extract detailed information using the endpoint_details module
        print(f"Extracting detailed information from endpoint at {endpoint_ip}...")
        detailed_endpoint = extract_endpoint_details(basic_endpoint, username, password)
        
        # Add status and capabilities information
        detailed_endpoint['status'] = 'online'
        detailed_endpoint['last_meeting'] = None
        detailed_endpoint['capabilities'] = ['video', 'audio']
        
        return detailed_endpoint
    
    return basic_endpoint
