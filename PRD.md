# Product Requirements Document (PRD)
## EYE - Automated Attack Surface Manager

---

## 1. Project Overview

### 1.1 Project Name
**EYE** - Automated Vulnerability Assessment & Reconnaissance Tool

### 1.2 Version
v1.0

### 1.3 Creator
JohyRipper

### 1.4 Purpose
EYE is a high-performance, CLI-based reconnaissance framework designed for security professionals and penetration testers. It automates the attack surface discovery process by identifying subdomains, scanning ports, and capturing visual evidence of discovered assets.

---

## 2. Business Objectives

### 2.1 Primary Goals
- Automate subdomain enumeration for comprehensive attack surface mapping
- Perform rapid, asynchronous port scanning across multiple targets
- Capture visual evidence (screenshots) of discovered web assets
- Provide a professional, user-friendly CLI interface
- Generate organized output for further analysis

### 2.2 Target Users
- Security Engineers
- Penetration Testers
- Red Team Operators
- Bug Bounty Hunters
- Security Researchers

---

## 3. Functional Requirements

### 3.1 Core Features

#### F1: Banner Display
- **Priority:** High
- **Description:** Display a branded ASCII art logo with project information
- **Components:**
  - Pyfiglet-generated "EYE" text (slant font)
  - Custom ASCII eye artwork
  - Version information
  - Creator attribution

#### F2: Subdomain Discovery
- **Priority:** Critical
- **Description:** Enumerate subdomains for a given target domain
- **Method:** Certificate Transparency (CT) logs via crt.sh API
- **Requirements:**
  - Asynchronous HTTP requests
  - Automatic deduplication
  - Wildcard subdomain detection (%.domain)
  - Error handling for API failures

#### F3: Port Scanning
- **Priority:** Critical
- **Description:** Scan common service ports on discovered subdomains
- **Target Ports:** 80, 443, 22, 21, 3306, 8080
- **Requirements:**
  - Asynchronous TCP connection attempts
  - Concurrent connection limiting (100 simultaneous)
  - Timeout handling (default: 3 seconds)
  - Status reporting (open/closed)

#### F4: Visual Reconnaissance
- **Priority:** High
- **Description:** Capture screenshots of web services
- **Requirements:**
  - Headless browser automation (Chrome)
  - Support for HTTP/HTTPS protocols
  - Automatic screenshot storage
  - Error handling for inaccessible sites

#### F5: CLI Interface
- **Priority:** High
- **Description:** Command-line argument parsing
- **Arguments:**
  - `-d, --domain`: Target domain (required)
- **Output:**
  - Real-time progress indicators
  - Colored console output
  - Summary statistics

### 3.2 Data Management

#### D1: Output Structure
```
output/
├── screenshots/
│   ├── subdomain1_com.png
│   ├── subdomain2_com.png
│   └── ...
└── (future: JSON/CSV reports)
```

#### D2: Data Storage
- Screenshots saved as PNG files
- Filename format: `{sanitized_domain}.png`
- Organized by target domain (future enhancement)

---

## 4. Non-Functional Requirements

### 4.1 Performance
- **Concurrency:** Support up to 100 concurrent operations
- **Efficiency:** Utilize asyncio for non-blocking I/O
- **Scalability:** Handle 100+ subdomains per scan

### 4.2 Reliability
- **Error Handling:** Graceful degradation on service failures
- **Timeout Management:** Prevent hanging on unresponsive targets
- **Network Resilience:** Retry logic for transient failures

### 4.3 Security
- **Ethical Use:** Tool intended for authorized testing only
- **Rate Limiting:** Respect target infrastructure
- **Stealth:** Configurable delays (future)

### 4.4 Usability
- **Installation:** Simple pip-based dependency installation
- **Documentation:** Clear usage instructions
- **Feedback:** Real-time progress updates

---

## 5. Technical Architecture

