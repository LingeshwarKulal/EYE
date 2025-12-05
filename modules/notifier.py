"""
EYE - Telegram Notification Module
Sends alerts via Telegram when critical findings are discovered
"""

import os
import aiohttp
import asyncio
from rich.console import Console
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_ENABLED

console = Console()


class TelegramNotifier:
    """
    Sends notifications via Telegram Bot API
    """
    
    def __init__(self):
        """
        Initialize Telegram notifier with credentials from config or environment
        """
        # Check environment variables first, then config
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', TELEGRAM_BOT_TOKEN)
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', TELEGRAM_CHAT_ID)
        self.enabled = TELEGRAM_ENABLED and self.bot_token and self.chat_id
        
        if not self.enabled:
            console.print("[*] [yellow]Telegram notifications disabled (no credentials)[/yellow]")
    
    async def send_telegram_alert(self, message):
        """
        Send a message via Telegram Bot API
        
        Args:
            message (str): Message to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        console.print("[+] [green]Telegram alert sent successfully[/green]")
                        return True
                    else:
                        console.print(f"[!] [yellow]Telegram API returned status {response.status}[/yellow]")
                        return False
                        
        except Exception as e:
            console.print(f"[!] [red]Failed to send Telegram alert: {str(e)}[/red]")
            return False
    
    async def send_critical_port_alert(self, host, port):
        """
        Send alert for critical port discovery
        
        Args:
            host (str): Target host
            port (int): Critical port number
        """
        port_info = {
            22: ("SSH", "Remote Access"),
            3306: ("MySQL", "Database"),
            5432: ("PostgreSQL", "Database"),
            27017: ("MongoDB", "NoSQL Database"),
            6379: ("Redis", "Cache/DB")
        }
        
        service, desc = port_info.get(port, ("Unknown", "Service"))
        
        message = f"""
🚨 *CRITICAL PORT DETECTED* 🚨

━━━━━━━━━━━━━━━━━━━━━━
🎯 *Target:* `{host}`
🔌 *Port:* `{port}`
📡 *Service:* {service}
📋 *Type:* {desc}
━━━━━━━━━━━━━━━━━━━━━━

⚠️ *SEVERITY:* 🔴 HIGH

⚡ *Action Required:*
This critical port is publicly accessible and should be protected immediately\!

🛡️ *Recommendations:*
• Close port or restrict access
• Use firewall rules
• Enable VPN/IP whitelist
• Monitor for suspicious activity

🕒 *Detected:* Now
"""
        await self.send_telegram_alert(message)
    
    async def send_scan_complete(self, domain, stats):
        """
        Send scan completion summary
        
        Args:
            domain (str): Target domain
            stats (dict): Scan statistics
        """
        subdomains = stats.get('subdomains', 0)
        active = stats.get('active_hosts', 0)
        ports = stats.get('open_ports', 0)
        screenshots = stats.get('screenshots', 0)
        sensitive = stats.get('sensitive_files', 0)
        
        # Status emoji based on findings
        status = "🟢 CLEAN" if sensitive == 0 else "🔴 ISSUES FOUND"
        alert_msg = "⚠️ *ALERT:* Review sensitive files immediately!" if sensitive > 0 else "✨ *No critical issues detected*"
        
        message = f"""
✅ *SCAN COMPLETE* ✅

━━━━━━━━━━━━━━━━━━━━━━
🎯 *Target Domain*
`{domain}`

━━━━━━━━━━━━━━━━━━━━━━
📊 *RECONNAISSANCE RESULTS*

🌐 *Subdomains Found:* {subdomains}
   └─ Total domains discovered

💻 *Active Hosts:* {active}
   └─ Responding to requests

🔌 *Open Ports:* {ports}
   └─ Accessible services

🔥 *Sensitive Files:* {sensitive}
   └─ Exposed critical files

━━━━━━━━━━━━━━━━━━━━━━
📈 *ATTACK SURFACE STATUS*
{status}

🕒 *Completed:* Just now
🔍 *Tool:* EYE v1\\.1

━━━━━━━━━━━━━━━━━━━━━━
{alert_msg}

📁 Results saved to output directory
"""
        await self.send_telegram_alert(message)
    
    async def send_sensitive_file_alert(self, url, path):
        """
        Send alert for sensitive file discovery
        
        Args:
            url (str): Base URL
            path (str): Sensitive file path
        """
        # File type specific warnings
        file_risks = {
            "/.env": ("Environment Variables", "May contain API keys, passwords, database credentials"),
            "/.git/HEAD": ("Git Repository", "Source code and history exposed"),
            "/.git/config": ("Git Config", "Repository URLs and sensitive data"),
            "/admin": ("Admin Panel", "Unauthorized access possible"),
            "/backup.zip": ("Backup Archive", "May contain database dumps and sensitive files"),
            "/backup.sql": ("SQL Dump", "Database backup exposed"),
            "/config.php": ("Config File", "Database credentials and API keys"),
            "/wp-config.php": ("WordPress Config", "Database and security keys exposed"),
            "/phpinfo.php": ("PHP Info", "Server configuration disclosed"),
            "/.aws/credentials": ("AWS Credentials", "Cloud access keys exposed"),
        }
        
        risk_type, risk_desc = file_risks.get(path, ("Sensitive File", "Critical information exposed"))
        
        message = f"""
🔥🔥🔥 *CRITICAL LEAK* 🔥🔥🔥

━━━━━━━━━━━━━━━━━━━━━━
⚠️ *IMMEDIATE ACTION REQUIRED* ⚠️
━━━━━━━━━━━━━━━━━━━━━━

🌐 *Exposed URL:*
`{url}{path}`

📁 *File Type:*
{risk_type}

🚨 *Status:* ✅ ACCESSIBLE (200 OK)

━━━━━━━━━━━━━━━━━━━━━━
🔓 *SECURITY RISK:*
{risk_desc}

━━━━━━━━━━━━━━━━━━━━━━
⚡ *URGENT ACTIONS:*

1️⃣ Block public access immediately
2️⃣ Move file outside web root
3️⃣ Review server configuration
4️⃣ Check for data exposure
5️⃣ Rotate any exposed credentials

━━━━━━━━━━━━━━━━━━━━━━
🔴 *SEVERITY:* CRITICAL
🕒 *Detected:* Just now
🔍 *Scanner:* EYE v1\\.1

━━━━━━━━━━━━━━━━━━━━━━
⚠️ This vulnerability is actively being scanned by attackers!
"""
        await self.send_telegram_alert(message)
    
    async def send_scan_start(self, domain):
        """
        Send notification when scan starts
        
        Args:
            domain (str): Target domain
        """
        message = f"""
🔍 *SCAN INITIATED* 🔍

━━━━━━━━━━━━━━━━━━━━━━
🎯 *Target Domain*
`{domain}`

━━━━━━━━━━━━━━━━━━━━━━
📋 *SCAN PHASES*

1️⃣ Subdomain Discovery
   └─ Certificate Transparency

2️⃣ Port Scanning
   └─ Common service ports

3️⃣ Sensitive File Detection
   └─ Critical file fuzzing

━━━━━━━━━━━━━━━━━━━━━━
⏳ *Status:* In Progress\\.\\.\\.
🔍 *Tool:* EYE v1\\.1
🤖 *Bot:* @eyescanjohn\\_bot

━━━━━━━━━━━━━━━━━━━━━━
💡 You'll receive real\\-time alerts for:
• Critical port discoveries
• Sensitive file exposures
• Scan completion summary

Stay tuned for results! 🚀
"""
        await self.send_telegram_alert(message)
