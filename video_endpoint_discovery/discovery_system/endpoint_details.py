"""
Endpoint Details Extractor Module
---------------------------------
Extract manufacturer, model, make, URI, and software version from video endpoints
of different manufacturers.

This module provides an abstraction layer to handle different vendor-specific
approaches to retrieving device information.
"""

import re
import requests
import urllib3
from bs4 import BeautifulSoup

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def extract_endpoint_details(endpoint, username="admin", password="TANDBERG"):
    """
    Extract detailed information from a video endpoint.
    
    Args:
        endpoint (dict): Dictionary containing endpoint information
                        (ip, hostname, open_ports, type)
        username (str): Username for authentication
        password (str): Password for authentication
        
    Returns:
        dict: Dictionary with detailed endpoint information including:
              manufacturer, model, make, uri, sw_version, etc.
    """
    # Start with basic details and defaults
    details = {
        'ip': endpoint['ip'],
        'hostname': endpoint.get('hostname', endpoint['ip']),
        'manufacturer': 'Unknown',
        'model': 'Unknown',
        'sw_version': 'Unknown',
        'uri': get_endpoint_uri(endpoint),
        'type': endpoint.get('type', 'unknown')  # Preserve the original type
    }
    
    # Try to get the web interface content
    html_content = ""
    try:
        url = details['uri']
        print(f"DEBUG: Requesting endpoint details from {url}")
        response = requests.get(
            url, 
            auth=(username, password), 
            timeout=10,
            verify=False
        )
        
        if response.status_code == 200:
            html_content = response.text
            print(f"DEBUG: Successfully retrieved content from {url}")
        else:
            print(f"DEBUG: Failed to retrieve content from {url}, status code: {response.status_code}")
            return details
    except Exception as e:
        print(f"DEBUG: Error retrieving endpoint details: {str(e)}")
        return details
    
    # Determine manufacturer and extract details
    if "cisco" in html_content.lower() or "webex" in html_content.lower():
        print("DEBUG: Detected Cisco/Webex endpoint")
        cisco_details = parse_cisco_details(html_content)
        details.update(cisco_details)
    elif "polycom" in html_content.lower() or "realpresence" in html_content.lower():
        print("DEBUG: Detected Polycom endpoint")
        polycom_details = parse_polycom_details(html_content)
        details.update(polycom_details)
    elif "tandberg" in html_content.lower():
        print("DEBUG: Detected Tandberg endpoint")
        tandberg_details = parse_tandberg_details(html_content)
        details.update(tandberg_details)
    else:
        # Try generic parsing for unknown manufacturers
        details.update(parse_generic_details(html_content))
    
    # Update the display name to include manufacturer and model if available
    if details['manufacturer'] != 'Unknown' and details['model'] != 'Unknown':
        details['name'] = f"{details['manufacturer']} {details['model']} at {details['hostname']}"
    else:
        details['name'] = f"Device at {details['hostname']}"
    
    return details

def parse_cisco_details(html_content):
    """
    Parse HTML content from a Cisco/Webex endpoint to extract details.
    
    Args:
        html_content (str): HTML content from the endpoint
        
    Returns:
        dict: Dictionary with extracted details
    """
    details = {
        'manufacturer': 'Cisco'
    }
    
    # Parse model from title
    title_match = re.search(r'<title>(?:Cisco)?\s*(?:Webex)?\s*(.*?)</title>', html_content, re.IGNORECASE)
    if title_match:
        model = title_match.group(1).strip()
        if "webex" not in model.lower():
            model = f"Webex {model}"
        details['model'] = model
    
    # Parse software version
    sw_version_match = re.search(r'<span class="sw-version">(.*?)</span>', html_content)
    if sw_version_match:
        details['sw_version'] = sw_version_match.group(1).strip()
    else:
        # Alternative pattern
        alt_version = re.search(r'Software Version:\s*</td><td[^>]*>(.*?)</td>', html_content)
        if alt_version:
            details['sw_version'] = alt_version.group(1).strip()
    
    # Parse serial number if available
    serial_match = re.search(r'<div class="serial-number">(.*?)</div>', html_content)
    if serial_match:
        details['serial'] = serial_match.group(1).strip()
    
    # Parse MAC address if available
    mac_match = re.search(r'<div class="mac-address">(.*?)</div>', html_content)
    if mac_match:
        details['mac_address'] = mac_match.group(1).strip()
    
    return details

