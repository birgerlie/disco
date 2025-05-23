import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import json
import io

# Add the parent directory to the path so we can import discovery_system
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestScannerCLI:
    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('discovery_system.discover.find_endpoints')
    @patch('discovery_system.network_utils.get_local_network_range')
    def test_scanner_cli_basic_output(self, mock_get_network_range, mock_find_endpoints, mock_stdout):
        """Test that the scanner CLI outputs endpoint information correctly"""
        from discovery_system.scanner_cli import main
        
        # Set up mocks
        mock_get_network_range.return_value = '192.168.1.0/24'
        mock_find_endpoints.return_value = [
            {'ip': '192.168.1.10', 'type': 'video_endpoint', 'name': 'Meeting Room 1'},
            {'ip': '192.168.1.12', 'type': 'video_endpoint', 'name': 'Meeting Room 2'}
        ]
        
        # Run the scanner CLI with default arguments
        with patch('sys.argv', ['scanner_cli']):
            main()
        
        # Check that the output contains the endpoint information
        output = mock_stdout.getvalue()
        assert 'Meeting Room 1' in output
        assert '192.168.1.10' in output
        assert 'Meeting Room 2' in output
        assert '192.168.1.12' in output
    
    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('discovery_system.discover.find_endpoints')
    @patch('discovery_system.network_utils.get_local_network_range')
    def test_scanner_cli_json_output(self, mock_get_network_range, mock_find_endpoints, mock_stdout):
        """Test that the scanner CLI can output JSON format"""
        from discovery_system.scanner_cli import main
        
        # Set up mocks
        mock_get_network_range.return_value = '192.168.1.0/24'
        
        # Mock the find_endpoints function to return test data
        test_endpoints = [
            {'ip': '192.168.1.10', 'type': 'video_endpoint', 'name': 'Meeting Room 1'},
            {'ip': '192.168.1.12', 'type': 'video_endpoint', 'name': 'Meeting Room 2'}
        ]
        mock_find_endpoints.return_value = test_endpoints
        
        # Run the scanner CLI with JSON output argument
        with patch('sys.argv', ['scanner_cli', '--json']):
            main()
        
        # Get the output and find the JSON part (should be the last part of the output)
        output = mock_stdout.getvalue()
        
        # Try to find the start of the JSON array
        json_start = output.find('[\n')
        if json_start >= 0:
            json_str = output[json_start:]
            parsed_output = json.loads(json_str)
            assert len(parsed_output) == 2
            assert parsed_output[0]['name'] == 'Meeting Room 1'
            assert parsed_output[1]['ip'] == '192.168.1.12'
        else:
            pytest.fail("JSON output not found in CLI output")
    
    @patch('discovery_system.discover.find_endpoints')
    @patch('discovery_system.network_utils.get_local_network_range')
    def test_scanner_cli_auto_detects_network_range(self, mock_get_network_range, mock_find_endpoints):
        """Test that scanner CLI automatically detects and uses local network range"""
        from discovery_system.scanner_cli import main
        
        # Mock the network range detection to return a specific range
        # Use the actual range that's being detected in the environment
        mock_get_network_range.return_value = '172.17.20.0/23'
        
        # Call the main function
        with patch('sys.argv', ['scanner_cli']):
            main()
        
        # Verify that find_endpoints was called with the mocked network range
        assert mock_find_endpoints.call_count >= 1
        call_args = mock_find_endpoints.call_args[1]  # Get the keyword arguments
        assert call_args['ip_range'] == '172.17.20.0/23'
        assert call_args['include_details'] == True
        assert call_args['force_endpoints'] == None
        # CLI-based tests pass None for username/password, which will use defaults in the actual function
        assert 'username' in call_args
        assert 'password' in call_args
    
    @patch('discovery_system.discover.find_endpoints')
    @patch('discovery_system.network_utils.get_local_network_range')
    def test_scanner_cli_custom_ip_range(self, mock_get_network_range, mock_find_endpoints):
        """Test that the scanner CLI can use a user-specified IP range"""
        from discovery_system.scanner_cli import main
        
        # Set up mocks
        mock_find_endpoints.return_value = []
        
        # Run the scanner CLI with custom IP range
        with patch('sys.argv', ['scanner_cli', '--range', '10.0.0.0/24']):
            main()
        
        # Verify find_endpoints was called with the user-specified range
        assert mock_find_endpoints.call_count >= 1
        call_args = mock_find_endpoints.call_args[1]  # Get the keyword arguments
        assert call_args['ip_range'] == '10.0.0.0/24'
        assert call_args['include_details'] == True
        assert call_args['force_endpoints'] == None
        # CLI-based tests pass None for username/password, which will use defaults in the actual function
        assert 'username' in call_args
        assert 'password' in call_args
