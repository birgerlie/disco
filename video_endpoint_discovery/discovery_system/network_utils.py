import socket
import ipaddress
import concurrent.futures
import requests
import urllib3

# Disable SSL warnings - in a production environment, proper certificate handling would be implemented
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time

# Try to import netifaces, but provide fallback if not available
try:
    import netifaces
    HAVE_NETIFACES = True
except ImportError:
    HAVE_NETIFACES = False
    print("Warning: netifaces module not available. Using fallback method for network detection.")
    print("For better network detection, install netifaces: pip install netifaces")

# Common ports used by video conferencing endpoints
VIDEO_ENDPOINT_PORTS = [80, 443, 5060, 5061, 1720]  # HTTP, HTTPS, SIP, H.323


def get_local_network_range():
    """
    Automatically detect the network range of the computer
    
    Returns:
        str: CIDR notation of local network (e.g., '192.168.1.0/24')
    """
    # If netifaces is available, use it for better network detection
    if HAVE_NETIFACES:
        interfaces = netifaces.interfaces()
        
        # Filter for active interfaces with IPv4 addresses (exclude loopback)
        for interface in interfaces:
            addrs = netifaces.ifaddresses(interface)
            # Check if interface has IPv4 address
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    # Skip loopback addresses
                    if not ip.startswith('127.'):
                        # Get netmask if available
                        if 'netmask' in addr:
                            netmask = addr['netmask']
                            # Convert IP and netmask to CIDR format
                            ip_interface = ipaddress.IPv4Interface(f"{ip}/{netmask}")
                            network = ip_interface.network
                            return str(network)
    
    # Fallback method if netifaces is not available or no suitable interface found
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This doesn't need to be a valid or reachable address
        # It's just to get the socket to associate with an interface
        s.connect(('10.255.255.255', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        # If that fails, fall back to localhost
        local_ip = '127.0.0.1'
    finally:
        s.close()
    
    # Assume a /24 network (common for home/office networks)
    # In a real-world application, you might want to make this configurable
    ip_parts = local_ip.split('.')
    return f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"

def scan_ip(ip, ports=VIDEO_ENDPOINT_PORTS, timeout=0.5, force_endpoint=False, username="admin", password="TANDBERG"):
    """
    Scan a single IP address for open ports that might indicate a video endpoint
    
    Args:
        ip (str): IP address to scan
        ports (list): List of ports to check
        timeout (float): Socket timeout in seconds
        force_endpoint (bool): Force classification as video endpoint (for testing)
    
    Returns:
        dict or None: Device info if detected, None otherwise
    """
    print(f"DEBUG: Scanning IP: {ip}")
    open_ports = []
    
    for port in ports:
        try:
            print(f"DEBUG: Checking {ip}:{port}")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            if result == 0:
                print(f"DEBUG: Found open port at {ip}:{port}")
                open_ports.append(port)
            sock.close()
        except Exception as e:
            print(f"DEBUG: Error scanning {ip}:{port} - {str(e)}")
    
    # If we found open ports that match video endpoint patterns
    if open_ports:
        print(f"DEBUG: Found open ports on {ip}: {open_ports}")
        # Try to get hostname
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            print(f"DEBUG: Resolved hostname for {ip}: {hostname}")
        except Exception as e:
            print(f"DEBUG: Could not resolve hostname for {ip} - {str(e)}")
            hostname = ip
            
        # Basic heuristic to identify video endpoints
        # In a real implementation, this would be more sophisticated
        # For example, probing HTTP ports for device information
        device_type = 'unknown'
        
        # Check for video endpoint based on common ports
        is_video_endpoint = False
        
        # SIP/H.323 ports are strong indicators of video endpoints
        if 5060 in open_ports or 5061 in open_ports or 1720 in open_ports:
            is_video_endpoint = True
        
        # HTTP/HTTPS ports with specific patterns can indicate Cisco endpoints
        if (80 in open_ports or 443 in open_ports):
            # Try to connect to the endpoint using the provided credentials
            print(f"DEBUG: Checking if {ip} might be a video endpoint using credentials {username}:****")
            
            # Try HTTP first
            if 80 in open_ports:
                try:
                    url = f"http://{ip}"
                    print(f"DEBUG: Attempting HTTP connection to {url} with credentials")
                    response = requests.get(url, auth=(username, password), timeout=5, verify=False)
                    
                    if response.status_code == 200:
                        print(f"DEBUG: Successfully authenticated with {ip} via HTTP")
                        # Check response content for signs of a video endpoint
                        if any(x in response.text.lower() for x in ['cisco', 'polycom', 'tandberg', 'webex', 'room', 'codec']):
                            print(f"DEBUG: HTTP content suggests a video endpoint")
                            is_video_endpoint = True
                except Exception as e:
                    print(f"DEBUG: HTTP connection to {ip} failed: {str(e)}")
            
            # Try HTTPS if HTTP didn't succeed
            if 443 in open_ports and not is_video_endpoint:
                try:
                    url = f"https://{ip}"
                    print(f"DEBUG: Attempting HTTPS connection to {url} with credentials")
                    response = requests.get(url, auth=(username, password), timeout=5, verify=False)
                    
                    if response.status_code == 200:
                        print(f"DEBUG: Successfully authenticated with {ip} via HTTPS")
                        # Check response content for signs of a video endpoint
                        if any(x in response.text.lower() for x in ['cisco', 'polycom', 'tandberg', 'webex', 'room', 'codec']):
                            print(f"DEBUG: HTTPS content suggests a video endpoint")
                            is_video_endpoint = True
                except Exception as e:
                    print(f"DEBUG: HTTPS connection to {ip} failed: {str(e)}")
                    
            # If we still haven't identified an endpoint, check hostname as a fallback
            if not is_video_endpoint:
                try:
                    # Check if hostname contains known video endpoint keywords
                    if any(x in hostname.lower() for x in ['cisco', 'polycom', 'tandberg', 'webex', 'room', 'meeting', 'codec']):
                        print(f"DEBUG: Hostname {hostname} suggests a video endpoint")
                        is_video_endpoint = True
                except Exception as e:
                    print(f"DEBUG: Hostname check failed: {str(e)}")
        
        # Force classification if requested (for testing)
        if force_endpoint:
            print(f"DEBUG: Forcing classification of {ip} as video endpoint")
            is_video_endpoint = True
            
        if is_video_endpoint:
            device_type = 'video_endpoint'
            # In production code, we would do banner grabbing or other 
            # techniques to confirm device type
        
        return {
            'ip': ip,
            'hostname': hostname,
            'open_ports': open_ports,
            'type': device_type,
            'name': f'Device at {hostname}'
        }
    
    return None

def scan_network(ip_range=None, max_workers=20, force_endpoints=None, username="admin", password="TANDBERG"):
    """
    Scan the local network for devices, with focus on video endpoints
    
    Args:
        ip_range (str): CIDR notation of IP range to scan (e.g. '192.168.1.0/24')
                       If None, tries to determine the local network
        max_workers (int): Maximum number of concurrent scanning threads
        force_endpoints (list): List of IPs to force classify as video endpoints
    
    Returns:
        list: List of dictionaries containing device information
    """
    """
    Scan the local network for devices, with focus on video endpoints
    
    Args:
        ip_range (str): CIDR notation of IP range to scan (e.g. '192.168.1.0/24')
                       If None, tries to determine the local network
        max_workers (int): Maximum number of concurrent scanning threads
    
    Returns:
        list: List of dictionaries containing device information
    """
    print("Scanning network...")
    
    print(f"DEBUG: Scanning IP range: {ip_range}")
    print(f"DEBUG: Using {max_workers} worker threads")

    # If no IP range specified, try to determine local network
    if not ip_range:
        print("DEBUG: No IP range specified, attempting to determine local network")
        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Doesn't need to be reachable
            s.connect(('10.255.255.255', 1))
            local_ip = s.getsockname()[0]
            print(f"DEBUG: Detected local IP: {local_ip}")
        except Exception as e:
            print(f"DEBUG: Error detecting local IP - {str(e)}")
            local_ip = '127.0.0.1'
            print("DEBUG: Falling back to localhost (127.0.0.1)")
        finally:
            s.close()
        
        # Assume a /24 network
        ip_parts = local_ip.split('.')
        ip_range = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
        print(f"DEBUG: Determined network range: {ip_range}")
    
    # Parse the IP range
    try:
        network = ipaddress.ip_network(ip_range, strict=False)
        print(f"DEBUG: Successfully parsed network: {network}")
        host_count = sum(1 for _ in network.hosts())
        print(f"DEBUG: Network contains {host_count} host addresses to scan")
    except ValueError as e:
        print(f"Invalid IP range: {ip_range} - {str(e)}")
        return []
    
    # Handle force_endpoints parameter
    if force_endpoints is None:
        force_endpoints = []
    else:
        print(f"DEBUG: Will force classify these IPs as endpoints: {force_endpoints}")
        
    # Log credentials being used (masking password)
    print(f"DEBUG: Using credentials - Username: {username}, Password: {'*' * len(password)}")
    
    # Scan the network with a thread pool for efficiency
    devices = []
    print(f"DEBUG: Starting network scan with {max_workers} concurrent workers")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        print("DEBUG: Creating scan tasks...")
        future_to_ip = {executor.submit(
            scan_ip, 
            str(ip), 
            force_endpoint=str(ip) in force_endpoints,
            username=username,
            password=password
        ): ip for ip in network.hosts()}
        print(f"DEBUG: Submitted {len(future_to_ip)} scan tasks")
        completed = 0
        for future in concurrent.futures.as_completed(future_to_ip):
            ip = future_to_ip[future]
            completed += 1
            if completed % 10 == 0:
                print(f"DEBUG: Progress: {completed}/{len(future_to_ip)} IPs scanned ({completed/len(future_to_ip)*100:.1f}%)")
            try:
                result = future.result()
                if result:
                    print(f"DEBUG: Found device at {ip}")
                    devices.append(result)
            except Exception as e:
                print(f"DEBUG: Error processing scan result for {ip} - {str(e)}")
    
    return devices

