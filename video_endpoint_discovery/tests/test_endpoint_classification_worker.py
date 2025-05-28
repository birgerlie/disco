"""
Test the endpoint classification worker system that uses a queue
"""

import sys
import os
import pytest
import threading
import queue
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import discovery_system modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from discovery_system.endpoint_classification import EndpointClassificationWorker, classify_endpoints


class TestEndpointClassificationWorker:
    """Tests for the endpoint classification worker system."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.endpoint_queue = queue.Queue()
        self.result_list = []
        self.lock = threading.Lock()
        
    def test_classification_worker(self):
        """Test that the worker correctly processes endpoints from the queue."""
        # Create a worker
        with patch('discovery_system.endpoint_classification.extract_endpoint_details') as mock_extract:
            # Configure the mock to return different details for different IPs
            def mock_extract_side_effect(endpoint, *args, **kwargs):
                # Add classification details to the endpoint
                ip = endpoint['ip']
                if ip == '192.168.1.1':
                    endpoint.update({
                        'manufacturer': 'Cisco',
                        'model': 'Webex Room Kit',
                        'sw_version': '10.15.1',
                        'serial': 'ABC123',
                        'mac_address': '00:11:22:33:44:55'
                    })
                elif ip == '192.168.1.2':
                    endpoint.update({
                        'manufacturer': 'Polycom',
                        'model': 'Group 700',
                        'sw_version': '6.2.2',
                        'serial': 'XYZ789',
                        'mac_address': '55:44:33:22:11:00'
                    })
                return endpoint
                
            mock_extract.side_effect = mock_extract_side_effect
            
            # Create test endpoints
            endpoints = [
                {
                    'ip': '192.168.1.1',
                    'hostname': 'cisco-endpoint',
                    'open_ports': [80, 443, 5060],
                    'type': 'video_endpoint',
                    'name': 'Device at 192.168.1.1'
                },
                {
                    'ip': '192.168.1.2',
                    'hostname': 'polycom-endpoint',
                    'open_ports': [80, 443, 5061],
                    'type': 'video_endpoint',
                    'name': 'Device at 192.168.1.2'
                }
            ]
            
            # Create a worker and start it
            worker = EndpointClassificationWorker(
                endpoint_queue=self.endpoint_queue,
                results=self.result_list,
                lock=self.lock,
                username='admin',
                password='TANDBERG'
            )
            
            # Start the worker in a thread
            worker_thread = threading.Thread(target=worker.run)
            worker_thread.daemon = True
            worker_thread.start()
            
            # Add endpoints to the queue
            for endpoint in endpoints:
                self.endpoint_queue.put(endpoint)
            
            # Add sentinel to signal end of queue
            self.endpoint_queue.put(None)
            
            # Wait for the worker to finish
            worker_thread.join(timeout=2)
            
            # Check that we have the expected number of results
            assert len(self.result_list) == 2
            
            # Check the details of the classified endpoints
            classified_endpoints = sorted(self.result_list, key=lambda x: x['ip'])
            
            # Check first endpoint
            assert classified_endpoints[0]['ip'] == '192.168.1.1'
            assert classified_endpoints[0]['manufacturer'] == 'Cisco'
            assert classified_endpoints[0]['model'] == 'Webex Room Kit'
            
            # Check second endpoint
            assert classified_endpoints[1]['ip'] == '192.168.1.2'
            assert classified_endpoints[1]['manufacturer'] == 'Polycom'
            assert classified_endpoints[1]['model'] == 'Group 700'
            
    def test_classify_endpoints_function(self):
        """Test the classify_endpoints function that manages multiple workers."""
        # Create test endpoints
        endpoints = [
            {'ip': '192.168.1.1', 'type': 'video_endpoint'},
            {'ip': '192.168.1.2', 'type': 'video_endpoint'},
            {'ip': '192.168.1.3', 'type': 'video_endpoint'},
            {'ip': '192.168.1.4', 'type': 'video_endpoint'}
        ]
        
        # Mock the extract_endpoint_details function
        with patch('discovery_system.endpoint_classification.extract_endpoint_details') as mock_extract:
            # Configure the mock to add classification details
            def mock_extract_side_effect(endpoint, *args, **kwargs):
                endpoint['classified'] = True
                endpoint['manufacturer'] = 'Test Manufacturer'
                endpoint['model'] = f'Model for {endpoint["ip"]}'
                return endpoint
                
            mock_extract.side_effect = mock_extract_side_effect
            
            # Call the classify_endpoints function
            classified_endpoints = classify_endpoints(
                endpoints=endpoints,
                num_workers=2,
                username='admin',
                password='TANDBERG'
            )
            
            # Check that all endpoints were classified
            assert len(classified_endpoints) == 4
            for endpoint in classified_endpoints:
                assert endpoint['classified'] == True
                assert 'manufacturer' in endpoint
                assert 'model' in endpoint
