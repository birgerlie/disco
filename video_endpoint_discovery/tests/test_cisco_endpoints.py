import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import re

# Add the parent directory to the path so we can import discovery_system
sys.path.insert(0, str(Path(__file__).parent.parent))

from discovery_system.endpoint_details import (
    parse_cisco_details,
    extract_endpoint_details
)

class TestCiscoEndpointParsing:
    """Tests for parsing Cisco endpoint HTML content with real-world patterns."""
    
    def test_parse_cisco_room_kit_basic(self):
        """Test parsing Room Kit with basic HTML patterns."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Cisco Webex Room Kit</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
            <div class="system-info">
                <table>
                    <tr>
                        <td>Software Version:</td>
                        <td>RoomOS 11.3.1.0</td>
                    </tr>
                    <tr>
                        <td>Serial Number:</td>
                        <td>FTT234500AB</td>
                    </tr>
                    <tr>
                        <td>MAC Address:</td>
                        <td>00:11:22:33:44:55</td>
                    </tr>
                </table>
            </div>
        </body>
        </html>
        """
        
        result = parse_cisco_details(html_content)
        
        assert result['manufacturer'] == 'Cisco'
        assert result['model'] == 'Webex Room Kit'
        assert result['sw_version'] == 'RoomOS 11.3.1.0'
        assert result['serial'] == 'FTT234500AB'
        assert result['mac_address'] == '00:11:22:33:44:55'
    
    def test_parse_cisco_desk_pro(self):
        """Test parsing Desk Pro with more complex HTML structure."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Desk Pro</title>
            <meta name="description" content="Cisco Webex Desk Pro">
        </head>
        <body>
            <div id="system-info-container">
                <div class="info-block">
                    <span class="info-label">Product:</span>
                    <span class="info-value">Cisco Webex Desk Pro</span>
                </div>
                <div class="info-block">
                    <span class="info-label">Software:</span>
                    <span class="info-value">RoomOS 11.2.1.4 d8e76fa3669</span>
                </div>
                <div class="info-block">
                    <span class="info-label">Serial:</span>
                    <span class="info-value">FOC2307H1X2</span>
                </div>
            </div>
        </body>
        </html>
        """
        
        result = parse_cisco_details(html_content)
        
        assert result['manufacturer'] == 'Cisco'
        assert result['model'] == 'Webex Desk Pro'
        assert result['sw_version'] == 'RoomOS 11.2.1.4 d8e76fa3669'
        assert result['serial'] == 'FOC2307H1X2'
    
    def test_parse_cisco_sx80_legacy(self):
        """Test parsing older SX80 HTML structure."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Cisco TelePresence SX80</title>
        </head>
        <body>
            <div class="product-info">
                <h1>Cisco TelePresence SX80</h1>
                <p>Software version: TC7.3.6</p>
                <p>Serial number: FTT182700UT</p>
                <p>IP: 172.17.20.72</p>
            </div>
        </body>
        </html>
        """
        
        result = parse_cisco_details(html_content)
        
        assert result['manufacturer'] == 'Cisco'
        assert result['model'] == 'TelePresence SX80'
        assert result['sw_version'] == 'TC7.3.6'
        assert result['serial'] == 'FTT182700UT'
    
    @patch('requests.get')
    def test_extract_endpoint_details_cisco_actual(self, mock_requests):
        """Test extracting details from a simulated actual Cisco endpoint."""
        # This test uses a more realistic HTML snippet that approximates
        # what we might get from a real Cisco endpoint
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Cisco Webex Codec Pro</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body>
            <header>
                <div class="product-header">
                    <img src="/images/cisco-logo.png" alt="Cisco">
                    <h1>Webex Codec Pro</h1>
                </div>
            </header>
            <main>
                <div class="system-status">
                    <table class="status-table">
                        <tr>
                            <td class="label">Software:</td>
                            <td class="value">RoomOS 10.8.2.5 a267d082159</td>
                        </tr>
                        <tr>
                            <td class="label">Serial Number:</td>
                            <td class="value">FOC2237N4VJ</td>
                        </tr>
                        <tr>
                            <td class="label">Uptime:</td>
                            <td class="value">17 days, 4 hours</td>
                        </tr>
                        <tr>
                            <td class="label">MAC Address:</td>
                            <td class="value">08:96:AD:F2:E3:1A</td>
                        </tr>
                        <tr>
                            <td class="label">IP Address:</td>
                            <td class="value">172.17.20.72</td>
                        </tr>
                    </table>
                </div>
            </main>
        </body>
        </html>
        """
        mock_requests.return_value = mock_response
        
        endpoint = {
            'ip': '172.17.20.72',
            'hostname': '172.17.20.72',
            'type': 'video_endpoint',
            'open_ports': [80, 443]
        }
        
        result = extract_endpoint_details(endpoint, username='admin', password='TANDBERG')
        
        assert result['manufacturer'] == 'Cisco'
        assert result['model'] == 'Webex Codec Pro'
        assert result['sw_version'] == 'RoomOS 10.8.2.5 a267d082159'
        assert result['serial'] == 'FOC2237N4VJ'
        assert result['mac_address'] == '08:96:AD:F2:E3:1A'
        assert result['type'] == 'video_endpoint'  # Type should be preserved
        assert result['uri'] == 'https://172.17.20.72'