### 5.1 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | Python 3.9+ | Core development |
| Async Framework | AsyncIO | Concurrency management |
| HTTP Client | Aiohttp | Async HTTP requests |
| DNS Library | DNSPython | DNS resolution |
| Browser Automation | Selenium | Screenshot capture |
| CLI Framework | Argparse | Command parsing |
| UI Library | Rich | Console formatting |
| ASCII Art | Pyfiglet | Banner generation |
| Data Processing | Pandas | Report generation (future) |

### 5.2 Module Architecture

```
EYE/
├── main.py                 # Entry point & orchestration
├── config.py               # Global configuration
├── requirements.txt        # Dependencies
├── PRD.md                  # This document
├── modules/
│   ├── __init__.py
│   ├── banner.py           # Logo display
│   ├── subdomain.py        # Subdomain enumeration
│   ├── scanner.py          # Port scanning
│   └── visual.py           # Screenshot capture
└── output/
    └── screenshots/
```

### 5.3 Data Flow

1. **Initialization:**
   - Parse CLI arguments
   - Display banner
   - Initialize modules

2. **Subdomain Discovery Phase:**
   - Query crt.sh API
   - Parse JSON response
   - Deduplicate results
   - Return subdomain set

3. **Parallel Reconnaissance Phase:**
   - **Thread A:** Port Scanning
     - Iterate through subdomains
     - Attempt connections to target ports
     - Report open ports
   - **Thread B:** Visual Reconnaissance
     - Launch headless browser
     - Navigate to HTTP/HTTPS URLs
     - Capture screenshots
     - Save to output directory

4. **Completion:**
   - Display summary statistics
   - Clean up resources
   - Exit gracefully

---

## 6. Module Specifications

### 6.1 modules/banner.py

**Class/Function:** `show_logo()`

**Responsibilities:**
- Render "EYE" text using pyfiglet (slant font)
- Display ASCII eye artwork
- Show version and creator information
- Use Rich console for colored output

**Output Format:**
```
    ______  _______   __
   / ____/ / ____/\ \ / /
  / __/   / __/    \ V / 
 / /___  / /___     | |  
/_____/ /_____/     |_|  

       _______
    .-'       '-.
   /   (_>O<_)   \
  |     \   /     |
   \     '-'     /
    '-._______.-'

─────────────────────────────────
Automated Attack Surface Manager v1.0
Created by: JohyRipper
```

### 6.2 modules/subdomain.py

**Class:** `SubdomainHunter`

**Methods:**
- `async find_subdomains(domain: str) -> set`

**Logic:**
1. Construct crt.sh API URL: `https://crt.sh/?q=%.{domain}&output=json`
2. Send async GET request
3. Parse JSON response
4. Extract `name_value` fields
5. Handle wildcard entries (`*.domain`)
6. Deduplicate using set
7. Return unique subdomain list

**Error Handling:**
- Network failures
- Invalid JSON
- Empty responses

### 6.3 modules/scanner.py

**Class:** `PortScanner`

**Attributes:**
- `ports: list = [80, 443, 22, 21, 3306, 8080]`
- `timeout: int = 3`
- `semaphore: asyncio.Semaphore(100)`

**Methods:**
- `async scan_port(host: str, port: int) -> tuple`
- `async scan_host(host: str) -> dict`
- `async scan_multiple(hosts: list) -> list`

**Logic:**
1. Use `asyncio.open_connection(host, port)`
2. Limit concurrency with semaphore
3. Return (host, port, status) tuple
4. Aggregate results per host

### 6.4 modules/visual.py

**Class:** `VisualRecon`

**Attributes:**
- `output_dir: str = "output/screenshots"`

**Methods:**
- `capture_screenshot(url: str) -> bool`
- `async capture_multiple(urls: list) -> int`

**Chrome Options:**
- `--headless`
- `--disable-gpu`
- `--no-sandbox`
- `--disable-dev-shm-usage`
- `--window-size=1920,1080`

**Logic:**
1. Initialize WebDriver with options
2. Navigate to URL (timeout: 10s)
3. Capture full-page screenshot
4. Save to `output/screenshots/{sanitized_url}.png`
5. Close driver
6. Return success/failure status

### 6.5 main.py

