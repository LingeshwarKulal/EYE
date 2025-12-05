# EYE - Project Architecture

## 📂 Complete File Structure

```
d:\EYE\
│
├── 📄 main.py                    # Main entry point - orchestrates entire workflow
├── 📄 config.py                  # Global configuration settings
├── 📄 requirements.txt           # Python package dependencies
├── 📄 setup.py                   # Automated setup script
│
├── 📁 modules/                   # Core functionality modules
│   ├── 📄 __init__.py           # Package initializer
│   ├── 📄 banner.py             # ASCII logo and branding display
│   ├── 📄 subdomain.py          # Certificate Transparency subdomain discovery
│   ├── 📄 scanner.py            # Asynchronous port scanning
│   └── 📄 visual.py             # Selenium screenshot capture
│
├── 📁 output/                    # Results directory (created automatically)
│   └── 📁 screenshots/          # Captured webpage screenshots
│       ├── 🖼️ domain1.png
│       ├── 🖼️ domain2.png
│       └── ...
│
├── 📄 README.md                  # Comprehensive documentation
├── 📄 PRD.md                     # Product Requirements Document
├── 📄 QUICKSTART.md              # Quick installation guide
├── 📄 LICENSE                    # MIT License + Disclaimer
└── 📄 .gitignore                 # Git ignore rules

```

## 🔄 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                               │
│                    python main.py -d domain.com                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MAIN.PY (Orchestrator)                        │
│  - Parse arguments                                               │
│  - Validate domain                                               │
│  - Initialize async event loop                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BANNER.PY (Display)                            │
│  - Show ASCII art logo                                           │
│  - Display version info                                          │
│  - Show creator attribution                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│               PHASE 1: SUBDOMAIN DISCOVERY                       │
│                   (SUBDOMAIN.PY)                                 │
│                                                                  │
│  1. Query crt.sh API                                            │
│     └─> GET https://crt.sh/?q=%.domain.com&output=json         │
│                                                                  │
│  2. Parse JSON response                                         │
│     └─> Extract 'name_value' fields                            │
│                                                                  │
│  3. Deduplicate & filter                                        │
│     └─> Remove wildcards, lowercase, unique set                │
│                                                                  │
│  Output: Set{subdomain1, subdomain2, ...}                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│         PHASE 2: PARALLEL RECONNAISSANCE                         │
│                                                                  │
│  ┌─────────────────────────┐   ┌──────────────────────────┐   │
│  │   SCANNER.PY            │   │   VISUAL.PY              │   │
│  │   (Port Scanning)       │   │   (Screenshots)          │   │
│  │                         │   │                          │   │
│  │  For each subdomain:    │   │  For each web service:   │   │
│  │  ├─ Async TCP connect  │   │  ├─ Launch Chrome        │   │
│  │  ├─ Ports: 80,443,...  │   │  ├─ Navigate to URL      │   │
│  │  ├─ Timeout: 3s        │   │  ├─ Wait for load        │   │
│  │  ├─ Max concurrent:100 │   │  ├─ Capture screenshot   │   │
│  │  └─ Return open ports  │   │  └─ Save as PNG          │   │
│  │                         │   │                          │   │
│  │  Output: List of       │   │  Output: Saved files     │   │
│  │  {host, ports, status} │   │  in output/screenshots/  │   │
│  └─────────────────────────┘   └──────────────────────────┘   │
│                    │                        │                   │
│                    └────────┬───────────────┘                   │
│                             │                                   │
│                  asyncio.gather()                               │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESULTS DISPLAY                               │
│  - Summary statistics                                            │
│  - Rich table of open ports                                      │
│  - Screenshot count                                              │
│  - Output directory location                                     │
└─────────────────────────────────────────────────────────────────┘
```

## 🧩 Module Dependencies

```
main.py
├── modules/banner.py
│   ├── rich.console → Console
│   └── pyfiglet → Figlet
│
├── modules/subdomain.py
│   ├── aiohttp → ClientSession
│   ├── asyncio → event loop
│   └── rich.console → Console
│
├── modules/scanner.py
│   ├── asyncio → open_connection, Semaphore
│   ├── rich.console → Console
│   └── rich.table → Table
│
└── modules/visual.py
    ├── selenium → webdriver, Options
    ├── asyncio → to_thread
    └── rich.console → Console
