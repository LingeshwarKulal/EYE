# 🔍 EYE - Automated Attack Surface Manager

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

A comprehensive, high-performance reconnaissance framework designed for security professionals and penetration testers. EYE automates attack surface discovery and security assessment through advanced scanning techniques.

## ⚡ Features

### Core Capabilities
- **🌐 Subdomain Discovery**: Certificate Transparency log enumeration
- **🔌 Async Port Scanning**: High-speed multi-threaded scanning
- **🖥️ OS Detection**: TTL-based operating system fingerprinting
- **🔧 Technology Fingerprinting**: Detect web servers, frameworks, CMS (50+ signatures)
- **📊 Rich CLI Interface**: Beautiful console output with progress tracking

### Advanced Security Testing
- **🔒 403/401 Bypass Testing**: 30+ techniques with false positive detection
- **🔴 Spring Boot Actuator Hunt**: Identify exposed actuator endpoints
- **🌐 CORS Testing**: Misconfiguration detection
- **🔐 SSL/TLS Audit**: Certificate validation and security header analysis
- **📁 Sensitive File Discovery**: Automated fuzzing for configs and backups
- **📧 Data Harvesting**: Email and phone extraction with validation
- **👥 Social Media Discovery**: Profile detection across platforms

### Monitoring & Reporting
- **👁️ Watcher Mode**: Continuous monitoring with change detection
- **📄 Multiple Export Formats**: JSON, CSV, HTML reports
- **⚡ High Performance**: Fully asynchronous architecture

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.9+ |
| Async Framework | AsyncIO |
| HTTP Client | Aiohttp |
| Browser Automation | Selenium |
| CLI UI | Rich & Pyfiglet |
| DNS | DNSPython |

## 📋 Requirements

- Python 3.9 or higher
- Chrome/Chromium browser
- ChromeDriver (compatible with your Chrome version)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/LingeshwarKulal/EYE.git
cd EYE
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create Configuration File
**IMPORTANT**: Create `config.py` from the template (required for the tool to run):
```bash
# Linux/Mac
cp config_template.py config.py

# Windows
copy config_template.py config.py
```

You can customize scanning parameters in `config.py` if needed (port ranges, timeouts, etc.).

## 📖 Usage

### Basic Scan
```bash
python eye.py -d target.com
# OR
python main.py -d target.com
```

### Advanced Options
```bash
# Watcher mode (continuous monitoring)
python eye.py -d target.com --monitor --interval 3600

# Skip sensitive file fuzzing
python eye.py -d target.com --no-fuzz

# Monitor mode without fuzzing
python eye.py -d target.com --monitor --no-fuzz
```

### Command-Line Options
```
-d, --domain       Target domain (required)
--subdomains       Enable subdomain enumeration
--watch            Enable continuous monitoring
--interval         Monitoring interval in seconds
--ports            Custom ports to scan
--export           Export formats (json, csv, html)
```

## 📁 Project Structure

```
EYE/
├── main.py                      # Entry point and orchestration
├── config_template.py           # Configuration template
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── modules/
│   ├── __init__.py
│   ├── banner.py                # ASCII logo display
│   ├── subdomain.py             # Subdomain enumeration
│   ├── scanner.py               # Port scanning
│   ├── os_detect.py             # OS fingerprinting
│   ├── tech_stack.py            # Technology detection
│   ├── fuzzer.py                # Sensitive file discovery
│   ├── bypass_403.py            # Access control bypass
│   ├── springboot.py            # Spring Boot actuator hunt
│   ├── harvester.py             # Email/phone extraction
│   ├── socials.py               # Social media discovery
│   ├── cors.py                  # CORS testing
│   ├── audit.py                 # SSL/security audit
│   ├── watcher.py               # Continuous monitoring
│   ├── notifier.py              # Telegram notifications
│   ├── exporter.py              # Report generation
│   └── reporter.py              # Report formatting
└── output/
    ├── scan_results.json        # JSON output
    ├── scan_results.csv         # CSV output
    └── security_report.html     # HTML report
```

