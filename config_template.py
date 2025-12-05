"""
EYE - Configuration Template
Copy this file to config.py and customize your settings
"""

# Scanning Configuration
MAX_CONCURRENT_SCANS = 10
SCAN_TIMEOUT = 30

# Port Scanning
PORT_LIST = [80, 443, 22, 21, 3306, 8080, 8443]
PORT_TIMEOUT = 3

# Watcher Mode
DEFAULT_MONITOR_INTERVAL = 21600  # 6 hours in seconds
