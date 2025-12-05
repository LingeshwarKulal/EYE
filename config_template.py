"""
EYE - Configuration Template
Copy this file to config.py and customize your settings
"""

# Scanning Configuration
MAX_CONCURRENT = 100
MAX_CONCURRENT_SCANS = 10
SCAN_TIMEOUT = 30
REQUEST_TIMEOUT = 30

# Port Scanning
PORT_LIST = [80, 443, 22, 21, 3306, 8080, 8443, 5432, 27017, 6379]
PORT_TIMEOUT = 3
CRITICAL_PORTS = [22, 3306, 5432, 27017, 6379]

# API URLs
CRT_SH_URL = "https://crt.sh/?q=%.{domain}&output=json"

# HTTP Headers
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Sensitive File Paths
SENSITIVE_PATHS = [
    "/.env",
    "/.git/HEAD",
    "/.git/config",
    "/admin",
    "/admin.php",
    "/phpinfo.php",
    "/config.php",
    "/config.json",
    "/backup.zip",
    "/backup.sql",
    "/db_backup.sql",
    "/.htaccess",
    "/.htpasswd",
    "/web.config",
    "/robots.txt",
    "/sitemap.xml",
    "/.DS_Store",
    "/composer.json",
    "/package.json",
    "/.env.local",
    "/.env.production",
    "/credentials.json",
    "/settings.py",
    "/config.yml",
    "/docker-compose.yml",
    "/Dockerfile",
]

# Screenshot Configuration
SCREENSHOT_DIR = "output/screenshots"
BROWSER_TIMEOUT = 10
WINDOW_SIZE = "1920,1080"

# Output Configuration
VERBOSE = True
SAVE_JSON = False

# Watcher Mode
DEFAULT_MONITOR_INTERVAL = 21600  # 6 hours in seconds
