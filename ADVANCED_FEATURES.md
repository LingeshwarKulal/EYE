# 🔥 EYE Advanced Features Guide

## New Features Overview

EYE has been upgraded with 3 powerful advanced features:

### 1. 📱 Telegram Alerts
Receive real-time notifications for critical findings directly on Telegram.

### 2. 🔍 Sensitive File Fuzzing
Automatically detect exposed sensitive files and directories on web servers.

### 3. ⚠️ Critical Port Detection
Get instant alerts when dangerous ports are discovered open.

---

## 📱 Feature 1: Telegram Notifications

### Setup Instructions

#### Step 1: Create a Telegram Bot
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the **Bot Token** (e.g., `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### Step 2: Get Your Chat ID
1. Search for `@userinfobot` on Telegram
2. Start a chat and send `/start`
3. Copy your **Chat ID** (e.g., `123456789`)

#### Step 3: Configure EYE

**Option A: Using .env file (Recommended)**
```bash
# Copy the example file
copy .env.example .env

# Edit .env and add your credentials
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

**Option B: Using config.py**
Edit `config.py` and set:
```python
TELEGRAM_BOT_TOKEN = "your_bot_token_here"
TELEGRAM_CHAT_ID = "your_chat_id_here"
TELEGRAM_ENABLED = True
```

### Usage

Run EYE with the `--alert` flag:
```bash
python main.py -d example.com --alert
```

### Alert Types

**1. Critical Port Alert**
```
🚨 CRITICAL PORT DETECTED
🎯 Host: mail.example.com
🔌 Port: 22
⚠️ Severity: HIGH
```

**2. Sensitive File Alert**
```
🔥 CRITICAL LEAK DETECTED
🌐 URL: https://example.com/.env
📁 File: /.env
🚨 Status: ACCESSIBLE (200 OK)
⚠️ IMMEDIATE ACTION REQUIRED!
```

**3. Scan Complete Summary**
```
✅ SCAN COMPLETE
🎯 Target: example.com
📊 Results:
  • Subdomains: 47
  • Active Hosts: 23
  • Open Ports: 15
  • Screenshots: 12
  • Sensitive Files: 3
```

---

## 🔍 Feature 2: Sensitive File Fuzzing

### What It Does
Automatically checks discovered web services for exposed sensitive files including:

- ✅ `.env` - Environment variables with secrets
- ✅ `.git/HEAD` - Git repository exposure
- ✅ `/admin` - Admin panels
- ✅ `/backup.zip` - Backup files
- ✅ `/config.php` - Configuration files
- ✅ `/phpinfo.php` - PHP information disclosure
- ✅ `/.aws/credentials` - AWS credentials
- ✅ And more...

### Usage

**Fuzzing is enabled by default:**
```bash
python main.py -d example.com
```

**To skip fuzzing:**
```bash
python main.py -d example.com --no-fuzz
```

### Output Example

```
═══ Phase 3: Sensitive File Fuzzing ═══
[*] Starting sensitive file fuzzing on 15 targets...
[*] Checking 13 sensitive paths per target

🔥 CRITICAL: https://example.com/.env (Status: 200, Size: 1024)
🔥 CRITICAL: https://api.example.com/backup.zip (Status: 200, Size: 15360)

[+] Fuzzing complete!
[+] Found 2 sensitive files!

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┓
┃ URL                           ┃ Path        ┃ Status ┃ Severity ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━┩
│ https://example.com/.env      │ /.env       │ 200    │ CRITICAL │
│ https://api.example.com/...   │ /backup.zip │ 200    │ CRITICAL │
└───────────────────────────────┴─────────────┴────────┴──────────┘
```

### Customization

Edit `config.py` to add more paths:
```python
SENSITIVE_PATHS = [
    "/.env",
    "/.git/HEAD",
    "/admin",
    "/your-custom-path",  # Add your own
]
```

---

## ⚠️ Feature 3: Critical Port Detection

### Critical Ports Monitored

| Port  | Service         | Risk                          |
|-------|-----------------|-------------------------------|
| 22    | SSH             | Remote access vulnerability   |
| 3306  | MySQL           | Database exposure             |
| 5432  | PostgreSQL      | Database exposure             |
| 27017 | MongoDB         | NoSQL database exposure       |
| 6379  | Redis           | Cache/database exposure       |

### Automatic Alerts

When critical ports are found:
1. **Console:** Red warning displayed
2. **Telegram:** Instant alert sent (if enabled)

Example output:
```
⚠️ Critical port 22 found on mail.example.com!
⚠️ Critical port 3306 found on db.example.com!
```

### Customization

Edit `config.py` to modify critical ports:
```python
CRITICAL_PORTS = [22, 3306, 5432, 27017, 6379, 8080]  # Add your own
```

---

## 🚀 Complete Usage Examples

### Basic Scan (No Alerts)
```bash
python main.py -d example.com
```

### Advanced Scan with Alerts
```bash
python main.py -d example.com --alert
```

### Scan Without Fuzzing
```bash
python main.py -d example.com --no-fuzz
```

### Full Scan with All Features
```bash
python main.py -d example.com --alert
```

---

## 📊 New Command-Line Arguments

```
usage: main.py [-h] -d DOMAIN [--alert] [--no-fuzz]

options:
  -h, --help            Show help message
  -d DOMAIN, --domain DOMAIN
                        Target domain to scan
  --alert               Enable Telegram alerts for critical findings
  --no-fuzz             Skip sensitive file fuzzing
```

---

## 🔧 Configuration Files

### config.py
```python
# Telegram Configuration
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""
TELEGRAM_ENABLED = False

# Sensitive Paths to Check
SENSITIVE_PATHS = ["/.env", "/.git/HEAD", "/admin", ...]

# Critical Ports
CRITICAL_PORTS = [22, 3306, 5432, 27017, 6379]
```

### .env (Recommended)
```bash
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

---

## 🛡️ Security Best Practices

### ⚠️ Important Warnings

1. **Authorization Required:** Only scan domains you own or have permission to test
2. **Rate Limiting:** The fuzzer sends multiple requests - respect target infrastructure
3. **Legal Compliance:** Unauthorized scanning may violate laws
4. **Telegram Security:** Keep your bot token secret - never commit it to Git

### Safe Usage

✅ **DO:**
- Use on your own infrastructure
- Get written permission before scanning
- Use `--no-fuzz` on sensitive production systems
- Keep credentials in `.env` file (not tracked by Git)

❌ **DON'T:**
- Scan without authorization
- Share your bot token publicly
- Commit `.env` file to version control
- Use aggressive settings on production systems

---

## 🐛 Troubleshooting

### Telegram Alerts Not Working

**Problem:** "Telegram notifications disabled"
```bash
[*] Telegram notifications disabled (no credentials)
```

**Solution:**
1. Verify bot token and chat ID are set
2. Check `.env` file exists and is in the correct format
3. Ensure `TELEGRAM_ENABLED = True` in `config.py`
4. Test bot token with: `https://api.telegram.org/bot<TOKEN>/getMe`

### Fuzzer Finding False Positives

**Problem:** Too many 403 Forbidden alerts

**Solution:**
The fuzzer marks 403 as "MEDIUM" severity. These indicate the file exists but is protected. You can filter these by modifying `modules/fuzzer.py`:

```python
# Only report 200 OK
if response.status == 200:
    return { ... }
# Remove the 403 check
```

### Performance Issues

**Problem:** Fuzzing is slow

**Solution:**
Reduce concurrent requests in `modules/fuzzer.py`:
```python
def __init__(self, timeout=5, max_concurrent=20):  # Reduced from 50
```

---

## 📈 Performance Impact

### Scan Time Comparison

| Feature | Before | After | Increase |
|---------|--------|-------|----------|
| Subdomain Discovery | 5s | 5s | 0s |
| Port Scanning | 30s | 30s | 0s |
| Screenshots | 60s | 60s | 0s |
| **Fuzzing (NEW)** | - | **+45s** | +45s |
| **Total** | ~95s | **~140s** | +45% |

*For 20 active web hosts with 13 paths checked*

### Optimization Tips

1. **Skip fuzzing** on large scans: `--no-fuzz`
2. **Reduce paths** in `config.py`
3. **Adjust concurrency** in fuzzer settings

---

## 📦 Dependencies Added

```
python-dotenv>=1.0.0  # Environment variable management
```

No additional dependencies needed - all features use existing `aiohttp` library!

---

## 🎯 Next Steps

1. **Install new dependency:**
   ```bash
   pip install python-dotenv
   ```

2. **Setup Telegram (optional):**
   ```bash
   copy .env.example .env
   # Edit .env with your credentials
   ```

3. **Test the new features:**
   ```bash
   python main.py -d example.com --alert
   ```

4. **Review findings** in the console and Telegram

---

## 📚 Additional Resources

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [OWASP Top 10 Sensitive Data Exposure](https://owasp.org/www-project-top-ten/)
- [Common Sensitive Files List](https://github.com/danielmiessler/SecLists)

---

**Last Updated:** December 5, 2025  
**Version:** 1.1 (Advanced Features)  
**Status:** Production Ready ✅

---

**Remember: Use these powerful features responsibly and ethically!** 🔍🛡️