def parse_polycom_details(html_content):
    """
    Parse HTML content from a Polycom endpoint to extract details.
    
    Args:
        html_content (str): HTML content from the endpoint
        
    Returns:
        dict: Dictionary with extracted details
    """
    details = {
        'manufacturer': 'Polycom'
    }
    
    # Parse model from title
    title_match = re.search(r'<title>(?:Polycom)?\s*(.*?)</title>', html_content, re.IGNORECASE)
    if title_match:
        details['model'] = title_match.group(1).strip()
    
    # Parse software version
    sw_version_match = re.search(r'<div class="software-version">(.*?)</div>', html_content)
    if sw_version_match:
        details['sw_version'] = sw_version_match.group(1).strip()
    else:
        # Alternative pattern
        alt_version = re.search(r'Software:\s*</td><td[^>]*>(.*?)</td>', html_content)
        if alt_version:
            details['sw_version'] = alt_version.group(1).strip()
    
    # Parse system name if available
    name_match = re.search(r'<div class="system-name">(.*?)</div>', html_content)
    if name_match:
        details['system_name'] = name_match.group(1).strip()
    
    return details

def parse_tandberg_details(html_content):
    """
    Parse HTML content from a Tandberg endpoint to extract details.
    
    Args:
        html_content (str): HTML content from the endpoint
        
    Returns:
        dict: Dictionary with extracted details
    """
    details = {
        'manufacturer': 'TANDBERG'
    }
    
    # Parse model from title
    title_match = re.search(r'<title>(?:TANDBERG)?\s*(.*?)</title>', html_content, re.IGNORECASE)
    if title_match:
        details['model'] = title_match.group(1).strip()
    
    # Parse software version
    sw_version_match = re.search(r'<div id="sw-version">(.*?)</div>', html_content)
    if sw_version_match:
        details['sw_version'] = sw_version_match.group(1).strip()
    else:
        # Alternative pattern
        alt_version = re.search(r'Software:\s*</td><td[^>]*>(.*?)</td>', html_content)
        if alt_version:
            details['sw_version'] = alt_version.group(1).strip()
    
    # Parse product ID if available
    product_match = re.search(r'<div id="product-id">(.*?)</div>', html_content)
    if product_match:
        details['product_id'] = product_match.group(1).strip()
    
    return details

def parse_generic_details(html_content):
    """
    Parse HTML content from an unknown endpoint to extract generic details.
    Uses BeautifulSoup for more robust parsing when the manufacturer is unknown.
    
    Args:
        html_content (str): HTML content from the endpoint
        
    Returns:
        dict: Dictionary with extracted details
    """
    details = {}
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try to get manufacturer and model from title
        if soup.title:
            title = soup.title.text.strip()
            
            # Check for known manufacturer names in title
            manufacturers = ['cisco', 'polycom', 'tandberg', 'webex', 'lifesize', 'avaya', 'huawei', 'zoom']
            found_manufacturer = None
            
            for manufacturer in manufacturers:
                if manufacturer.lower() in title.lower():
                    found_manufacturer = manufacturer.capitalize()
                    if manufacturer.lower() == 'tandberg':
                        found_manufacturer = 'TANDBERG'
                    if manufacturer.lower() == 'webex':
                        found_manufacturer = 'Cisco'
                    break
            
            if found_manufacturer:
                details['manufacturer'] = found_manufacturer
                # Remove manufacturer from title to extract model
                model_pattern = re.compile(re.escape(found_manufacturer), re.IGNORECASE)
                model = model_pattern.sub('', title).strip()
                if model:
                    details['model'] = model
        
        # Look for version information in various formats
        version_elements = soup.find_all(string=re.compile(r'(version|software|firmware|sw version)', re.IGNORECASE))
        if version_elements:
            for element in version_elements:
                parent = element.parent
                if parent and parent.next_sibling:
                    version_text = parent.next_sibling.strip()
                    if version_text:
                        details['sw_version'] = version_text
                        break
    
    except Exception as e:
        print(f"DEBUG: Error parsing generic details: {str(e)}")
    
    return details

def get_endpoint_uri(endpoint):
    """
    Generate the URI for accessing the endpoint based on available ports.
    
    Args:
        endpoint (dict): Dictionary containing endpoint information
                        including IP and open ports
        
    Returns:
        str: URI for accessing the endpoint
    """
    ip = endpoint['ip']
    open_ports = endpoint.get('open_ports', [])
    
    # Prefer HTTPS (port 443) if available
    if 443 in open_ports:
        return f"https://{ip}"
    # Fall back to HTTP (port 80) if available
    elif 80 in open_ports:
        return f"http://{ip}"
    # Default to HTTP if no web ports are detected
    else:
        return f"http://{ip}"
