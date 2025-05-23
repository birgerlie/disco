"""
Test for enhanced JSON output with detailed endpoint information
"""
import pytest
import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import discovery_system
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestEnhancedOutput:
    """Test the enhanced JSON output format for endpoint details."""
    
    @patch('requests.get')
    def test_enhanced_json_output(self, mock_requests):
        """Test that the endpoint details include manufacturer, model, sip_uri, etc."""
        from discovery_system.scanner_cli import display_endpoints
        
        # Mock a Cisco endpoint with enhanced details
        endpoint = {
            'ip': '172.17.20.70',
            'hostname': '172.17.20.70',
            'open_ports': [80, 443],
            'type': 'video_endpoint',
            'manufacturer': 'Cisco',
            'model': 'Webex Room Kit',
            'sw_version': 'RoomOS 10.11.2.3',
            'serial': 'FTT234500AB',
            'mac_address': '00:11:22:33:44:55',
            'system_name': 'Conference Room A',
            'sip_uri': 'room.kit@example.com',
            'contact_info': 'IT Support (555-1234)',
            'name': 'Cisco Webex Room Kit at Conference Room A'
        }
        
        # Test JSON output format
        with patch('builtins.print') as mock_print:
            display_endpoints([endpoint], json_output=True)
            
            # Get the JSON string that was printed
            json_str = mock_print.call_args[0][0]
            json_data = json.loads(json_str)
            
            # Verify all the required fields are present
            assert len(json_data) == 1
            assert json_data[0]['ip'] == '172.17.20.70'
            assert json_data[0]['manufacturer'] == 'Cisco'
            assert json_data[0]['model'] == 'Webex Room Kit'
            assert json_data[0]['sip_uri'] == 'room.kit@example.com'
            assert json_data[0]['system_name'] == 'Conference Room A'
            assert 'Cisco Webex Room Kit' in json_data[0]['name']
