import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import discovery_system
sys.path.insert(0, str(Path(__file__).parent.parent))

from discovery_system.scanner_cli import parse_arguments, main

class TestScannerCLIDefaults:
    """Tests for scanner_cli module to ensure default values for username and password."""
    
    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_arguments_default_credentials(self, mock_parse_args):
        """Test that parse_arguments provides default values for username and password when they are None."""
        # Mock the parse_args to return None for username and password
        mock_args = MagicMock()
        mock_args.username = None
        mock_args.password = None
        mock_args.ip_range = None
        mock_args.json = False
        mock_args.simple = False
        mock_args.force_endpoints = None
        mock_parse_args.return_value = mock_args
        
        # Call the function under test
        args = parse_arguments()
        
        # Verify the default values are applied
        assert args.username == "admin", "Default username should be 'admin'"
        assert args.password == "TANDBERG", "Default password should be 'TANDBERG'"
        
    @patch('discovery_system.discover.find_endpoints')
    def test_main_passes_default_credentials(self, mock_find_endpoints):
        """Test that main passes default values to find_endpoints when no credentials are provided."""
        # Create a mock parser and arguments to override the actual command-line arguments
        with patch('argparse.ArgumentParser.parse_args') as mock_parse_args:
            # Mock arguments with default values for username and password
            mock_args = MagicMock()
            mock_args.username = "admin"
            mock_args.password = "TANDBERG"
            mock_args.ip_range = "192.168.1.0/24"  # Specify the IP range directly
            mock_args.json = False
            mock_args.simple = False
            mock_args.force_endpoints = None
            mock_parse_args.return_value = mock_args
            
            # Call the function under test
            main()
            
            # Verify find_endpoints was called with the correct default values
            mock_find_endpoints.assert_called_once_with(
                ip_range="192.168.1.0/24",
                include_details=True,
                force_endpoints=None,
                username="admin",
                password="TANDBERG"
            )
