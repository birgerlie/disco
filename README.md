# Disco
Network Discovery Prototype

## Current Status (May 2025)

The project currently has one implemented module:

- **Video Endpoint Discovery** - A tool for scanning networks to identify video conferencing endpoints

## Components

### Video Endpoint Discovery

A robust network scanner that identifies video conferencing equipment (Cisco, Polycom, Tandberg, etc.) on a network. It uses port scanning and web authentication to detect and verify endpoints.

Key features:
- Network scanning with multi-threading for performance
- Authentication using default or custom credentials (default: admin/TANDBERG)
- Detection of common video conferencing ports (80, 443, 5060, 5061, 1720)
- JSON output option for integration with other systems

## How to Use

### Video Endpoint Discovery

```bash
# Navigate to the module directory
cd video_endpoint_discovery

# Set up environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run a basic network scan
python -m discovery_system.scanner_cli

# Scan a specific IP range
python -m discovery_system.scanner_cli --range 192.168.1.0/24

# Scan with custom credentials
python -m discovery_system.scanner_cli --username admin --password cisco123
```

For detailed usage instructions, see the [Video Endpoint Discovery README](./video_endpoint_discovery/README.md).

## Development Status

This project follows test-first development practices using pytest. All modules have comprehensive test coverage.

Current development focus:
- Enhancing detection capabilities for different vendor endpoints
- Improving authentication methods for secure endpoints
- Adding more discovery modules for other network device types
