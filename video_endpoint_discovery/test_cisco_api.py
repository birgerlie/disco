#!/usr/bin/env python3
"""
Test script for Cisco endpoint details extraction
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

# Add the parent directory to the path
parent_dir = str(Path(__file__).parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from discovery_system.endpoint_details import extract_endpoint_details, access_cisco_xml_api

def test_cisco_api_integration():
    """Test the integration of Cisco XML API into endpoint details extraction"""
    
    with patch('requests.get') as mock_requests:
        # Mock successful HTML response
        mock_html_response = MagicMock()
        mock_html_response.status_code = 200
        mock_html_response.text = """
        <html>
        <head><title>Cisco Webex Room Kit</title></head>
        <body>
            <div class="product-name">Cisco Webex Room Kit</div>
            <div class="sw-info">RoomOS 10.11.2.3</div>
            <div class="hw-info">
                <span>Serial: FTT234500AB</span>
                <span>MAC: 00:11:22:33:44:55</span>
            </div>
        </body>
        </html>
        """
        
        # Mock successful status.xml response
        mock_status_response = MagicMock()
        mock_status_response.status_code = 200
        mock_status_response.text = """<?xml version="1.0"?>
<Status>
  <SystemUnit>
    <ProductId>Cisco Webex Room Kit</ProductId>
    <ProductPlatform>Room Kit</ProductPlatform>
    <ProductType>Cisco Codec</ProductType>
    <Software>
      <DisplayName>RoomOS</DisplayName>
      <Version>10.11.2.3</Version>
    </Software>
    <Hardware>
      <SerialNumber>FTT234500AB</SerialNumber>
      <MACAddress>00:11:22:33:44:55</MACAddress>
    </Hardware>
  </SystemUnit>
  <Network>
    <IPv4>
      <Address>192.168.1.100</Address>
    </IPv4>
    <DNS>
      <Domain>example.com</Domain>
    </DNS>
  </Network>
</Status>"""
        
        # Mock successful config.xml response
        mock_config_response = MagicMock()
        mock_config_response.status_code = 200
        mock_config_response.text = """<?xml version="1.0"?>
<Configuration>
  <SystemUnit>
    <Name>Conference Room A</Name>
    <ContactInfo>
      <Name>IT Support</Name>
      <ContactNumber>555-1234</ContactNumber>
    </ContactInfo>
  </SystemUnit>
  <SIP>
    <URI>room.kit@example.com</URI>
  </SIP>
</Configuration>"""
        
        # Set up the mock to return our mock responses
        def mock_get_response(url, **kwargs):
            print(f"Mock request to: {url}")
            if "status.xml" in url:
                return mock_status_response
            elif "config.xml" in url:
                return mock_config_response
            else:
                return mock_html_response
        
        mock_requests.side_effect = mock_get_response
        
        # Define a simulated endpoint
        endpoint = {
            'ip': '192.168.1.100',
            'hostname': 'roomkit.example.com',
            'type': 'video_endpoint',
            'open_ports': [80, 443]
        }
        
        # Call the extract_endpoint_details function to test XML API integration
        details = extract_endpoint_details(endpoint, "admin", "TANDBERG")
        
        # Print the resulting details
        print("\nExtracted Endpoint Details:")
        print(json.dumps(details, indent=2))
        
        # Verify key information was retrieved from the XML API
        assert details['manufacturer'] == 'Cisco'
        assert details['model'] == 'Webex Room Kit'
        assert details['sw_version'] == 'RoomOS 10.11.2.3'
        assert details['serial'] == 'FTT234500AB'
        assert details['mac_address'] == '00:11:22:33:44:55'
        assert details['system_name'] == 'Conference Room A'
        assert details['sip_uri'] == 'room.kit@example.com'
        assert details['contact_info'] == 'IT Support (555-1234)'
        
        print("\nTest passed! XML API integration is working correctly.")

if __name__ == "__main__":
    test_cisco_api_integration()
