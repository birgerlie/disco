import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import re
import json

# Add the parent directory to the path so we can import discovery_system
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestCiscoXmlApi:
    """Tests for accessing and parsing Cisco endpoint XML API files (config.xml and status.xml)."""
    
    @patch('requests.get')
    def test_access_cisco_status_xml(self, mock_requests):
        """Test accessing and parsing status.xml from a Cisco endpoint."""
        from discovery_system.endpoint_details import access_cisco_xml_api
        
        # Mock successful response for status.xml
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
        
        # Set up the mock to return our mock response
        mock_requests.side_effect = lambda url, **kwargs: (
            mock_status_response if "status.xml" in url else MagicMock(status_code=404)
        )
        
        # Call the function to test
        endpoint = {
            'ip': '172.17.20.72',
            'hostname': '172.17.20.72',
            'type': 'video_endpoint',
            'open_ports': [80, 443]
        }
        
        result = access_cisco_xml_api(endpoint, "admin", "TANDBERG")
        
        # Verify that the function extracted the correct data
        assert result is not None
        assert result['manufacturer'] == 'Cisco'
        assert result['model'] == 'Webex Room Kit'
        assert result['sw_version'] == 'RoomOS 10.11.2.3'
        assert result['serial'] == 'FTT234500AB'
        assert result['mac_address'] == '00:11:22:33:44:55'
        assert result['product_type'] == 'Cisco Codec'
    
    @patch('requests.get')
    def test_access_cisco_config_xml(self, mock_requests):
        """Test accessing and parsing config.xml from a Cisco endpoint."""
        from discovery_system.endpoint_details import access_cisco_xml_api
        
        # Mock successful response for config.xml
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
  <Network>
    <DNS>
      <Domain>example.com</Domain>
      <Server>
        <Address>8.8.8.8</Address>
      </Server>
    </DNS>
  </Network>
  <SIP>
    <URI>room.kit@example.com</URI>
  </SIP>
</Configuration>"""
        
        # Mock 404 for status.xml to ensure we test config.xml parsing
        mock_status_response = MagicMock()
        mock_status_response.status_code = 404
        
        # Set up the mock to return our mock responses
        def mock_get_response(url, **kwargs):
            if "config.xml" in url:
                return mock_config_response
            elif "status.xml" in url:
                return mock_status_response
            else:
                return MagicMock(status_code=404)
        
        mock_requests.side_effect = mock_get_response
        
        # Call the function to test
        endpoint = {
            'ip': '172.17.20.72',
            'hostname': '172.17.20.72',
            'type': 'video_endpoint',
            'open_ports': [80, 443]
        }
        
        result = access_cisco_xml_api(endpoint, "admin", "TANDBERG")
        
        # Verify that the function extracted the correct data
        assert result is not None
        assert result['system_name'] == 'Conference Room A'
        assert result['sip_uri'] == 'room.kit@example.com'
        assert result['contact_info'] == 'IT Support (555-1234)'
    
    @patch('requests.get')
    def test_access_cisco_both_xml_files(self, mock_requests):
        """Test accessing and parsing both status.xml and config.xml."""
        from discovery_system.endpoint_details import access_cisco_xml_api
        
        # Mock successful responses for both XML files
        mock_status_response = MagicMock()
        mock_status_response.status_code = 200
        mock_status_response.text = """<?xml version="1.0"?>
<Status>
  <SystemUnit>
    <ProductId>Cisco Webex Desk Pro</ProductId>
    <ProductPlatform>Desk Pro</ProductPlatform>
    <ProductType>Cisco Codec</ProductType>
    <Software>
      <DisplayName>RoomOS</DisplayName>
      <Version>11.0.1.4</Version>
    </Software>
    <Hardware>
      <SerialNumber>FTT987654ZY</SerialNumber>
      <MACAddress>AA:BB:CC:DD:EE:FF</MACAddress>
    </Hardware>
  </SystemUnit>
</Status>"""
        
        mock_config_response = MagicMock()
        mock_config_response.status_code = 200
        mock_config_response.text = """<?xml version="1.0"?>
<Configuration>
  <SystemUnit>
    <Name>Executive Office</Name>
  </SystemUnit>
  <SIP>
    <URI>desk.pro@example.com</URI>
  </SIP>
</Configuration>"""
        
        # Set up the mock to return our mock responses
        def mock_get_response(url, **kwargs):
            if "config.xml" in url:
                return mock_config_response
            elif "status.xml" in url:
                return mock_status_response
            else:
                return MagicMock(status_code=404)
        
        mock_requests.side_effect = mock_get_response
        
        # Call the function to test
        endpoint = {
            'ip': '172.17.20.72',
            'hostname': '172.17.20.72',
            'type': 'video_endpoint',
            'open_ports': [80, 443]
        }
        
        result = access_cisco_xml_api(endpoint, "admin", "TANDBERG")
        
        # Verify that the function extracted the correct data from both files
        assert result is not None
        assert result['manufacturer'] == 'Cisco'
        assert result['model'] == 'Webex Desk Pro'
        assert result['sw_version'] == 'RoomOS 11.0.1.4'
        assert result['serial'] == 'FTT987654ZY'
        assert result['mac_address'] == 'AA:BB:CC:DD:EE:FF'
        assert result['system_name'] == 'Executive Office'
        assert result['sip_uri'] == 'desk.pro@example.com'
