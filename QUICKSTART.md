# 🚀 Quick Start Guide - EYE Tool

## Installation Steps (Windows)

### 1️⃣ Install Python 3.9+
```powershell
# Check if Python is installed
python --version

# If not installed, download from: https://www.python.org/downloads/
```

### 2️⃣ Install Dependencies
```powershell
# Navigate to EYE directory
cd d:\EYE

# Install required packages
pip install -r requirements.txt
```

### 3️⃣ Install Chrome Browser
Download and install from: https://www.google.com/chrome/

### 4️⃣ Install ChromeDriver

**Option A: Automatic (Recommended)**
```powershell
pip install webdriver-manager
```

**Option B: Manual**
1. Check your Chrome version: `chrome://version/`
2. Download matching ChromeDriver: https://chromedriver.chromium.org/downloads
3. Extract and add to PATH or place in project directory

### 5️⃣ Run Setup Script
```powershell
python setup.py
```

## 🎯 Usage Examples

### Basic Scan
```powershell
python main.py -d example.com
```

### Test with Your Domain
```powershell
python main.py -d yourdomain.com
```

## 📊 What Happens During a Scan?

1. **Logo Display** - Shows the EYE banner
2. **Subdomain Discovery** - Finds subdomains via Certificate Transparency logs
3. **Port Scanning** - Checks for open ports (80, 443, 22, 21, 3306, 8080)
4. **Screenshot Capture** - Takes screenshots of web services
5. **Results** - Displays summary and saves screenshots to `output/screenshots/`

## 🔧 Common Issues & Solutions

### Issue: "ChromeDriver not found"
**Solution:**
```powershell
# Install webdriver-manager
pip install webdriver-manager

# OR download manually from:
# https://chromedriver.chromium.org/downloads
```

### Issue: "Module not found"
**Solution:**
```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: "Permission denied" or "Access denied"
**Solution:**
```powershell
# Run PowerShell as Administrator
# OR use virtual environment:
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: "SSL Certificate error"
**Solution:** The tool automatically handles SSL errors. If issues persist, check your internet connection.

### Issue: "Rate limited by crt.sh"
**Solution:** Wait a few minutes and try again. The API has rate limits.

## 📁 Output Location

All results are saved to:
```
d:\EYE\output\screenshots\
```

Each screenshot is named after the domain:
- `www_example_com.png`
- `api_example_com.png`
- etc.

## ⚡ Performance Tips

1. **Faster Scans**: Reduce `MAX_CONCURRENT` in `config.py` if network is slow
2. **Skip Screenshots**: Comment out visual recon in `main.py` if only need port data
3. **Custom Ports**: Edit `PORT_LIST` in `config.py` to scan specific ports only

## 🎓 Learning Path

1. Start with a domain you own
2. Review the `PRD.md` for architecture details
3. Explore `modules/` directory to understand each component
4. Customize `config.py` for your needs
5. Check `output/screenshots/` for results

## 🆘 Get Help

```powershell
# Show help message
python main.py --help

# Check tool version
python main.py -d test.com  # Will show version in banner
```

## ✅ Verification Checklist

- [ ] Python 3.9+ installed
- [ ] Dependencies installed (`pip list`)
- [ ] Chrome browser installed
- [ ] ChromeDriver available
- [ ] `output/screenshots/` directory exists
- [ ] Can run `python main.py --help`

## 🎉 Ready to Go!

Once everything is set up, run your first scan:

```powershell
python main.py -d example.com
```

**Important:** Only scan domains you own or have permission to test!

---

**Need more help?** Check `README.md` for detailed documentation.
