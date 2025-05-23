# Video Endpoint Discovery System

This project aims to discover video conferencing endpoints on a local network. It can automatically detect and identify video endpoints from various manufacturers like Cisco, Polycom, Tandberg, and more.

## Features

- Automated scanning of local networks for video conferencing endpoints
- Detection based on common endpoint ports (80, 443, 5060, 5061, 1720)
- Authentication using default or custom credentials
- Ability to force specific IPs to be classified as endpoints for testing
- Simplified or detailed output formats including JSON

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install requests pytest
   ```

## Running the discovery

The discovery system provides a command-line interface with several options:

### Basic usage

```bash
# Auto-detect and scan local network
python -m discovery_system.scanner_cli

# Scan a specific network range
python -m discovery_system.scanner_cli --range 192.168.1.0/24

# Scan a specific IP (e.g., known Cisco endpoint)
python -m discovery_system.scanner_cli --range 172.17.20.72/32
```

### Authentication

By default, the scanner uses common credentials (username: `admin`, password: `TANDBERG`) for video endpoints. You can override these:

```bash
python -m discovery_system.scanner_cli --username myuser --password mypass
```

### Output options

```bash
# Output in JSON format
python -m discovery_system.scanner_cli --json

# Simplified output (less detail)
python -m discovery_system.scanner_cli --simple
```

### Advanced options

```bash
# Force a specific IP to be classified as a video endpoint
python -m discovery_system.scanner_cli --force-endpoint 192.168.1.100

# Combine multiple options
python -m discovery_system.scanner_cli --range 10.0.0.0/24 --json --username admin --password cisco123
```

## Running tests

This project uses pytest for testing, following test-first development principles:

```bash
# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_discovery.py

# Run with verbose output
python -m pytest -v
```

## Known endpoints

For testing and development purposes, here's a list of known endpoints:

- Cisco endpoint at 172.17.20.72 (username: admin, default password)

## Troubleshooting

If no endpoints are found, try the following:

1. Verify network connectivity to the target devices
2. Try specifying the correct network range using the `--range` parameter
3. Check if different credentials are needed using the `--username` and `--password` parameters
4. Use the `--force-endpoint` parameter to test with a specific IP address
TANDBERG