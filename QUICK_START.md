# 🎯 EYE AI Integration - Quick Start

## ✅ What Was Automated

### Before (Manual Process):
1. Run scan: `python main.py -d example.com`
2. Copy JSON output
3. Manually open Gemini AI website
4. Paste data into chat
5. Copy AI response
6. Manually create report
7. Paste AI insights

### After (Fully Automated):
1. Set API key: `$env:GEMINI_API_KEY="your-key"`
2. Run scan: `python main.py -d example.com`
3. **Everything else happens automatically!**

## 🔄 Automatic Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                     USER RUNS SCAN                          │
│             python main.py -d example.com                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: Subdomain Discovery (crt.sh)                     │
│  Phase 2: Port Scanning (asyncio)                          │
│  Phase 3: Advanced Scanning (parallel)                     │
│    ├─ Sensitive File Fuzzing                               │
│    ├─ Data Harvesting (emails/phones)                      │
│    ├─ CORS Testing                                         │
│    ├─ Security Audit (SSL/Headers)                         │
│    └─ Social Media Extraction                              │
│  Phase 3.5: Spring Boot Actuator Hunt                      │
│  Phase 3.6: Access Control Bypass Attempts                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│        DATA COLLECTION (export_data dictionary)             │
│  • 43 subdomains discovered                                 │
│  • 28 active hosts                                          │
│  • 74 open ports                                            │
│  • 2 sensitive files                                        │
│  • 1 actuator endpoint                                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         AUTOMATIC: JSON/CSV Export                          │
│  Saves: output/scan_results.json                           │
│  Saves: output/scan_results.csv                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: AI Security Analysis (AUTOMATIC)                 │
│                                                             │
│  1. AIAnalyst.prepare_scan_summary(export_data)            │
│     └─ Converts dict to text summary (≤4000 chars)         │
│                                                             │
│  2. Gemini API Call (google.generativeai)                  │
│     └─ Prompt: "Act as Senior Pen-Tester..."              │
│     └─ Model: gemini-pro                                   │
│                                                             │
│  3. Response: AI Executive Summary                         │
│     └─ Risk assessment + recommendations                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│     AUTOMATIC: HTML Report Generation                       │
│                                                             │
│  HTMLReporter.generate_report(export_data, ai_summary)     │
│                                                             │
│  Template sections:                                         │
│  ┌────────────────────────────────────────────────┐       │
│  │ 🤖 AI Executive Summary                        │       │
│  │    (Gemini's professional analysis)            │       │
│  ├────────────────────────────────────────────────┤       │
│  │ ⚠️ Risk Assessment (Score: 85/100)            │       │
│  ├────────────────────────────────────────────────┤       │
│  │ 📊 Statistics Dashboard                        │       │
│  ├────────────────────────────────────────────────┤       │
│  │ 🔥 Sensitive Files Exposed                     │       │
│  ├────────────────────────────────────────────────┤       │
│  │ 🔴 Spring Boot Actuators                       │       │
│  ├────────────────────────────────────────────────┤       │
│  │ 🔓 Access Control Bypasses                     │       │
│  ├────────────────────────────────────────────────┤       │
│  │ 🔍 Port Scan Results Table                     │       │
│  └────────────────────────────────────────────────┘       │
│                                                             │
│  Saves: output/security_report.html                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    SCAN COMPLETE                            │
│                                                             │
│  [+] Results saved to output/ directory                    │
│  [+] HTML Report generated: output/security_report.html    │
│  [+] Thank you for using EYE! Stay ethical. 🔍             │
└─────────────────────────────────────────────────────────────┘
```

## 📋 File Structure (Updated)

```
D:\EYE\
├── main.py                          # ✅ UPDATED: Imports AIAnalyst + HTMLReporter
│   └── Phase 4: AI Analysis added after data export
│
├── modules/
│   ├── ai_gemini.py                 # 🆕 NEW: AI Analyst class
│   │   ├── prepare_scan_summary()   #     Converts scan data to text
│   │   └── analyze_scan_results()   #     Calls Gemini API automatically
│   │
│   ├── reporter.py                  # 🆕 NEW: HTML Report Generator
│   │   ├── generate_report()        #     Creates dashboard with AI section
│   │   └── Jinja2 template          #     Professional HTML + CSS
│   │
│   ├── [all other modules unchanged]
│
├── config.py                        # ✅ UPDATED: Added AI configuration docs
├── requirements.txt                 # ✅ UPDATED: Added google-generativeai, jinja2
├── AI_SETUP_GUIDE.md                # 🆕 NEW: Complete setup instructions
└── QUICK_START.md                   # 🆕 NEW: This file
```

## 🚀 Test It Now (3 Steps)

### Step 1: Get API Key (30 seconds)
```
Visit: https://makersuite.google.com/app/apikey
Click: "Create API Key"
Copy: Your API key
```

### Step 2: Set Environment Variable
```powershell
$env:GEMINI_API_KEY="paste-your-api-key-here"
```

### Step 3: Run a Test Scan
```powershell
python main.py -d example.com --no-fuzz
```

## 📝 Expected Output

```
🔍 EYE - Automated Attack Surface Manager v3.0
   Created by John Ripper

[*] Target Domain: example.com
[*] Telegram Alerts: Enabled

═══ Phase 1: Subdomain Discovery ═══
[+] Found 5 subdomains via Certificate Transparency

═══ Phase 2: Port Scanning ═══
[*] Starting port scanning...
[+] Active Hosts: 3/5
[+] Total Open Ports: 12

═══ Phase 3: Advanced Scanning ═══
[*] Skipping fuzzing (--no-fuzz flag set)
[+] Harvested 8 emails and 3 phone numbers
[+] Found 2 social media profiles

═══ Phase 4: AI Security Analysis ═══          ← NEW!
[*] Preparing scan data for AI analysis...      ← NEW!
[*] Querying Gemini AI for security analysis... ← NEW!
[✓] AI analysis completed successfully!         ← NEW!

[*] Generating HTML security report...          ← NEW!
[+] HTML Report generated: output/security_report.html ← NEW!
[*] Open the HTML file in your browser to view the full dashboard

[+] Results saved to output/ directory
[+] Thank you for using EYE! Stay ethical. 🔍
```

## 🎨 What's in the HTML Report

### 1. AI Executive Summary (at the top)
```
RISK ASSESSMENT: MEDIUM

This security assessment reveals several areas requiring attention. 
The target has 12 open ports across 3 active hosts, indicating a 
moderate attack surface.

Key Findings:
• No sensitive files exposed (positive finding)
• Standard ports detected (22, 80, 443)
• No critical vulnerabilities discovered during automated testing

Recommendations:
1. Ensure SSH (port 22) has strong authentication enabled
2. Review web service configurations for security headers
3. Consider implementing additional monitoring for the active services
```

### 2. Visual Dashboard
- **Risk Badge**: Color-coded (🔴 CRITICAL, 🟠 HIGH, 🟡 MEDIUM, 🟢 LOW)
- **Statistics Cards**: Beautiful gradient boxes showing key metrics
- **Interactive Tables**: Sortable port scan results
- **Color-Coded Severity**: Red for critical, yellow for medium, green for low

### 3. Detailed Sections
- Sensitive Files (if found)
- Spring Boot Actuators (if found)
- Access Control Bypasses (if found)
- CORS Vulnerabilities (if found)
- Port Scan Results (always)
- Data Exposure Summary (emails/phones counts)

## 🔒 Security Notes

### What Gets Sent to Gemini:
✅ **Sent:** Summary statistics (counts, numbers)
✅ **Sent:** Vulnerability types (e.g., ".env file exposed")
✅ **Sent:** Port numbers and services
✅ **Sent:** Severity levels

❌ **NOT Sent:** Actual harvested emails
❌ **NOT Sent:** Phone numbers
❌ **NOT Sent:** Raw HTML/page content
❌ **NOT Sent:** API keys or credentials

### Data Truncation:
- Maximum 4000 characters sent to API
- Only summary data, not full scan output
- Sensitive details are counts only (not actual data)

## 🎯 Use Cases

### 1. Bug Bounty Reporting
- Run scan on target
- Get AI-generated executive summary
- Include HTML report in submission
- Professional presentation

### 2. Red Team Assessments
- Quick reconnaissance + AI analysis
- Identify critical issues fast
- Professional client reports

### 3. Security Audits
- Automated scanning of infrastructure
- AI helps prioritize findings
- Beautiful reports for stakeholders

### 4. Learning & Training
- See how AI interprets findings
- Learn security terminology
- Understand risk assessment

## 🛑 If Something Goes Wrong

### No AI Analysis?
```
[!] Gemini API key not found. Skipping AI analysis.
```
**Fix:** Set the `GEMINI_API_KEY` environment variable

### API Error?
```
AI Analysis Failed: 429 Too Many Requests
```
**Fix:** Wait 1 minute (free tier: 60 requests/minute)

### Import Error?
```
ModuleNotFoundError: No module named 'google.generativeai'
```
**Fix:** Run `pip install google-generativeai`

### HTML Not Generated?
- Check terminal for error messages
- Verify `jinja2` is installed: `pip install jinja2`
- Look in `output/` folder for any files created

## 📞 Support

For issues or questions:
1. Check `AI_SETUP_GUIDE.md` for detailed setup
2. Review error messages in terminal
3. Verify all dependencies are installed
4. Test API key: https://makersuite.google.com/

## 🎉 That's It!

**The entire pipeline is now automated:**
1. Set `GEMINI_API_KEY` once
2. Run scan
3. Get AI-powered HTML report

**No copying, no pasting, no manual work!** ✅
