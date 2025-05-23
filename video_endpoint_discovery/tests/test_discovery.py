import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import discovery_system
sys.path.insert(0, str(Path(__file__).parent.parent))

from discovery_system.discover import find_endpoints, get_endpoint_details
from discovery_system.network_utils import scan_network


class TestEndpointDiscovery:
    def test_find_endpoints_returns_list(self):
        """Test that find_endpoints returns a list"""
        result = find_endpoints()
        assert isinstance(result, list)
    
    @patch('discovery_system.discover.scan_network')
    def test_find_endpoints_uses_network_scan(self, mock_scan):
        """Test that find_endpoints calls scan_network"""
        mock_scan.return_value = []
        find_endpoints()
        mock_scan.assert_called_once()
    
    @patch('discovery_system.discover.scan_network')
    def test_find_endpoints_filters_video_endpoints(self, mock_scan):
        """Test that find_endpoints filters video endpoints from scan results"""
        # Mock network scan returning various devices
        mock_scan.return_value = [
            {'ip': '192.168.1.10', 'type': 'video_endpoint', 'name': 'Meeting Room 1'},
            {'ip': '192.168.1.11', 'type': 'printer'},
            {'ip': '192.168.1.12', 'type': 'video_endpoint', 'name': 'Meeting Room 2'},
            {'ip': '192.168.1.13', 'type': 'computer'}
        ]
        
        result = find_endpoints()
        
        # Should only return the video endpoints
        assert len(result) == 2
        assert result[0]['name'] == 'Meeting Room 1'
        assert result[1]['name'] == 'Meeting Room 2'
    
    @patch('discovery_system.discover.scan_network')
    def test_find_endpoints_simplified_output(self, mock_scan):
        """Test that find_endpoints can return simplified results"""
        mock_scan.return_value = [
            {
                'ip': '192.168.1.10', 
                'type': 'video_endpoint', 
                'name': 'Meeting Room 1',
                'hostname': 'meetingroom1.local',
                'open_ports': [80, 443, 5060]
            }
        ]
        
        # Test with simplified output
        result = find_endpoints(include_details=False)
        
        assert len(result) == 1
        assert result[0].keys() == {'ip', 'name', 'type'}
        assert 'open_ports' not in result[0]
        assert 'hostname' not in result[0]
    
    @patch('discovery_system.discover.scan_network')
    def test_get_endpoint_details_returns_details(self, mock_scan):
        """Test that get_endpoint_details returns endpoint details"""
        # Mock a successful scan result
        endpoint_ip = '192.168.1.10'
        mock_scan.return_value = [
            {
                'ip': endpoint_ip,
                'type': 'video_endpoint',
                'name': 'Meeting Room 1',
                'hostname': 'meetingroom1.local',
                'open_ports': [80, 443, 5060]
            }
        ]
        
        result = get_endpoint_details(endpoint_ip)
        
        assert result is not None
        assert result['ip'] == endpoint_ip
        assert result['type'] == 'video_endpoint'
        assert 'model' in result
        assert 'status' in result
        assert 'capabilities' in result
    
    @patch('discovery_system.discover.scan_network')
    def test_get_endpoint_details_not_found(self, mock_scan):
        """Test that get_endpoint_details returns None when endpoint not found"""
        # Mock an empty scan result
        mock_scan.return_value = []
        
        result = get_endpoint_details('192.168.1.99')
        
        assert result is None


class TestNetworkUtils:
    def test_scan_network_returns_list(self):
        """Test that scan_network returns a list"""
        result = scan_network()
        assert isinstance(result, list)
    
    @patch('socket.socket')
    def test_scan_network_checks_common_ports(self, mock_socket):
        """Test that scan_network checks common video endpoint ports"""
        # This is a placeholder that would be expanded in a real implementation
        # For now, we're just verifying that our test infrastructure is working
        mock_instance = mock_socket.return_value
        mock_instance.connect_ex.return_value = 0  # Simulate open port
        
        # Verify the scan_network function doesn't crash
        # In a real test, we'd verify that it probes the expected ports
        result = scan_network('127.0.0.1/32')
        assert isinstance(result, list)
        
    @patch('socket.socket')
    @patch('requests.get')
    def test_scan_network_with_credentials(self, mock_requests, mock_socket):
        """Test that scan_network uses credentials when provided"""
        # Mock socket to simulate an open port 80
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.connect_ex.return_value = 0  # Port is open
        
        # Set up mock HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<title>Cisco Webex Room Kit</title>'
        mock_requests.return_value = mock_response
        
        # Call scan_network with a very narrow IP range to avoid long test times
        result = scan_network('127.0.0.1/32', username='admin', password='TANDBERG')
        
        # Just verify that requests.get was called at least once with the right credentials
        # The actual URL may vary because we're scanning multiple ports
        mock_requests.assert_called_with(
            mock_requests.call_args[0][0],  # Any URL
            auth=('admin', 'TANDBERG'),
            timeout=5,
            verify=False
        )
        
    @patch('discovery_system.discover.scan_network')
    def test_find_endpoints_passes_credentials(self, mock_scan):
        """Test that find_endpoints passes credentials to scan_network"""
        mock_scan.return_value = []
        
        # Call find_endpoints with credentials
        find_endpoints(username='admin', password='TANDBERG')
        
        # Verify that scan_network was called with credentials
        mock_scan.assert_called_with(
            None, 
            force_endpoints=None, 
            username='admin', 
            password='TANDBERG'
        )
