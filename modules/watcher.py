"""
EYE - Asset Watcher Module
Continuous monitoring for infrastructure changes
"""

import json
import os
import asyncio
from datetime import datetime
from typing import Dict, Any, Callable
from rich.console import Console

console = Console()


class AssetWatcher:
    """
    Monitors infrastructure for changes over time
    """
    
    def __init__(self, domain: str, interval: int = 21600):
        """
        Initialize the asset watcher
        
        Args:
            domain: Target domain to monitor
            interval: Time in seconds between scans (default: 6 hours)
        """
        self.domain = domain
        self.interval = interval
        self.state_file = f"state_{domain.replace('/', '_').replace(':', '_')}.json"
        self.scan_count = 0
        
    def save_state(self, scan_data: Dict[str, Any]):
        """
        Save current scan state to JSON file
        
        Args:
            scan_data: Current scan results containing subdomains and ports
        """
        try:
            state = {
                'timestamp': datetime.now().isoformat(),
                'domain': self.domain,
                'subdomains': scan_data.get('subdomains', []),
                'scan_results': scan_data.get('scan_results', []),
                'statistics': scan_data.get('statistics', {}),
                'scan_count': self.scan_count
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            console.print(f"[*] State saved to [cyan]{self.state_file}[/cyan]")
            
        except Exception as e:
            console.print(f"[!] [red]Failed to save state: {str(e)}[/red]")
    
    def load_previous_state(self) -> Dict[str, Any]:
        """
        Load previous scan state from JSON file
        
        Returns:
            Previous state dictionary or empty dict if not found
        """
        if not os.path.exists(self.state_file):
            console.print(f"[*] No previous state found. This is the first scan.")
            return {}
        
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            
            console.print(f"[*] Loaded previous state from [cyan]{self.state_file}[/cyan]")
            console.print(f"[*] Last scan: [yellow]{state.get('timestamp', 'Unknown')}[/yellow]")
            return state
            
        except Exception as e:
            console.print(f"[!] [red]Failed to load previous state: {str(e)}[/red]")
            return {}
    
    def detect_changes(self, current_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect changes between current and previous scan
        
        Args:
            current_data: Current scan results
            
        Returns:
            Dictionary containing detected changes
        """
        previous_state = self.load_previous_state()
        
        if not previous_state:
            console.print("[*] [yellow]First scan - no changes to detect[/yellow]")
            return {
                'new_subdomains': [],
                'new_ports': [],
                'removed_subdomains': [],
                'removed_ports': [],
                'is_first_scan': True
            }
        
        # Get previous data
        prev_subdomains = set(previous_state.get('subdomains', []))
        prev_scan_results = previous_state.get('scan_results', [])
        
        # Get current data
        curr_subdomains = set(current_data.get('subdomains', []))
        curr_scan_results = current_data.get('scan_results', [])
        
        # Detect new and removed subdomains
        new_subdomains = list(curr_subdomains - prev_subdomains)
        removed_subdomains = list(prev_subdomains - curr_subdomains)
        
        # Detect new ports
        prev_ports = {}
        for result in prev_scan_results:
            host = result.get('host')
            ports = result.get('open_ports', [])
            if host and ports:
                prev_ports[host] = set(ports)
        
        curr_ports = {}
        for result in curr_scan_results:
            host = result.get('host')
            ports = result.get('open_ports', [])
            if host and ports:
                curr_ports[host] = set(ports)
        
        new_ports = []
        removed_ports = []
        
        # Check for new ports on existing hosts
        for host, ports in curr_ports.items():
            if host in prev_ports:
                new = ports - prev_ports[host]
                if new:
                    new_ports.append({'host': host, 'ports': list(new)})
            else:
                # New host entirely
                if ports:
                    new_ports.append({'host': host, 'ports': list(ports)})
        
        # Check for removed ports
        for host, ports in prev_ports.items():
            if host in curr_ports:
                removed = ports - curr_ports[host]
                if removed:
                    removed_ports.append({'host': host, 'ports': list(removed)})
            else:
                # Host is gone
                if ports:
                    removed_ports.append({'host': host, 'ports': list(ports)})
        
        changes = {
            'new_subdomains': new_subdomains,
            'new_ports': new_ports,
            'removed_subdomains': removed_subdomains,
            'removed_ports': removed_ports,
            'is_first_scan': False
        }
        
        # Display changes
        if new_subdomains:
            console.print(f"\n[bold green]🆕 NEW SUBDOMAINS DETECTED:[/bold green]")
            for subdomain in new_subdomains:
                console.print(f"  + {subdomain}")
        
        if new_ports:
            console.print(f"\n[bold green]🔓 NEW OPEN PORTS DETECTED:[/bold green]")
            for item in new_ports:
                console.print(f"  + {item['host']}: {', '.join(map(str, item['ports']))}")
        
        if removed_subdomains:
            console.print(f"\n[bold yellow]📉 REMOVED SUBDOMAINS:[/bold yellow]")
            for subdomain in removed_subdomains:
                console.print(f"  - {subdomain}")
        
        if removed_ports:
            console.print(f"\n[bold yellow]🔒 CLOSED PORTS:[/bold yellow]")
            for item in removed_ports:
                console.print(f"  - {item['host']}: {', '.join(map(str, item['ports']))}")
        
        if not any([new_subdomains, new_ports, removed_subdomains, removed_ports]):
            console.print(f"\n[*] [green]No infrastructure changes detected[/green]")
        
        return changes
    
    async def send_change_alert(self, changes: Dict[str, Any], notifier):
        """
        Send alert about detected changes
        
        Args:
            changes: Dictionary of detected changes
            notifier: TelegramNotifier instance
        """
        if not notifier or not notifier.enabled:
            return
        
        if changes.get('is_first_scan'):
            return
        
        new_subdomains = changes.get('new_subdomains', [])
        new_ports = changes.get('new_ports', [])
        removed_subdomains = changes.get('removed_subdomains', [])
        removed_ports = changes.get('removed_ports', [])
        
        if not any([new_subdomains, new_ports, removed_subdomains, removed_ports]):
            return
        
        # Build alert message
        message = f"🚨 *Infrastructure Changes Detected*\n"
        message += f"📍 Target: `{self.domain}`\n"
        message += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if new_subdomains:
            message += f"🆕 *New Subdomains ({len(new_subdomains)}):*\n"
            for subdomain in new_subdomains[:10]:  # Limit to 10
                message += f"  • `{subdomain}`\n"
            if len(new_subdomains) > 10:
                message += f"  ... and {len(new_subdomains) - 10} more\n"
            message += "\n"
        
        if new_ports:
            message += f"🔓 *New Open Ports ({len(new_ports)}):*\n"
            for item in new_ports[:10]:  # Limit to 10
                message += f"  • `{item['host']}`: {', '.join(map(str, item['ports']))}\n"
            if len(new_ports) > 10:
                message += f"  ... and {len(new_ports) - 10} more\n"
            message += "\n"
        
        if removed_subdomains:
            message += f"📉 *Removed Subdomains ({len(removed_subdomains)}):*\n"
            for subdomain in removed_subdomains[:5]:
                message += f"  • `{subdomain}`\n"
            if len(removed_subdomains) > 5:
                message += f"  ... and {len(removed_subdomains) - 5} more\n"
            message += "\n"
        
        if removed_ports:
            message += f"🔒 *Closed Ports ({len(removed_ports)}):*\n"
            for item in removed_ports[:5]:
                message += f"  • `{item['host']}`: {', '.join(map(str, item['ports']))}\n"
            if len(removed_ports) > 5:
                message += f"  ... and {len(removed_ports) - 5} more\n"
        
        # Send alert
        await notifier.send_message(message)
        console.print("[+] [green]Change alert sent via Telegram[/green]")
    
    async def monitor_loop(self, scan_func: Callable, domain: str, enable_alerts: bool = False, skip_fuzz: bool = False):
        """
        Run continuous monitoring loop
        
        Args:
            scan_func: Async function to execute for scanning
            domain: Target domain
            enable_alerts: Enable Telegram notifications
            skip_fuzz: Skip sensitive file fuzzing
        """
        console.print("\n" + "="*60)
        console.print("[bold cyan]🔍 WATCHER MODE ACTIVATED[/bold cyan]")
        console.print("="*60)
        console.print(f"[*] Target: [cyan]{domain}[/cyan]")
        console.print(f"[*] Interval: [yellow]{self.interval}[/yellow] seconds ([yellow]{self.interval/3600:.1f}[/yellow] hours)")
        console.print(f"[*] State file: [cyan]{self.state_file}[/cyan]")
        console.print("[*] Press [red]Ctrl+C[/red] to stop monitoring")
        console.print("="*60 + "\n")
        
        from modules.notifier import TelegramNotifier
        notifier = None
        if enable_alerts:
            notifier = TelegramNotifier()
            if notifier.enabled:
                console.print("[+] [green]Telegram alerts enabled for change detection[/green]\n")
        
        while True:
            try:
                self.scan_count += 1
                console.print(f"\n[bold yellow]{'='*60}[/bold yellow]")
                console.print(f"[bold yellow]🔄 SCAN #{self.scan_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/bold yellow]")
                console.print(f"[bold yellow]{'='*60}[/bold yellow]\n")
                
                # Run the scan
                scan_data = await scan_func(domain, enable_alerts, skip_fuzz)
                
                # Detect changes
                console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
                console.print("[bold cyan]🔍 CHANGE DETECTION[/bold cyan]")
                console.print(f"[bold cyan]{'='*60}[/bold cyan]")
                
                changes = self.detect_changes(scan_data)
                
                # Send alert if changes detected
                if not changes.get('is_first_scan'):
                    await self.send_change_alert(changes, notifier)
                
                # Save current state
                self.save_state(scan_data)
                
                # Sleep until next scan
                console.print(f"\n[bold green]{'='*60}[/bold green]")
                console.print(f"[bold green]✓ Scan #{self.scan_count} Complete[/bold green]")
                console.print(f"[bold green]{'='*60}[/bold green]")
                console.print(f"[*] [yellow]Next scan in {self.interval} seconds ({self.interval/3600:.1f} hours)[/yellow]")
                console.print(f"[*] [dim]Sleeping until {datetime.fromtimestamp(datetime.now().timestamp() + self.interval).strftime('%Y-%m-%d %H:%M:%S')}[/dim]\n")
                
                await asyncio.sleep(self.interval)
                
            except KeyboardInterrupt:
                console.print("\n\n[bold red]{'='*60}[/bold red]")
                console.print("[bold red]⚠️  WATCHER MODE STOPPED[/bold red]")
                console.print("[bold red]{'='*60}[/bold red]")
                console.print(f"[*] Total scans completed: [cyan]{self.scan_count}[/cyan]")
                console.print(f"[*] State saved to: [cyan]{self.state_file}[/cyan]")
                console.print("[+] Thank you for using EYE Watcher! 🔍\n")
                break
            except Exception as e:
                console.print(f"\n[!] [red]Error in monitoring loop: {str(e)}[/red]")
                console.print(f"[*] Retrying in 60 seconds...\n")
                await asyncio.sleep(60)
