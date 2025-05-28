"""
Test optimized scan approach that first scans for SIP ports and then only checks those IPs
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock, call

# Add the parent directory to the path so we can import discovery_system modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from discovery_system.network_utils import scan_network


class TestScanNetwork:
    """Tests for the optimized scanning functionality."""
    
    def test_two_phase_scanning(self):
        """Test that the optimized scan works in two phases as expected."""
        # Create a test IP range
        test_range = "192.168.1.0/28"  # 16 IPs for testing
        
        # Create simulated IP addresses that respond on different ports
        ip_responses = {
            "192.168.1.1": [5060],               # Only SIP, should be checked further
            "192.168.1.2": [80, 443],            # No SIP, should be skipped
            "192.168.1.3": [5060, 5061, 80],     # Multiple ports including SIP
            "192.168.1.4": [22],                 # No relevant ports, should be skipped
            "192.168.1.5": [5061],               # Only secure SIP, should be checked
            "192.168.1.6": []                    # No open ports, should be skipped
        }
        
        # This will simulate our first phase scan that only checks SIP ports
        def mock_scan_ip_first_phase(ip, ports, timeout, **kwargs):
            if ip in ip_responses:
                open_ports = [p for p in ports if p in ip_responses[ip]]
                if open_ports:
                    return {
                        'ip': ip,
                        'hostname': f'test-host-{ip}',
                        'name': f'Device at {ip}',
                        'open_ports': open_ports
                    }
            return None
        
        # This will simulate our second phase scan that does detailed checks
        def mock_scan_ip_second_phase(ip, ports, timeout, **kwargs):
            if ip in ip_responses:
                open_ports = [p for p in ports if p in ip_responses[ip]]
                result = {
                    'ip': ip,
                    'hostname': f'test-host-{ip}',
                    'name': f'Device at {ip}',
                    'open_ports': open_ports
                }
                # Mark as video endpoint if it has at least one SIP port
                if 5060 in open_ports or 5061 in open_ports:
                    result['type'] = 'video_endpoint'
                return result
            return None
        
        # Mock the IP network parsing
        with patch('ipaddress.ip_network') as mock_ip_network, \
             patch('discovery_system.network_utils.scan_ip') as mock_scan_ip:
            
            # Setup the IP network mock
            mock_network = MagicMock()
            mock_ip_network.return_value = mock_network
            
            # Create mock IP addresses
            mock_ips = []
            for i in range(1, 7):
                mock_ip = MagicMock()
                mock_ip.__str__.return_value = f"192.168.1.{i}"
                mock_ips.append(mock_ip)
            
            # Set up network.hosts() to return our mock IPs
            mock_network.hosts.return_value = mock_ips
            
            # Set up scan_ip to behave differently for first and second phase
            mock_scan_ip.side_effect = lambda ip, ports, timeout, **kwargs: \
                mock_scan_ip_first_phase(ip, ports, timeout, **kwargs) \
                if 5060 in ports and 80 not in ports \
                else mock_scan_ip_second_phase(ip, ports, timeout, **kwargs)
            
            # Run the scanner
            result = scan_network(test_range)
            
            # Verify the function was called correctly
            assert mock_scan_ip.call_count > 0
            
            # The first set of calls should only check SIP ports
            first_phase_calls = [
                call for call in mock_scan_ip.call_args_list 
                if call[1]['ports'] == [5060, 5061]
            ]
            assert len(first_phase_calls) == len(mock_ips)
            
            # The second set of calls should be for IPs that responded in the first phase
            # and should check all video endpoint ports
            second_phase_calls = [
                call for call in mock_scan_ip.call_args_list 
                if call[1]['ports'] != [5060, 5061]
            ]
            # Should only check IPs 1, 3, and 5 which responded to SIP ports
            assert len(second_phase_calls) == 3
            
            # Verify we got the right endpoints in the final result
            assert len(result) == 3
            ip_addresses = [device['ip'] for device in result]
            assert "192.168.1.1" in ip_addresses
            assert "192.168.1.3" in ip_addresses
            assert "192.168.1.5" in ip_addresses
            assert "192.168.1.2" not in ip_addresses
            assert "192.168.1.4" not in ip_addresses
            assert "192.168.1.6" not in ip_addresses
