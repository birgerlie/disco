"""
Test the scanner CLI with optimized scanning option
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import discovery_system modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import with a different name to avoid name conflicts in the mock patching
from discovery_system.scanner_cli import main as scanner_main


class TestOptimizedScannerCLI:
    """Tests for the scanner CLI with optimized scanning option."""
    
    def test_optimized_scanning_option(self):
        """Test that the --optimized flag enables optimized scanning."""
        # Mock find_endpoints to avoid actual network scanning
        with patch('discovery_system.discover.find_endpoints') as mock_find_endpoints, \
             patch('discovery_system.scanner_cli.get_local_network_range') as mock_get_range, \
             patch('sys.argv', ['scanner_cli.py', '--optimized']), \
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
            
            # Verify that USE_OPTIMIZED_SCAN environment variable was set to 'true'
            assert os.environ.get('USE_OPTIMIZED_SCAN') == 'true'
            
            # Verify find_endpoints was called
            mock_find_endpoints.assert_called_once()
    
    def test_normal_scanning_without_option(self):
        """Test that without the --optimized flag, normal scanning is used."""
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
            
            # Verify that USE_OPTIMIZED_SCAN environment variable was NOT set
            assert 'USE_OPTIMIZED_SCAN' not in os.environ or os.environ.get('USE_OPTIMIZED_SCAN') != 'true'
            
            # Verify find_endpoints was called
            mock_find_endpoints.assert_called_once()