**Workflow:**
```python
async def main(domain):
    # 1. Display banner
    show_logo()
    
    # 2. Subdomain discovery
    console.print(f"[+] Target: {domain}")
    hunter = SubdomainHunter()
    subdomains = await hunter.find_subdomains(domain)
    
    # 3. Parallel reconnaissance
    console.print("[+] Starting Scan...")
    scanner = PortScanner()
    visual = VisualRecon()
    
    results = await asyncio.gather(
        scanner.scan_multiple(subdomains),
        visual.capture_multiple(subdomains)
    )
    
    # 4. Display results
    console.print("[+] Scan Complete!")
```

---

## 7. Configuration (config.py)

```python
# Scanning Configuration
PORT_LIST = [80, 443, 22, 21, 3306, 8080]
PORT_TIMEOUT = 3
MAX_CONCURRENT = 100

# Screenshot Configuration
SCREENSHOT_DIR = "output/screenshots"
BROWSER_TIMEOUT = 10
WINDOW_SIZE = "1920,1080"

# API Configuration
CRT_SH_URL = "https://crt.sh/?q=%.{domain}&output=json"
REQUEST_TIMEOUT = 30

# Output Configuration
VERBOSE = True
SAVE_JSON = False
```

---

## 8. Dependencies (requirements.txt)

```
aiohttp>=3.9.0
dnspython>=2.4.0
selenium>=4.15.0
rich>=13.7.0
pyfiglet>=1.0.2
pandas>=2.1.0
```

---

## 9. Installation & Usage

### 9.1 Installation
```bash
pip install -r requirements.txt
```

### 9.2 Usage
```bash
python main.py -d example.com
```

### 9.3 Output
- Console: Real-time progress and results
- Files: Screenshots in `output/screenshots/`

---

## 10. Future Enhancements

### Phase 2 Features
- [ ] JSON/CSV report generation
- [ ] Vulnerability detection (CVE checks)
- [ ] Technology fingerprinting (Wappalyzer)
- [ ] DNS record enumeration
- [ ] WHOIS information gathering
- [ ] Multi-domain batch processing
- [ ] Custom wordlist support
- [ ] API rate limiting controls
- [ ] Proxy support
- [ ] User-agent rotation

### Phase 3 Features
- [ ] Web dashboard
- [ ] Database integration (SQLite/PostgreSQL)
- [ ] Historical scan comparison
- [ ] Automated scheduling
- [ ] Alert notifications (Discord/Slack)
- [ ] Plugin architecture

---

## 11. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Rate limiting by crt.sh | Medium | Implement retry logic + delays |
| Chrome driver compatibility | High | Pin selenium version, add setup guide |
| Network instability | Medium | Comprehensive timeout handling |
| Large subdomain sets (1000+) | Medium | Pagination, progress tracking |
| Legal/ethical misuse | High | Clear disclaimer, ethical guidelines |

---

## 12. Success Metrics

- **Performance:** Scan 100 subdomains in < 5 minutes
- **Accuracy:** 95%+ subdomain discovery rate
- **Reliability:** < 5% failure rate on valid targets
- **Usability:** Installation in < 2 minutes

---

## 13. Compliance & Ethics

**DISCLAIMER:**
This tool is intended for authorized security testing only. Users must:
- Obtain written permission before scanning targets
- Comply with local laws and regulations
- Respect rate limits and target infrastructure
- Use responsibly and ethically

Unauthorized use may violate:
- Computer Fraud and Abuse Act (CFAA)
- Computer Misuse Act
- Local cybersecurity laws

---

## 14. Glossary

- **CT Logs:** Certificate Transparency logs (public audit trail of SSL certificates)
- **Attack Surface:** All points where an unauthorized user could try to enter/extract data
- **Headless Browser:** Browser without GUI for automated testing
- **AsyncIO:** Python's asynchronous I/O framework
- **Reconnaissance:** Information gathering phase of security assessment

---

**Document Version:** 1.0  
**Last Updated:** December 5, 2025  
**Status:** Approved for Development
