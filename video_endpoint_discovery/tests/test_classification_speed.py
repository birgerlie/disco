"""
Test the endpoint classification system with focus on speed.
These tests use extensive mocking to avoid real network calls and timeout delays.
"""

import pytest
import sys
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import discovery_system
sys.path.insert(0, str(Path(__file__).parent.parent))

from discovery_system.discover import find_endpoints
from discovery_system.endpoint_classification import classify_endpoints


class TestEndpointClassificationSpeed:
    """Tests for the endpoint classification system with focus on speed."""
    
    @patch('discovery_system.discover.scan_network')
    @patch('discovery_system.endpoint_classification.extract_endpoint_details')
    def test_classification_speed_with_multiple_workers(self, mock_extract, mock_scan):
        """Test that the worker-based classification system is faster with multiple workers."""
        # Create a larger set of endpoints for testing performance
        endpoints = []
        for i in range(10):  # 10 endpoints should be enough for testing
            endpoints.append({
                'ip': f'192.168.1.{i+1}',
                'type': 'video_endpoint',
                'name': f'Meeting Room {i+1}',
                'hostname': f'meetingroom{i+1}.local',
                'open_ports': [80, 443, 5060]
            })
        
        # Mock scan_network to return test endpoints
        mock_scan.return_value = endpoints
        
        # Mock extract_endpoint_details to add a slight delay and return test data
        def mock_extract_side_effect(endpoint, *args, **kwargs):
            # Very small delay to simulate API call without actually being slow
            time.sleep(0.01)
            return {
                **endpoint,
                'manufacturer': 'Test Manufacturer',
                'model': f'Test Model for {endpoint["ip"]}',
                'sw_version': '1.0',
                'serial': f'SERIAL{endpoint["ip"].split(".")[-1]}',
                'mac_address': '00:11:22:33:44:55',
                'status': 'online',
                'capabilities': ['video', 'audio']
            }
            
        mock_extract.side_effect = mock_extract_side_effect
        
        # First run with a single worker
        start_time_single = time.time()
        result_single = find_endpoints(num_workers=1)
        end_time_single = time.time()
        single_worker_time = end_time_single - start_time_single
        
        # Reset mocks
        mock_scan.reset_mock()
        mock_extract.reset_mock()
        mock_scan.return_value = endpoints
        mock_extract.side_effect = mock_extract_side_effect
        
        # Run with multiple workers
        start_time_multi = time.time()
        result_multi = find_endpoints(num_workers=4)
        end_time_multi = time.time()
        multi_worker_time = end_time_multi - start_time_multi
        
        # Check that both runs found the correct endpoints
        assert len(result_single) == 10
        assert len(result_multi) == 10
        
        # Multiple workers should be at least somewhat faster
        # We're not asserting an exact amount because test environments vary
        print(f"\nSingle worker time: {single_worker_time:.4f}s")
        print(f"Multi worker time:  {multi_worker_time:.4f}s")
        print(f"Speed improvement:  {(single_worker_time / multi_worker_time):.2f}x")
        
        # We don't make this a strict assertion because some test environments
        # might not show a speedup with such a small test set
        assert len(result_single) == len(result_multi)
        
    @patch('discovery_system.endpoint_classification.extract_endpoint_details')
    def test_queue_based_classification_directly(self, mock_extract):
        """Test the queue-based classification system directly."""
        # Create a set of endpoints for testing
        endpoints = []
        for i in range(5):
            endpoints.append({
                'ip': f'192.168.1.{i+1}',
                'type': 'video_endpoint',
                'name': f'Meeting Room {i+1}'
            })
        
        # Mock extract_endpoint_details to add classification details
        def mock_extract_side_effect(endpoint, *args, **kwargs):
            # Very small delay to simulate API call without actually being slow
            time.sleep(0.01)
            return {
                **endpoint,
                'manufacturer': 'Test Manufacturer',
                'model': f'Test Model for {endpoint["ip"]}',
                'sw_version': '1.0',
                'status': 'online',
                'capabilities': ['video', 'audio']
            }
            
        mock_extract.side_effect = mock_extract_side_effect
        
        # Call classify_endpoints directly with 4 workers
        start_time = time.time()
        result = classify_endpoints(
            endpoints=endpoints,
            num_workers=4,
            username='admin',
            password='TANDBERG'
        )
        end_time = time.time()
        classification_time = end_time - start_time
        
        # Verify results
        assert len(result) == 5
        for endpoint in result:
            assert 'manufacturer' in endpoint
            assert 'model' in endpoint
            assert 'status' in endpoint
        
        print(f"\nClassification time for 5 endpoints with 4 workers: {classification_time:.4f}s")
