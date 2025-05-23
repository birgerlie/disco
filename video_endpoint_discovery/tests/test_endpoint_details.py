import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import json
import re

# Add the parent directory to the path so we can import discovery_system
sys.path.insert(0, str(Path(__file__).parent.parent))

from discovery_system.endpoint_details import (
    extract_endpoint_details,
    parse_cisco_details,
    parse_polycom_details,
    parse_tandberg_details,
    get_endpoint_uri
)

class TestEndpointDetails:
    """Tests for the endpoint_details module which extracts manufacturer, model, 
    make, URI, and software version from video endpoints."""
    
    @patch('requests.get')
    def test_extract_endpoint_details_cisco(self, mock_requests):
        """Test extracting details from a Cisco endpoint."""
        # Mock a Cisco endpoint response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <title>Cisco Webex Room Kit</title>
        <meta name="description" content="Cisco Webex Room Kit Control Panel">
        <span class="sw-version">RoomOS 10.15.2.2</span>
        <div class="serial-number">FOC12345678</div>
        """
        mock_requests.return_value = mock_response
        
        endpoint = {
            'ip': '192.168.1.100',
            'hostname': 'roomkit.local',
            'type': 'video_endpoint',
            'open_ports': [80, 443]
        }
        
        result = extract_endpoint_details(endpoint, username='admin', password='TANDBERG')
        
        assert result['manufacturer'] == 'Cisco'
        assert result['model'] == 'Webex Room Kit'
        assert result['sw_version'] == 'RoomOS 10.15.2.2'
        assert result['uri'] == 'https://192.168.1.100'
        assert 'serial' in result
    
    @patch('requests.get')
    def test_extract_endpoint_details_polycom(self, mock_requests):
        """Test extracting details from a Polycom endpoint."""
        # Mock a Polycom endpoint response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <title>Polycom RealPresence Group 700</title>
        <div class="software-version">Software 6.2.1-12345</div>
        <div class="system-name">Conference Room A</div>
        """
        mock_requests.return_value = mock_response
        
        endpoint = {
            'ip': '192.168.1.101',
            'hostname': 'polycom-group.local',
            'type': 'video_endpoint',
            'open_ports': [80, 443]
        }
        
        result = extract_endpoint_details(endpoint, username='admin', password='admin')
        
        assert result['manufacturer'] == 'Polycom'
        assert result['model'] == 'RealPresence Group 700'
        assert result['sw_version'] == 'Software 6.2.1-12345'
        assert result['uri'] == 'https://192.168.1.101'
        assert 'system_name' in result
    
    @patch('requests.get')
    def test_extract_endpoint_details_tandberg(self, mock_requests):
        """Test extracting details from a Tandberg endpoint."""
        # Mock a Tandberg endpoint response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <title>TANDBERG C40</title>
        <div id="sw-version">TC7.3.6.4c7b8e7</div>
        <div id="product-id">Codec C40</div>
        """
        mock_requests.return_value = mock_response
        
        endpoint = {
            'ip': '192.168.1.102',
            'hostname': 'tandberg-c40.local',
            'type': 'video_endpoint',
            'open_ports': [80, 443]
        }
        
        result = extract_endpoint_details(endpoint, username='admin', password='TANDBERG')
        
        assert result['manufacturer'] == 'TANDBERG'
        assert result['model'] == 'C40'
        assert result['sw_version'] == 'TC7.3.6.4c7b8e7'
        assert result['uri'] == 'https://192.168.1.102'  # Using HTTPS since port 443 is in open_ports
    
    @patch('requests.get')
    def test_extract_endpoint_details_unknown(self, mock_requests):
        """Test extracting details from an unknown endpoint type."""
        # Mock an unknown endpoint response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <title>Video Endpoint</title>
        <div>Welcome to the control panel</div>
        """
        mock_requests.return_value = mock_response
        
        endpoint = {
            'ip': '192.168.1.103',
            'hostname': 'unknown.local',
            'type': 'video_endpoint',
            'open_ports': [80, 443]
        }
        
        result = extract_endpoint_details(endpoint, username='admin', password='admin')
        
        assert result['manufacturer'] == 'Unknown'
        assert result['model'] == 'Unknown'
        assert result['sw_version'] == 'Unknown'
        assert result['uri'] == 'https://192.168.1.103'  # Using HTTPS since port 443 is in open_ports
    
    def test_parse_cisco_details(self):
        """Test parsing details from Cisco endpoint HTML content."""
        html_content = """
        <title>Cisco Webex Room Kit Pro</title>
        <meta name="description" content="Cisco Webex Room Kit Pro Control Panel">
        <span class="sw-version">RoomOS 11.0.1.3</span>
        <div class="mac-address">00:11:22:33:44:55</div>
        """
        
        result = parse_cisco_details(html_content)
        
        assert result['manufacturer'] == 'Cisco'
        assert result['model'] == 'Webex Room Kit Pro'
        assert result['sw_version'] == 'RoomOS 11.0.1.3'
        assert result['mac_address'] == '00:11:22:33:44:55'
    
    def test_parse_polycom_details(self):
        """Test parsing details from Polycom endpoint HTML content."""
        html_content = """
        <title>Polycom RealPresence Group 500</title>
        <div class="software-version">Software 6.3.0-54321</div>
        <div class="system-name">Meeting Room B</div>
        """
        
        result = parse_polycom_details(html_content)
        
        assert result['manufacturer'] == 'Polycom'
        assert result['model'] == 'RealPresence Group 500'
        assert result['sw_version'] == 'Software 6.3.0-54321'
        assert result['system_name'] == 'Meeting Room B'
    
    def test_parse_tandberg_details(self):
        """Test parsing details from Tandberg endpoint HTML content."""
        html_content = """
        <title>TANDBERG MXP</title>
        <div id="sw-version">F9.3.1</div>
        <div id="product-id">Codec MXP</div>
        """
        
        result = parse_tandberg_details(html_content)
        
        assert result['manufacturer'] == 'TANDBERG'
        assert result['model'] == 'MXP'
        assert result['sw_version'] == 'F9.3.1'
        assert result['product_id'] == 'Codec MXP'
    
    def test_get_endpoint_uri(self):
        """Test generating the endpoint URI based on available ports."""
        # Test with HTTPS available
        endpoint = {'ip': '192.168.1.100', 'open_ports': [80, 443]}
        assert get_endpoint_uri(endpoint) == 'https://192.168.1.100'
        
        # Test with only HTTP available
        endpoint = {'ip': '192.168.1.101', 'open_ports': [80]}
        assert get_endpoint_uri(endpoint) == 'http://192.168.1.101'
        
        # Test with no web ports
        endpoint = {'ip': '192.168.1.102', 'open_ports': [22, 5060]}
        assert get_endpoint_uri(endpoint) == 'http://192.168.1.102'
