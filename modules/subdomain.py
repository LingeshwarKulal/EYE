"""
EYE - Subdomain Discovery Module
Enumerates subdomains using Certificate Transparency logs
"""

import aiohttp
import asyncio
from rich.console import Console
from config import CRT_SH_URL, REQUEST_TIMEOUT

console = Console()


class SubdomainHunter:
    """
    Discovers subdomains for a given domain using crt.sh API
    """
    
    def __init__(self):
        self.subdomains = set()
    
    async def find_subdomains(self, domain):
        """
        Query crt.sh for subdomains via Certificate Transparency logs
        
        Args:
            domain (str): Target domain to enumerate
            
        Returns:
            set: Unique set of discovered subdomains
        """
        self.domain = domain  # Store domain for fallback
        url = CRT_SH_URL.format(domain=domain)
        console.print(f"[*] Querying Certificate Transparency logs for [cyan]{domain}[/cyan]...")
        
        try:
            timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            
                            # Extract subdomains from the response
                            for entry in data:
                                name_value = entry.get('name_value', '')
                                
                                # Handle multi-line entries (certificate can have multiple names)
                                names = name_value.split('\n')
                                for name in names:
                                    name = name.strip()
                                    
                                    # Skip wildcards and empty entries
                                    if name and not name.startswith('*'):
                                        self.subdomains.add(name.lower())
                            
                            console.print(f"[+] Found [green]{len(self.subdomains)}[/green] unique subdomains")
                            return self.subdomains
                            
                        except aiohttp.ContentTypeError:
                            console.print("[!] [yellow]No valid JSON response from crt.sh[/yellow]")
                            return set()
                    else:
                        console.print(f"[!] [yellow]crt.sh returned status code: {response.status}[/yellow]")
                        console.print(f"[*] [cyan]Service may be temporarily unavailable. Continuing with main domain...[/cyan]")
                        # Return at least the main domain to continue scanning
                        return {self.domain}
                        
        except asyncio.TimeoutError:
            console.print(f"[!] [red]Request to crt.sh timed out after {REQUEST_TIMEOUT} seconds[/red]")
            console.print(f"[*] [cyan]Continuing with main domain only...[/cyan]")
            return {self.domain}
        except aiohttp.ClientError as e:
            console.print(f"[!] [red]Connection error: {str(e)}[/red]")
            console.print(f"[*] [cyan]Continuing with main domain only...[/cyan]")
            return {self.domain}
        except Exception as e:
            console.print(f"[!] [red]Unexpected error during subdomain discovery: {str(e)}[/red]")
            console.print(f"[*] [cyan]Continuing with main domain only...[/cyan]")
            return {self.domain}
