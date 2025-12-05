# EYE Tool v2.0 - Quick Reference Card

## 🎯 New Features at a Glance

### 1. Phone Number Harvesting
```python
from modules.harvester import DataHarvester

harvester = DataHarvester()
result = await harvester.harvest_multiple(urls)

# Access data
emails = result['https://example.com']['emails']
phones = result['https://example.com']['phones']
```

**Supported Formats:**
- `+1-800-123-4567` (US)
- `+91-9876543210` (India)
- `(555) 987-6543` (US with parentheses)
- `020-1234-5678` (UK)

**Auto-Filtered:**
- ❌ Dates: `2023-12-05`
- ❌ Times: `12:34:56`
- ❌ Short numbers: `123-456`

---

### 2. SSL & Security Headers Audit
```python
from modules import audit

result = await audit.check_security('https://example.com')

# Result structure
{
    'ssl_days': 120,              # Days until expiration
    'ssl_status': 'VALID',        # VALID, WARNING, EXPIRED
    'missing_headers': ['CSP'],   # Missing security headers
    'security_score': 90          # 0-100 score
}
```

**Checked Headers:**
1. X-Frame-Options
2. Content-Security-Policy (CSP)
3. Strict-Transport-Security (HSTS)
4. X-Content-Type-Options
5. X-XSS-Protection
6. Referrer-Policy

**SSL Status:**
- `VALID`: > 30 days remaining
- `WARNING`: < 30 days remaining
- `EXPIRED`: Past expiration
- `ERROR`: Connection failed

---

## 📊 Output Examples

### Console Output
```
[+] https://example.com
    📧 Emails: 3 found
    📞 Phones: 2 found

[!] https://api.example.com
    ⚠️  SSL Expires in: 28 days
    🔒 Missing Headers: CSP, HSTS
    📊 Security Score: 60/100
```

### Summary Statistics
```
Emails Harvested: 25
Phones Harvested: 12      ⬅️ NEW
SSL Warnings: 3           ⬅️ NEW
```

---

## 🚀 Command Usage

```bash
# Full scan with all features
python main.py -d example.com --alert

# Skip sensitive file fuzzing (faster)
python main.py -d example.com --no-fuzz

# Test phone extraction
python test_harvester.py
```

---

## 📦 Export Data Structure

### JSON Output
```json
{
    "harvest_data": {
        "https://example.com": {
            "emails": ["info@example.com"],
            "phones": ["+1-800-123-4567"]
        }
    },
    "security_audit": {
        "https://example.com": {
            "ssl_days": 120,
            "ssl_status": "VALID",
            "missing_headers": ["CSP"],
            "security_score": 90
        }
    },
    "statistics": {
        "emails_found": 25,
        "phones_found": 12,
        "ssl_warnings": 3
    }
}
```

---

## ⚡ Performance Specs

| Feature | Concurrency | Timeout |
|---------|-------------|---------|
| Data Harvesting | 50 | 10s |
| Security Audit | 30 | 10s |
| SSL Check | - | 5s |

---

## 🔧 Module Comparison

### OLD vs NEW

| Feature | OLD (`emails.py`) | NEW (`harvester.py`) |
|---------|-------------------|----------------------|
| Email extraction | ✅ | ✅ |
| Phone extraction | ❌ | ✅ |
| Smart filtering | ❌ | ✅ |
| Return structure | Set | Dict with emails + phones |

---

## 📝 Code Migration

```python
# OLD CODE
from modules.emails import EmailHarvester
harvester = EmailHarvester()
emails = await harvester.harvest_multiple(urls)
# Returns: {'url': {email1, email2}}

# NEW CODE
from modules.harvester import DataHarvester
harvester = DataHarvester()
result = await harvester.harvest_multiple(urls)
# Returns: {'url': {'emails': {...}, 'phones': {...}}}

# Access emails
emails = result['url']['emails']
# Access phones
phones = result['url']['phones']
```

---

## 🎨 Icon Reference

| Icon | Meaning |
|------|---------|
| 📧 | Emails found |
| 📞 | Phones found |
| ⚠️ | SSL warning |
| ❌ | SSL expired |
| 🔒 | Security headers |
| 📊 | Security score |
| ✅ | Success |
| ❌ | Filtered out |

---

## 🔍 Security Score Calculation

```
Base Score: 100

Deductions:
- Expired SSL: -30 points
- SSL < 30 days: -15 points
- Missing header: -10 points each

Example:
100 - 15 (SSL warning) - 20 (2 missing headers) = 65/100
```

---

## 📚 Documentation

- `UPGRADE_V2.md` - Full technical documentation
- `UPGRADE_COMPLETE.md` - Upgrade summary
- `README.md` - General tool documentation
- `test_harvester.py` - Test script

---

**Quick Start**: `python main.py -d example.com --alert`  
**Version**: 2.0 | **Status**: Production Ready ✅