```

## ⚙️ Configuration Hierarchy

```
config.py (Global Settings)
    │
    ├─► PORT_LIST = [80, 443, 22, 21, 3306, 8080]
    │   └─► Used by: scanner.py
    │
    ├─► PORT_TIMEOUT = 3
    │   └─► Used by: scanner.py
    │
    ├─► MAX_CONCURRENT = 100
    │   └─► Used by: scanner.py (Semaphore limit)
    │
    ├─► SCREENSHOT_DIR = "output/screenshots"
    │   └─► Used by: visual.py
    │
    ├─► BROWSER_TIMEOUT = 10
    │   └─► Used by: visual.py
    │
    ├─► WINDOW_SIZE = "1920,1080"
    │   └─► Used by: visual.py
    │
    ├─► CRT_SH_URL = "https://crt.sh/..."
    │   └─► Used by: subdomain.py
    │
    └─► REQUEST_TIMEOUT = 30
        └─► Used by: subdomain.py
```

## 🔐 Security Considerations

```
┌────────────────────────────────────────┐
│        SECURITY LAYERS                 │
├────────────────────────────────────────┤
│  1. Input Validation                   │
│     └─ Sanitize domain input           │
│     └─ Remove protocols                │
│                                        │
│  2. Rate Limiting                      │
│     └─ Semaphore controls (100 max)   │
│     └─ Timeout settings                │
│                                        │
│  3. Error Handling                     │
│     └─ Try-except blocks               │
│     └─ Graceful degradation            │
│                                        │
│  4. Output Sanitization                │
│     └─ Filename sanitization           │
│     └─ Path traversal prevention       │
│                                        │
│  5. Browser Security                   │
│     └─ Headless mode                   │
│     └─ Sandboxing (--no-sandbox)       │
│     └─ Certificate ignore              │
└────────────────────────────────────────┘
```

## 📊 Performance Metrics

```
Typical Scan Timeline:
├─ 00:00 - Logo Display            (instant)
├─ 00:01 - Subdomain Discovery     (2-10s depending on API)
├─ 00:11 - Port Scanning           (10-30s for 50 hosts)
└─ 00:41 - Screenshot Capture      (30-120s for 20 sites)

Total: ~1-3 minutes for typical domain
```

## 🎯 Key Design Decisions

1. **AsyncIO over Threading**
   - Better performance for I/O-bound operations
   - Lower memory footprint
   - Native Python support

2. **Certificate Transparency over DNS Bruteforce**
   - More reliable results
   - No need for wordlists
   - Passive reconnaissance

3. **Selenium over Requests**
   - Handles JavaScript rendering
   - Better screenshot quality
   - Mimics real browser behavior

4. **Rich Library for UI**
   - Beautiful console output
   - Cross-platform compatibility
   - Progress tracking

5. **Modular Architecture**
   - Easy to maintain
   - Testable components
   - Extensible design

## 🔄 Async Execution Model

```
Main Event Loop (asyncio.run)
│
├─► Sequential Phase 1
│   └─ await SubdomainHunter.find_subdomains()
│       └─ Single API call to crt.sh
│
└─► Parallel Phase 2 (asyncio.gather)
    ├─ await PortScanner.scan_multiple()
    │   └─ 100 concurrent port scans
    │       └─ Each uses asyncio.open_connection
    │
    └─ await VisualRecon.capture_multiple()
        └─ Sequential Selenium screenshots
            └─ Each wrapped in asyncio.to_thread
```

## 📦 Package Dependencies Graph

```
EYE Tool
│
├─ aiohttp (>=3.9.0)
│  └─ Used for: Async HTTP requests to crt.sh
│
├─ dnspython (>=2.4.0)
│  └─ Used for: DNS resolution (future feature)
│
├─ selenium (>=4.15.0)
│  └─ Used for: Browser automation & screenshots
│
├─ rich (>=13.7.0)
│  └─ Used for: Console formatting & tables
│
├─ pyfiglet (>=1.0.2)
│  └─ Used for: ASCII art logo
│
└─ pandas (>=2.1.0)
   └─ Used for: Report generation (future feature)
```

---

**Last Updated:** December 5, 2025  
**Version:** 1.0  
**Architecture Status:** Production Ready ✓
