"""
Test module to verify that the system works without using the cache.
"""

import sys
import pytest
from unittest.mock import patch, MagicMock
import os
import tempfile
import json
import requests

# Add the parent directory to the path so we can import discovery_system modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from discovery_system.api_cache import ApiEndpointCache
from discovery_system.vendors.polycom import extract_polycom_api_details
from discovery_system.vendors.cisco import access_cisco_xml_api
from discovery_system.discover import find_endpoints
from discovery_system.network_utils import scan_network


class TestNoCacheAccess:
    """Tests to ensure that the cache is not used in the vendor modules."""

    def setup_method(self):
        """Set up the test environment."""
        # Create a temporary directory for the test cache file
        self.temp_dir = tempfile.mkdtemp()
        self.cache_file = os.path.join(self.temp_dir, "test_api_cache.json")
        
        # Create a mock API cache
        self.mock_cache = MagicMock(spec=ApiEndpointCache)
        
        # Save the original cache to restore later
        import discovery_system.api_cache
        self.original_cache = discovery_system.api_cache.api_cache
        
        # Replace with the mock cache
        discovery_system.api_cache.api_cache = self.mock_cache

    def teardown_method(self):
        """Clean up after the test."""
        # Restore the original cache
        import discovery_system.api_cache
        discovery_system.api_cache.api_cache = self.original_cache
        
        # Clean up temp directory
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
    
    def test_polycom_no_cache_access(self):
        """Test that the Polycom vendor module doesn't access the cache."""
        # Create a test endpoint
        endpoint = {
            'ip': '192.168.1.100',
            'type': 'video_endpoint', 
            'model': 'Group 700'
        }
        
        # Call the extract function
        with patch('requests.get') as mock_get:
            # Set up mock response for the API call
            mock_response = MagicMock()
            mock_response.status_code = 404  # Make all requests fail
            mock_get.return_value = mock_response
            
            # Call function
            extract_polycom_api_details(endpoint)
            
            # Verify the cache was never accessed
            self.mock_cache.get_successful_endpoint.assert_not_called()
            self.mock_cache.add_successful_endpoint.assert_not_called()
            
    def test_cisco_no_cache_access(self):
        """Test that the Cisco vendor module doesn't access the cache."""
        # Create a test endpoint
        endpoint = {
            'ip': '192.168.1.101',
            'type': 'video_endpoint',
            'open_ports': [443]
        }
        
        # Call the extract function
        with patch('requests.get') as mock_get:
            # Set up mock response for the API call
            mock_response = MagicMock()
            mock_response.status_code = 404  # Make all requests fail
            mock_get.return_value = mock_response
            
            # Call function
            access_cisco_xml_api(endpoint)
            
            # Verify the cache was never accessed
            self.mock_cache.get_successful_endpoint.assert_not_called()
            self.mock_cache.add_successful_endpoint.assert_not_called()
            
    def test_scan_network_no_cache(self):
        """Test that the network scanner doesn't use the cache."""
        # Create a small test range
        test_range = "192.168.1.0/30"
        
        # Mock the socket and scan_ip function
        with patch('discovery_system.network_utils.scan_ip') as mock_scan_ip, \
             patch('ipaddress.ip_network') as mock_ip_network:
            
            # Configure mock for ip_network
            mock_network = MagicMock()
            mock_ip_network.return_value = mock_network
            
            # Create mock IP addresses
            mock_ip1 = MagicMock()
            mock_ip1.__str__.return_value = "192.168.1.1"
            mock_ip2 = MagicMock()
            mock_ip2.__str__.return_value = "192.168.1.2"
            
            # Make network.hosts() return our mock IPs
            mock_network.hosts.return_value = [mock_ip1, mock_ip2]
            
            # Configure scan_ip to return a video endpoint
            endpoint_result = {
                'ip': '192.168.1.1',
                'hostname': 'test-endpoint',
                'name': 'Device at 192.168.1.1',
                'type': 'video_endpoint',
                'open_ports': [80, 443]
            }
            mock_scan_ip.return_value = endpoint_result
            
            # Run the network scanner
            scan_result = scan_network(test_range)
            
            # Verify we got our expected endpoint
            assert len(scan_result) > 0
            assert scan_result[0]['type'] == 'video_endpoint'
            
            # Verify the cache was never accessed
            self.mock_cache.get_successful_endpoint.assert_not_called()
            self.mock_cache.add_successful_endpoint.assert_not_called()
