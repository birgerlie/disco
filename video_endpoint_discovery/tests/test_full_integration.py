import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

# Add the parent directory to the path so we can import discovery_system
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestFullIntegration:
    """Test the full integration of the endpoint discovery system."""
    
    @patch('discovery_system.endpoint_details.requests.get')
    def test_cisco_endpoint_full_extraction(self, mock_requests):
        """Test the full extraction flow for a Cisco endpoint."""
        from discovery_system.endpoint_details import extract_endpoint_details
        
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
      <Address>172.17.20.72</Address>
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
            if "status.xml" in url:
                return mock_status_response
            elif "config.xml" in url:
                return mock_config_response
            else:
                return mock_html_response
        
        mock_requests.side_effect = mock_get_response
        
        # Define the endpoint data
        endpoint = {
            'ip': '172.17.20.72',
            'hostname': '172.17.20.72',
            'type': 'video_endpoint',
            'open_ports': [80, 443]
        }
        
        # Call the extract_endpoint_details function
        details = extract_endpoint_details(endpoint, "admin", "TANDBERG")
        
        # Verify that the function extracted the correct data
        assert details is not None
        assert details['manufacturer'] == 'Cisco'
        assert details['model'] == 'Webex Room Kit'
        assert details['sw_version'] == 'RoomOS 10.11.2.3'
        assert details['serial'] == 'FTT234500AB'
        assert details['mac_address'] == '00:11:22:33:44:55'
        assert details['system_name'] == 'Conference Room A'
        assert details['sip_uri'] == 'room.kit@example.com'
        assert details['contact_info'] == 'IT Support (555-1234)'
