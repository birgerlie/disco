import pytest
import sys
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import discovery_system
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import after sys.path modification
from discovery_system.api_cache import ApiEndpointCache
from discovery_system.vendors.polycom import extract_polycom_api_details
from discovery_system.vendors.cisco import access_cisco_xml_api as extract_cisco_api_details

@pytest.mark.integration
class TestApiCacheIntegration:
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        # Create a temporary directory for the test cache file
        self.temp_dir = tempfile.mkdtemp()
        self.cache_file = os.path.join(self.temp_dir, "test_api_cache.json")
        
        # Initialize the API cache with our temporary file
        self.api_cache = ApiEndpointCache(self.cache_file)
        
        # Store the original global cache
        from discovery_system.api_cache import api_cache as global_cache
        self.original_cache = global_cache
        
        # Replace the global cache with our test cache
        import discovery_system.api_cache
        discovery_system.api_cache.api_cache = self.api_cache
        
        yield
        
        # Restore the original global cache
        discovery_system.api_cache.api_cache = self.original_cache
        
        # Clean up after the test
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        os.rmdir(self.temp_dir)
    
    @patch('requests.get')
    def test_polycom_cached_endpoint(self, mock_get):
        """Test that the system uses cached API endpoints for Polycom devices."""
        # Add a cached endpoint for RealPresence Group 300
        self.api_cache.add_successful_endpoint(
            manufacturer="Polycom",
            model="RealPresence Group 300", 
            endpoint_path="/rest/system",
            success=True
        )
        
        # Mock responses
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "build": "510016",
            "buildType": "Release",
            "model": "RealPresence Group 300",
            "serialNumber": "89153143C78AD5",
            "softwareVersion": "Release - 6.1.7.2-510016",
            "systemName": "test.system"
        }
        mock_get.return_value = mock_response
        
        # Create test endpoint data
        endpoint = {
            'ip': '172.17.21.20',
            'hostname': '172.17.21.20',
            'type': 'video_endpoint',
            'open_ports': [80, 443],
            'manufacturer': 'Polycom',
            'model': 'RealPresence Group 300'
        }
        
        # Call the function to test
        result = extract_polycom_api_details(endpoint, 'admin', 'admin')
        
        # Verify result
        assert result['manufacturer'] == 'Polycom'
        assert result['model'] == 'RealPresence Group 300'
        assert result['sw_version'] == 'Release - 6.1.7.2-510016'
        
        # Verify that we only called the API endpoint from the cache
        assert mock_get.call_count == 1
        mock_get.assert_called_once_with(
            f"https://{endpoint['ip']}/rest/system",
            auth=('admin', 'admin'),
            timeout=5,
            verify=False,
            headers={'Accept': 'application/json'}
        )
    
    @patch('requests.get')
    def test_cisco_cached_endpoint(self, mock_get):
        """Test that the system uses cached API endpoints for Cisco devices."""
        # Add a cached endpoint for Room Kit Mini
        self.api_cache.add_successful_endpoint(
            manufacturer="Cisco",
            model="Room Kit Mini", 
            endpoint_path="/status.xml",
            success=True
        )
        
        # Mock responses
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <Status>
            <SystemUnit>
                <ProductId>Room Kit Mini</ProductId>
                <ProductType>Cisco Codec</ProductType>
                <Software>
                    <Version>ce9.15.0.11</Version>
                </Software>
                <Hardware>
                    <SerialNumber>1234567890</SerialNumber>
                </Hardware>
            </SystemUnit>
        </Status>
        """
        mock_get.return_value = mock_response
        
        # Create test endpoint data
        endpoint = {
            'ip': '172.17.100.50',
            'hostname': '172.17.100.50',
            'type': 'video_endpoint',
            'open_ports': [80, 443],
            'manufacturer': 'Cisco',
            'model': 'Room Kit Mini'
        }
        
        # Call the function to test
        result = extract_cisco_api_details(endpoint, username='admin', password='admin')
        
        # Verify result
        assert result['manufacturer'] == 'Cisco'
        assert result['model'] == 'Room Kit Mini'
        assert result['sw_version'] == 'ce9.15.0.11'
        
        # Verify that we only called the API endpoint from the cache
        assert mock_get.call_count == 1
        mock_get.assert_called_once_with(
            f"https://{endpoint['ip']}/status.xml",
            auth=('admin', 'admin'),
            timeout=5,
            verify=False
        )
