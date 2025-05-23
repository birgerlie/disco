"""
Test for enhanced XML parsing and more detailed JSON output
"""
import pytest
import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import discovery_system
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestEnhancedXmlParsing:
    """Test the enhanced XML parsing to extract more detailed information."""
    
    @patch('requests.get')
    def test_enhanced_status_xml_parsing(self, mock_requests):
        """Test that we can extract more detailed information from status.xml."""
        from discovery_system.endpoint_details import access_cisco_xml_api
        
        # Load a real status.xml sample
        status_xml = """<?xml version="1.0"?>
<Status product="Cisco Codec" version="ce11.28.1.5.04b277ca762" apiVersion="4">
  <Audio>
    <Devices>
      <HandsetUSB>
        <ConnectionStatus>NotConnected</ConnectionStatus>
      </HandsetUSB>
    </Devices>
  </Audio>
  <Cameras>
    <Camera item="1">
      <Connected>True</Connected>
      <Model>Cisco Webex Quad Camera</Model>
      <SerialNumber>1234567890</SerialNumber>
    </Camera>
  </Cameras>
  <Network>
    <CDP>
      <DeviceId>switch123</DeviceId>
    </CDP>
    <Ethernet>
      <MacAddress>AA:BB:CC:DD:EE:FF</MacAddress>
    </Ethernet>
    <IPv4>
      <Address>172.17.41.19</Address>
      <Gateway>172.17.41.1</Gateway>
      <SubnetMask>255.255.255.0</SubnetMask>
    </IPv4>
    <DNS>
      <Domain>example.com</Domain>
      <Server item="1">
        <Address>8.8.8.8</Address>
      </Server>
    </DNS>
  </Network>
  <SystemUnit>
    <ProductId>Cisco Webex Room Kit</ProductId>
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
    <State>
      <NumberOfActiveCalls>0</NumberOfActiveCalls>
      <NumberOfInProgressCalls>0</NumberOfInProgressCalls>
      <NumberOfSuspendedCalls>0</NumberOfSuspendedCalls>
    </State>
  </SystemUnit>
  <Time>
    <SystemTime>2025-05-23T14:06:49Z</SystemTime>
  </Time>
  <SIP>
    <Registration item="1">
      <Status>Registered</Status>
      <URI>room.kit@example.com</URI>
    </Registration>
  </SIP>
</Status>"""
        
        # Mock the requests.get response for status.xml
        mock_status_response = MagicMock()
        mock_status_response.status_code = 200
        mock_status_response.text = status_xml
        
        # Mock the requests.get response for config.xml (failure or empty response)
        mock_config_response = MagicMock()
        mock_config_response.status_code = 401  # Unauthorized
        
        # Set up the mock to return our mock responses
        def mock_get_response(url, **kwargs):
            if "status.xml" in url:
                return mock_status_response
            else:
                return mock_config_response
        
        mock_requests.side_effect = mock_get_response
        
        # Define the endpoint data
        endpoint = {
            'ip': '172.17.41.19',
            'hostname': '172.17.41.19',
            'type': 'video_endpoint',
            'open_ports': [443]
        }
        
        # Call the access_cisco_xml_api function
        details = access_cisco_xml_api(endpoint, "admin", "TANDBERG")
        
        # Verify that the function extracted enhanced data
        assert details is not None
        assert details['manufacturer'] == 'Cisco'
        assert details['model'] == 'Webex Room Kit'
        assert details['sw_version'] == 'RoomOS 11.28.1.5.04b277ca762'
        assert details['serial'] == 'FTT1234567890'
        assert details['mac_address'] == 'AA:BB:CC:DD:EE:FF'
        assert details['product_type'] == 'Cisco Codec'
        
        # Enhanced data that should be extracted
        assert 'ip_address' in details
        assert details['ip_address'] == '172.17.41.19'
        assert 'subnet_mask' in details
        assert details['subnet_mask'] == '255.255.255.0'
        assert 'gateway' in details
        assert details['gateway'] == '172.17.41.1'
        assert 'sip_status' in details
        assert details['sip_status'] == 'Registered'
        assert 'sip_uri' in details
        assert details['sip_uri'] == 'room.kit@example.com'
        assert 'system_time' in details
        assert details['system_time'] == '2025-05-23T14:06:49Z'
        assert 'cameras' in details
        assert isinstance(details['cameras'], list)
        assert len(details['cameras']) > 0
        assert details['cameras'][0]['model'] == 'Cisco Webex Quad Camera'
