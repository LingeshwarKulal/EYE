"""
EYE - CORS Scanner Module
Detects CORS (Cross-Origin Resource Sharing) misconfigurations
"""

import aiohttp
import asyncio
from rich.console import Console
from rich.table import Table

console = Console()


class CORSScanner:
    """
    Scans for CORS misconfigurations that could lead to security issues
    """
    
    def __init__(self, timeout=10):
        """
        Initialize CORS scanner
        
        Args:
            timeout (int): Request timeout in seconds
        """
        self.timeout = timeout
        self.vulnerable_hosts = []
    
    async def check_cors(self, url):
        """
        Check if a URL has CORS misconfiguration
        
        Args:
            url (str): Target URL to check
            
        Returns:
            dict: CORS check results or None
        """
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            timeout_obj = aiohttp.ClientTimeout(total=self.timeout)
            headers = {
                'Origin': 'http://evil.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession(timeout=timeout_obj) as session:
                async with session.get(url, headers=headers, ssl=False) as response:
                    # Check Access-Control-Allow-Origin header
                    allow_origin = response.headers.get('Access-Control-Allow-Origin', '')
                    allow_credentials = response.headers.get('Access-Control-Allow-Credentials', '')
                    
                    # Check for vulnerabilities
                    is_vulnerable = False
                    vulnerability_type = None
                    
                    if allow_origin == '*':
                        is_vulnerable = True
                        vulnerability_type = "WILDCARD (*)"
                    elif allow_origin == 'http://evil.com':
                        is_vulnerable = True
                        vulnerability_type = "REFLECTED ORIGIN"
                    elif allow_origin and allow_credentials.lower() == 'true':
                        is_vulnerable = True
                        vulnerability_type = "CREDENTIALS + ORIGIN"
                    
                    if is_vulnerable:
                        result = {
                            'url': url,
                            'vulnerable': True,
                            'type': vulnerability_type,
                            'allow_origin': allow_origin,
                            'allow_credentials': allow_credentials
                        }
                        self.vulnerable_hosts.append(result)
                        return result
                    else:
                        return {
                            'url': url,
                            'vulnerable': False,
                            'allow_origin': allow_origin
                        }
                    
        except Exception as e:
            return None
    
    async def scan_multiple(self, urls):
        """
        Scan multiple URLs for CORS misconfigurations
        
        Args:
            urls (list): List of URLs to scan
            
        Returns:
            list: List of vulnerable hosts
        """
        if not urls:
            console.print("[!] [yellow]No URLs to scan for CORS[/yellow]")
            return []
        
        console.print(f"\n[*] Starting CORS misconfiguration scan on [cyan]{len(urls)}[/cyan] targets...")
        
        # Scan all URLs
        tasks = [self.check_cors(url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        # Filter out None results
        results = [r for r in results if r]
        
        # Count vulnerabilities
        vulnerable_count = len(self.vulnerable_hosts)
        
        # Display results
        console.print(f"[+] CORS scan complete!")
        
        if vulnerable_count > 0:
            console.print(f"[!] Found [red]{vulnerable_count}[/red] CORS vulnerabilities!")
            self._display_vulnerabilities()
        else:
            console.print(f"[+] No CORS misconfigurations detected")
        
        return self.vulnerable_hosts
    
    def _display_vulnerabilities(self):
        """
        Display CORS vulnerabilities in a formatted table
        """
        if not self.vulnerable_hosts:
            return
        
        # Create a rich table
        table = Table(title="⚠️ CORS Vulnerabilities Detected", show_header=True, header_style="bold red")
        table.add_column("URL", style="cyan", no_wrap=False)
        table.add_column("Vulnerability Type", style="yellow")
        table.add_column("Allow-Origin", style="red")
        table.add_column("Credentials", style="white")
        
        for vuln in self.vulnerable_hosts:
            table.add_row(
                vuln['url'],
                vuln['type'],
                vuln['allow_origin'],
                vuln.get('allow_credentials', 'N/A')
            )
        
        console.print(table)
        
        # Print recommendations
        console.print("\n[bold red]⚠️ SECURITY RISK:[/bold red]")
        console.print("CORS misconfigurations can allow malicious websites to:")
        console.print("  • Read sensitive data from your application")
        console.print("  • Make authenticated requests on behalf of users")
        console.print("  • Bypass same-origin policy protections")
        console.print("\n[bold yellow]📋 Recommendations:[/bold yellow]")
        console.print("  1. Specify exact allowed origins instead of '*'")
        console.print("  2. Avoid reflecting the Origin header without validation")
        console.print("  3. Don't combine credentials with wildcard origins")
