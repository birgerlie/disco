#!/usr/bin/env python3
"""
Test enhanced Cisco endpoint detection
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import xml.etree.ElementTree as ET
import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestEnhancedCiscoDetection:
    """Test the enhanced Cisco endpoint detection logic"""
    
    @patch('requests.get')
    def test_enhanced_cisco_detection(self, mock_requests):
        """Test that we can properly identify Cisco endpoints by checking the XML API"""
        from discovery_system.endpoint_details import extract_endpoint_details
        
        # Create a mock response for the HTML page
        mock_html_response = MagicMock()
        mock_html_response.status_code = 200
        mock_html_response.text = """
        <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <title>Meeting Room - Heimdall</title>
          </head>
          <body>
            <div class="container">
              <h1>Welcome to the Room</h1>
            </div>
          </body>
        </html>
        """
        
        # Create a mock response for status.xml
        mock_xml_response = MagicMock()
        mock_xml_response.status_code = 200
        mock_xml_response.text = """<?xml version="1.0"?>
<Status product="Cisco Codec" version="ce11.28.1.5.04b277ca762" apiVersion="4">
  <SystemUnit>
    <ProductId>Cisco Room Kit</ProductId>
    <ProductPlatform>Room Kit</ProductPlatform>
    <ProductType>Cisco Codec</ProductType>
    <Software>
      <DisplayName>RoomOS</DisplayName>
      <Version>11.28.1.5.04b277ca762</Version>
    </Software>
    <Hardware>
      <SerialNumber>FTT1234567890</SerialNumber>
      <MACAddress>AA:BB:CC:DD:EE:FF</MACAddress>
    </Hardware>
  </SystemUnit>
</Status>"""
        
        # Set up the mock to return different responses based on the URL
        def mock_get_response(url, **kwargs):
            if "status.xml" in url:
                return mock_xml_response
            else:
                return mock_html_response
            
        mock_requests.side_effect = mock_get_response
        
        # Create a test endpoint
        endpoint = {
            'ip': '172.17.41.19',
            'hostname': '172.17.41.19',
            'type': 'video_endpoint',
            'open_ports': [443]
        }
        
        # Call the function
        details = extract_endpoint_details(endpoint, "admin", "TANDBERG")
        
        # Verify that the function correctly identifies the endpoint as Cisco
        assert details['manufacturer'] == 'Cisco'
        assert details['model'] == 'Room Kit'
        assert 'sw_version' in details
        assert 'mac_address' in details
        
if __name__ == "__main__":
    pytest.main(["-v", __file__])