## 🔧 Configuration

Copy `config_template.py` to `config.py` and customize:

```python
# Scanning Configuration
MAX_CONCURRENT_SCANS = 10
SCAN_TIMEOUT = 30
PORT_LIST = [80, 443, 22, 21, 3306, 8080]
```

## 🎯 Key Modules

### Scanner Module
- Multi-threaded port scanning
- Service detection
- Banner grabbing

### Bypass Module (403/401)
- 30+ bypass techniques
- False positive detection
- Content analysis for bypassed pages

### Technology Stack Module
- 50+ technology signatures
- Server/framework/CMS detection
- Programming language identification

### Watcher Module
- Continuous monitoring
- Change detection
- State persistence
- Console logging

### Harvester Module
- Email extraction with validation
- Phone number extraction with false positive filtering
- Social media profile discovery

## 📊 Output Formats

### Console Output
Real-time color-coded results with rich formatting and progress tracking

### JSON Export
Structured data with all scan results including subdomains, ports, vulnerabilities, and findings

### CSV Export
Tabular format for spreadsheet analysis and data processing

### HTML Report
Professional security assessment report with organized sections and visual formatting

## 🎯 Workflow

1. **Subdomain Discovery**: Certificate Transparency log enumeration
2. **Port Scanning**: Asynchronous scanning of common service ports
3. **OS Detection**: TTL-based operating system fingerprinting
4. **Technology Fingerprinting**: Identify web stack and frameworks
5. **Security Scanning**: Test for vulnerabilities and misconfigurations
6. **Data Harvesting**: Extract emails, phones, and social profiles
7. **Access Control Testing**: 403/401 bypass attempts
8. **Report Generation**: Export results in multiple formats

## ⚠️ Legal Disclaimer

**FOR AUTHORIZED TESTING ONLY**

This tool is intended for:
- Security professionals conducting authorized assessments
- Bug bounty hunters with proper authorization
- Penetration testers with written permission
- Educational purposes in controlled environments

**You must:**
- ✅ Obtain written permission before scanning any target
- ✅ Comply with all applicable laws and regulations
- ✅ Respect rate limits and target infrastructure
- ✅ Use responsibly and ethically

**Unauthorized use may violate:**
- Computer Fraud and Abuse Act (CFAA)
- Computer Misuse Act
- Local cybersecurity laws

The author is not responsible for misuse or damage caused by this tool.

## 🐛 Troubleshooting

### Connection Issues
- Check network connectivity
- Adjust timeout values in configuration
- Verify DNS resolution

### Rate Limiting
- Use `--interval` flag for watcher mode
- Add delays between requests
- Respect target infrastructure

### Permission Errors
- Ensure write permissions for output directory
- Run with appropriate privileges if needed

### Module Import Errors
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (3.9+ required)

## 🔮 Features

- ✅ Subdomain Discovery (Certificate Transparency)
- ✅ Async Port Scanning
- ✅ OS Detection (TTL-based)
- ✅ Technology Fingerprinting (50+ signatures)
- ✅ Sensitive File Discovery
- ✅ 403/401 Bypass Testing (30+ techniques)
- ✅ False Positive Detection
- ✅ Spring Boot Actuator Hunt
- ✅ CORS Misconfiguration Testing
- ✅ SSL/TLS Security Audit
- ✅ Data Harvesting (Email/Phone)
- ✅ Social Media Profile Discovery
- ✅ Watcher Mode (Continuous Monitoring)
- ✅ Multiple Export Formats (JSON/CSV/HTML)

## 📝 License

MIT License - See LICENSE file for details

## 👨‍💻 Author

Created by John Ripper for the security community

## 🙏 Acknowledgments

- Certificate Transparency logs (crt.sh)
- Python AsyncIO community
- Rich library for CLI output
- Security research community

## 📧 Support

For issues or contributions:
- Open an issue on GitHub
- Submit a pull request

---

**Remember: Always obtain proper authorization before scanning. Use EYE ethically and responsibly!** 🔍🛡️
