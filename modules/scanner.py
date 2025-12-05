"""
EYE - Port Scanner Module
Performs asynchronous port scanning on discovered hosts
"""

import asyncio
from rich.console import Console
from rich.table import Table
from config import PORT_LIST, PORT_TIMEOUT, MAX_CONCURRENT

console = Console()


class PortScanner:
    """
    Asynchronous port scanner using asyncio
    """
    
    def __init__(self, ports=None, timeout=PORT_TIMEOUT):
        """
        Initialize port scanner
        
        Args:
            ports (list): List of ports to scan (default: from config)
            timeout (int): Connection timeout in seconds
        """
        self.ports = ports or PORT_LIST
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        self.results = []
    
    async def scan_port(self, host, port):
        """
        Attempt to connect to a specific port on a host
        
        Args:
            host (str): Target hostname or IP
            port (int): Port number to scan
            
        Returns:
            tuple: (host, port, is_open)
        """
        async with self.semaphore:
            try:
                # Attempt to open a connection
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port),
                    timeout=self.timeout
                )
                writer.close()
                await writer.wait_closed()
                return (host, port, True)
            except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
                return (host, port, False)
            except Exception as e:
                # Catch any other exceptions silently
                return (host, port, False)
    
    async def scan_host(self, host):
        """
        Scan all configured ports on a single host
        
        Args:
            host (str): Target hostname
            
        Returns:
            dict: Scan results for the host
        """
        tasks = [self.scan_port(host, port) for port in self.ports]
        results = await asyncio.gather(*tasks)
        
        # Filter only open ports
        open_ports = [port for (h, port, is_open) in results if is_open]
        
        if open_ports:
            return {
                'host': host,
                'open_ports': open_ports,
                'status': 'active'
            }
        return {
            'host': host,
            'open_ports': [],
            'status': 'inactive'
        }
    
    async def scan_multiple(self, hosts):
        """
        Scan multiple hosts concurrently
        
        Args:
            hosts (set/list): Collection of hostnames to scan
            
        Returns:
            list: Scan results for all hosts
        """
        if not hosts:
            console.print("[!] [yellow]No hosts to scan[/yellow]")
            return []
        
        console.print(f"[*] Starting port scan on [cyan]{len(hosts)}[/cyan] hosts...")
        console.print(f"[*] Scanning ports: [cyan]{', '.join(map(str, self.ports))}[/cyan]")
        
        # Convert set to list if needed
        host_list = list(hosts)
        
        # Scan all hosts
        tasks = [self.scan_host(host) for host in host_list]
        results = await asyncio.gather(*tasks)
        
        self.results = results
        
        # Display results
        self._display_results(results)
        
        return results
    
    def _display_results(self, results):
        """
        Display scan results in a formatted table
        
        Args:
            results (list): Scan results to display
        """
        # Count active hosts
        active_hosts = [r for r in results if r['open_ports']]
        
        console.print(f"\n[+] Port scan complete!")
        console.print(f"[+] Active hosts: [green]{len(active_hosts)}[/green] / [cyan]{len(results)}[/cyan]")
        
        if active_hosts:
            # Create a rich table
            table = Table(title="Open Ports Discovered", show_header=True, header_style="bold magenta")
            table.add_column("Host", style="cyan", no_wrap=True)
            table.add_column("Open Ports", style="green")
            
            for result in active_hosts:
                host = result['host']
                ports = ', '.join(map(str, sorted(result['open_ports'])))
                table.add_row(host, ports)
            
            console.print(table)
        else:
            console.print("[!] [yellow]No open ports found on any host[/yellow]")
