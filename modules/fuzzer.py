"""
EYE - Fuzzer Module
Checks for sensitive files and directories on discovered web services
"""

import aiohttp
import asyncio
from rich.console import Console
from rich.table import Table
from config import SENSITIVE_PATHS, USER_AGENT

console = Console()


class SensitiveFileFuzzer:
    """
    Checks for publicly accessible sensitive files
    """
    
    def __init__(self, timeout=5, max_concurrent=50):
        """
        Initialize fuzzer
        
        Args:
            timeout (int): Request timeout in seconds
            max_concurrent (int): Maximum concurrent requests
        """
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.sensitive_paths = SENSITIVE_PATHS
        self.findings = []
    
    async def check_sensitive_files(self, url):
        """
        Check a single URL for sensitive files
        
        Args:
            url (str): Base URL to check
            
        Returns:
            list: List of found sensitive files
        """
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        # Remove trailing slash
        url = url.rstrip('/')
        
        findings = []
        
        # Check each sensitive path
        tasks = [self._check_path(url, path) for path in self.sensitive_paths]
        results = await asyncio.gather(*tasks)
        
        # Collect findings
        for result in results:
            if result:
                findings.append(result)
        
        return findings
    
    async def _check_path(self, base_url, path):
        """
        Check if a specific path is accessible
        
        Args:
            base_url (str): Base URL
            path (str): Path to check
            
        Returns:
            dict: Finding details if accessible, None otherwise
        """
        async with self.semaphore:
            full_url = f"{base_url}{path}"
            
            try:
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                headers = {'User-Agent': USER_AGENT}
                
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(full_url, headers=headers, allow_redirects=False, ssl=False) as response:
                        # Check if file is accessible (200 OK)
                        if response.status == 200:
                            content_length = response.headers.get('Content-Length', 'Unknown')
                            
                            return {
                                'url': full_url,
                                'path': path,
                                'status': response.status,
                                'size': content_length,
                                'severity': 'CRITICAL'
                            }
                        
                        # Also flag 403 Forbidden (file exists but restricted)
                        elif response.status == 403:
                            return {
                                'url': full_url,
                                'path': path,
                                'status': response.status,
                                'size': 'N/A',
                                'severity': 'MEDIUM'
                            }
                        
            except asyncio.TimeoutError:
                pass
            except aiohttp.ClientError:
                pass
            except Exception:
                pass
            
            return None
    
    async def fuzz_multiple(self, urls, notifier=None):
        """
        Check multiple URLs for sensitive files
        
        Args:
            urls (list): List of URLs to check
            notifier: Optional TelegramNotifier instance
            
        Returns:
            list: All findings across all URLs
        """
        if not urls:
            console.print("[!] [yellow]No URLs to fuzz[/yellow]")
            return []
        
        console.print(f"\n[*] Starting sensitive file fuzzing on [cyan]{len(urls)}[/cyan] targets...")
        console.print(f"[*] Checking [cyan]{len(self.sensitive_paths)}[/cyan] sensitive paths per target")
        
        all_findings = []
        
        # Check each URL
        for url in urls:
            findings = await self.check_sensitive_files(url)
            
            if findings:
                all_findings.extend(findings)
                
                # Display findings for this URL
                for finding in findings:
                    severity_color = "red" if finding['severity'] == 'CRITICAL' else "yellow"
                    console.print(
                        f"[{severity_color}]🔥 {finding['severity']}:[/{severity_color}] "
                        f"[cyan]{finding['url']}[/cyan] "
                        f"(Status: {finding['status']}, Size: {finding['size']})"
                    )
                    
                    # Send Telegram alert for critical findings
                    if notifier and finding['severity'] == 'CRITICAL':
                        await notifier.send_sensitive_file_alert(url, finding['path'])
        
        self.findings = all_findings
        
        # Display summary
        console.print(f"\n[+] Fuzzing complete!")
        if all_findings:
            console.print(f"[+] Found [red]{len(all_findings)}[/red] sensitive files!")
            self._display_findings(all_findings)
        else:
            console.print("[+] No sensitive files found")
        
        return all_findings
    
    def _display_findings(self, findings):
        """
        Display findings in a formatted table
        
        Args:
            findings (list): List of findings
        """
        if not findings:
            return
        
        # Create a rich table
        table = Table(title="🔥 Sensitive Files Discovered", show_header=True, header_style="bold red")
        table.add_column("URL", style="cyan", no_wrap=False)
        table.add_column("Path", style="yellow")
        table.add_column("Status", style="white")
        table.add_column("Severity", style="red")
        
        for finding in findings:
            severity_style = "bold red" if finding['severity'] == 'CRITICAL' else "yellow"
            table.add_row(
                finding['url'],
                finding['path'],
                str(finding['status']),
                f"[{severity_style}]{finding['severity']}[/{severity_style}]"
            )
        
        console.print(table)
