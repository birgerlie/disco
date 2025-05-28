"""
Test the scanner CLI functionality
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import discovery_system modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import with a different name to avoid name conflicts in the mock patching
from discovery_system.scanner_cli import main as scanner_main


class TestScannerCLI:
    """Tests for the scanner CLI with optimized scanning option."""
    
    def test_basic_scanning(self):
        """Test that the scanner CLI works correctly."""
        # Mock find_endpoints to avoid actual network scanning
        with patch('discovery_system.discover.find_endpoints') as mock_find_endpoints, \
             patch('discovery_system.scanner_cli.get_local_network_range') as mock_get_range, \
             patch('sys.argv', ['scanner_cli.py']), \
             patch.dict('os.environ', {}):
            
            # Set up mocks
            mock_find_endpoints.return_value = [
                {
                    'ip': '192.168.1.100',
                    'name': 'Test Endpoint',
                    'type': 'video_endpoint'
                }
            ]
            mock_get_range.return_value = '192.168.1.0/24'
            
            # Run the CLI with our mocks
            scanner_main()
            
            # Verify find_endpoints was called
            mock_find_endpoints.assert_called_once()
    
    def test_custom_ip_range(self):
        """Test that the scanner CLI works with a custom IP range."""
        # Mock find_endpoints to avoid actual network scanning
        with patch('discovery_system.discover.find_endpoints') as mock_find_endpoints, \
             patch('sys.argv', ['scanner_cli.py', '--range', '10.0.0.0/24']), \
             patch.dict('os.environ', {}):
            
            # Set up mocks
            mock_find_endpoints.return_value = [
                {
                    'ip': '10.0.0.1',
                    'name': 'Test Endpoint',
                    'type': 'video_endpoint'
                }
            ]
            
            # Run the CLI with our mocks
            scanner_main()
            
            # Verify find_endpoints was called with the correct IP range
            mock_find_endpoints.assert_called_once_with(
                ip_range='10.0.0.0/24',
                include_details=True,
                force_endpoints=None,
                username='admin',
                password='TANDBERG'
            )
