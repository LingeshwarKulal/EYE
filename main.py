"""
EYE - Automated Attack Surface Manager
Main entry point for the reconnaissance framework

Usage:
    python main.py -d example.com
"""

import argparse
import asyncio
import sys
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from modules.banner import show_logo
from modules.subdomain import SubdomainHunter
from modules.scanner import PortScanner
from modules.fuzzer import SensitiveFileFuzzer
from modules.harvester import DataHarvester
from modules.cors import CORSScanner
from modules.exporter import DataExporter
from modules.socials import SocialHunter
from modules.springboot import hunt_actuators_multiple
from modules.bypass_403 import attempt_bypass_multiple
from modules.reporter import HTMLReporter
from modules.watcher import AssetWatcher
from modules.os_detect import detect_os_multiple, get_os_icon
from modules.tech_stack import identify_tech_multiple, get_tech_summary, get_tech_icon
from modules import audit
from config import CRITICAL_PORTS

# Load environment variables from .env file
load_dotenv()

console = Console()


def display_detailed_results(export_data):
    """
    Display detailed scan results on screen
    """
    console.print("\n[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]                    DETAILED SCAN RESULTS                      [/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]\n")
    
    # Display Subdomains
    console.print("[bold yellow]📍 DISCOVERED SUBDOMAINS:[/bold yellow]")
    if export_data['subdomains']:
        for subdomain in sorted(export_data['subdomains']):
            console.print(f"  • {subdomain}")
    else:
        console.print("  [dim]No subdomains found[/dim]")
    console.print()
    
    # Display Open Ports with OS and Tech Info
    console.print("[bold yellow]🔌 PORT SCAN RESULTS:[/bold yellow]")
    for result in export_data['scan_results']:
        if result.get('open_ports'):
            host_display = f"  [cyan]{result['host']}[/cyan]"
            
            # Add OS info if available
            os_data = export_data.get('os_detection', {}).get(result['host'])
            if os_data and os_data.get('os_guess'):
                os_icon = get_os_icon(os_data['os_guess'])
                host_display += f" {os_icon} [dim]{os_data['os_guess']}[/dim]"
            
            console.print(host_display)
            
            for port in sorted(result['open_ports']):
                service = result.get('services', {}).get(port, 'unknown')
                console.print(f"    → Port [green]{port}[/green] ({service})")
    console.print()
    
    # Display Sensitive Files
    if export_data['sensitive_files']:
        console.print("[bold red]🚨 SENSITIVE FILES FOUND:[/bold red]")
        for finding in export_data['sensitive_files']:
            status_color = "green" if finding['status'] == 200 else "yellow"
            console.print(f"  [{status_color}][{finding['status']}][/{status_color}] {finding['url']}")
            console.print(f"      Size: {finding.get('size', 'unknown')}")
        console.print()
    
    # Display Harvested Data
    total_emails = sum(len(data.get('emails', [])) for data in export_data['harvest_data'].values())
    total_phones = sum(len(data.get('phones', [])) for data in export_data['harvest_data'].values())
    
    if total_emails > 0 or total_phones > 0:
        console.print("[bold green]📧 HARVESTED DATA:[/bold green]")
        for url, data in export_data['harvest_data'].items():
            if data.get('emails') or data.get('phones'):
                console.print(f"  [cyan]{url}[/cyan]")
                if data.get('emails'):
                    console.print(f"    Emails: {', '.join(data['emails'])}")
                if data.get('phones'):
                    console.print(f"    Phones: {', '.join(data['phones'])}")
        console.print()
    
    # Display Social Profiles
    if export_data['social_profiles']:
        console.print("[bold magenta]👥 SOCIAL MEDIA PROFILES:[/bold magenta]")
        for url, profiles in export_data['social_profiles'].items():
            if any(profiles.values()):
                console.print(f"  [cyan]{url}[/cyan]")
                for platform, links in profiles.items():
                    if links:
                        console.print(f"    {platform}: {', '.join(links)}")
        console.print()
    
    # Display CORS Vulnerabilities
    if export_data['cors_vulnerabilities']:
        console.print("[bold red]⚠️  CORS VULNERABILITIES:[/bold red]")
        for vuln in export_data['cors_vulnerabilities']:
            console.print(f"  [red]{vuln['url']}[/red]")
            console.print(f"    Issue: {vuln.get('issue', 'Misconfiguration detected')}")
        console.print()
    
    # Display Spring Boot Actuators
    if export_data['redteam_actuators']:
        console.print("[bold red]🔴 SPRING BOOT ACTUATORS:[/bold red]")
        for url, data in export_data['redteam_actuators'].items():
            if data.get('actuators_found'):
                console.print(f"  [red]{url}[/red]")
                for actuator in data['actuators_found']:
                    console.print(f"    → {actuator}")
        console.print()
    
    # Display Access Control Bypasses
    if export_data['redteam_bypasses']:
        console.print("[bold red]🔓 ACCESS CONTROL BYPASSES:[/bold red]")
        bypass_count = 0
        for url, data in export_data['redteam_bypasses'].items():
            if data.get('bypassed'):
                bypass_count += 1
                console.print(f"\n  [red]{url}[/red]")
                console.print(f"    Original Status: [yellow]{data.get('original_status')}[/yellow]")
                console.print(f"    ✓ Bypassed with: [green]{data.get('technique')}[/green]")
                console.print(f"    New Status: [green]{data.get('final_status')}[/green]")
                if data.get('bypass_url') and data.get('bypass_url') != url:
                    console.print(f"    Bypass URL: {data.get('bypass_url')}")
                
                # Display page information if available
                page_info = data.get('page_info')
                if page_info and not page_info.get('error'):
                    console.print(f"\n    [bold cyan]📄 Bypassed Page Content Analysis:[/bold cyan]")
                    
                    # Check for false positive
                    if page_info.get('is_likely_false_positive'):
                        console.print(f"      [bold red]⚠️  WARNING: Possible False Positive![/bold red]")
                        console.print(f"      [yellow]{page_info.get('false_positive_reason')}[/yellow]")
                        console.print()
                    
                    # Show file-specific analysis for non-HTML files
                    if page_info.get('file_type_analysis'):
                        file_analysis = page_info['file_type_analysis']
                        console.print(f"      [bold green]📄 File Type Analysis:[/bold green]")
                        console.print(f"        File Type: .{file_analysis.get('file_type', 'unknown')}")
                        console.print(f"        Lines: {file_analysis.get('line_count', 0)}")
                        
                        if file_analysis.get('directives'):
                            console.print(f"        [bold yellow]Apache Directives Found:[/bold yellow]")
                            for directive in file_analysis['directives'][:10]:
                                console.print(f"          • {directive}")
                        
                        if file_analysis.get('configurations'):
                            console.print(f"        [bold cyan]Configuration Entries:[/bold cyan]")
                            for config in file_analysis['configurations'][:10]:
                                console.print(f"          • {config}")
                        
                        if file_analysis.get('comments'):
                            console.print(f"        [bold dim]Comments:[/bold dim]")
                            for comment in file_analysis['comments'][:5]:
                                console.print(f"          {comment}")
                        
                        if file_analysis.get('preview_lines'):
                            console.print(f"        [bold cyan]File Content Preview:[/bold cyan]")
                            for line in file_analysis['preview_lines'][:15]:
                                console.print(f"          {line}")
                        console.print()
                    
                    if page_info.get('title'):
                        console.print(f"      Title: [white]{page_info['title']}[/white]")
                    
                    console.print(f"      Content Length: {page_info.get('content_length', 0)} bytes")
                    console.print(f"      Content Type: {page_info.get('content_type', 'unknown')}")
                    
                    if page_info.get('server') and page_info.get('server') != 'unknown':
                        console.print(f"      Server: {page_info.get('server')}")
                    
                    if page_info.get('sensitive_keywords'):
                        console.print(f"      [bold red]⚠️  Sensitive Keywords:[/bold red] {', '.join(page_info['sensitive_keywords'][:10])}")
                    
                    if page_info.get('emails'):
                        console.print(f"      [bold yellow]📧 Emails Found:[/bold yellow] {', '.join(page_info['emails'])}")
                    
                    if page_info.get('interesting_patterns'):
                        console.print(f"      [bold red]🔑 Security Findings:[/bold red] {', '.join(page_info['interesting_patterns'])}")
                    
                    if page_info.get('config_vars'):
                        console.print(f"      [bold magenta]⚙️  Configuration Variables:[/bold magenta]")
                        for var in page_info['config_vars'][:5]:
                            console.print(f"        • {var}")
                    
                    if page_info.get('database_info'):
                        console.print(f"      [bold red]🗄️  Database Information:[/bold red]")
                        for db in page_info['database_info'][:3]:
                            console.print(f"        • {db}")
                    
                    if page_info.get('secrets'):
                        console.print(f"      [bold red]🔐 Secrets/Tokens Found:[/bold red]")
                        for secret in page_info['secrets'][:5]:
                            console.print(f"        • {secret}")
                    
                    if page_info.get('file_paths'):
                        console.print(f"      [bold blue]📁 File Paths Exposed:[/bold blue]")
                        for path in page_info['file_paths'][:5]:
                            console.print(f"        • {path}")
                    
                    if page_info.get('preview'):
                        console.print(f"      [bold cyan]📝 Content Preview:[/bold cyan]")
                        preview_lines = page_info['preview'].split('\n')[:3]
                        for line in preview_lines:
                            if line.strip():
                                console.print(f"        {line.strip()[:100]}")
                
                elif page_info and page_info.get('error'):
                    console.print(f"    [dim]Could not extract page content: {page_info['error']}[/dim]")
        
        if bypass_count == 0:
            console.print("  [dim]No successful bypasses[/dim]")
        console.print()
    
    # Display Technology Stack
    if export_data.get('technology_stack'):
        console.print("[bold cyan]🔧 TECHNOLOGY STACK:[/bold cyan]")
        has_tech = False
        for url, tech_data in export_data['technology_stack'].items():
            if not tech_data.get('error'):
                # Check if there's any actual tech detected
                has_any_tech = any([
                    tech_data.get('server'),
                    tech_data.get('cms'),
                    tech_data.get('frameworks'),
                    tech_data.get('languages'),
                    tech_data.get('cdn'),
                    tech_data.get('waf')
                ])
                
                if has_any_tech:
                    has_tech = True
                    tech_icon = get_tech_icon(tech_data)
                    console.print(f"  {tech_icon} [cyan]{url}[/cyan]")
                    
                    if tech_data.get('server'):
                        console.print(f"      Server: [green]{tech_data['server']}[/green]")
                    if tech_data.get('cms'):
                        console.print(f"      CMS: [yellow]{', '.join(tech_data['cms'])}[/yellow]")
                    if tech_data.get('frameworks'):
                        console.print(f"      Frameworks: [magenta]{', '.join(tech_data['frameworks'])}[/magenta]")
                    if tech_data.get('languages'):
                        console.print(f"      Languages: [blue]{', '.join(tech_data['languages'])}[/blue]")
                    if tech_data.get('cdn'):
                        console.print(f"      CDN: [cyan]{tech_data['cdn']}[/cyan]")
                    if tech_data.get('waf'):
                        console.print(f"      WAF: [red]{tech_data['waf']}[/red]")
                else:
                    console.print(f"  [cyan]{url}[/cyan] - [dim]No specific technology fingerprints detected[/dim]")
        
        if not has_tech:
            console.print("  [dim]No technology fingerprints detected[/dim]")
        console.print()
    
    # Display Security Audit Results
    if export_data['security_audit']:
        console.print("[bold yellow]🔒 SECURITY AUDIT:[/bold yellow]")
        for url, audit in export_data['security_audit'].items():
            console.print(f"  [cyan]{url}[/cyan]")
            ssl_status = audit.get('ssl_status', 'Unknown')
            
            # Color code SSL status
            if ssl_status == 'VALID':
                ssl_color = 'green'
            elif ssl_status == 'TIMEOUT':
                ssl_color = 'dim'
            elif ssl_status in ['EXPIRED', 'WARNING']:
                ssl_color = 'red'
            else:
                ssl_color = 'yellow'
            
            console.print(f"    SSL Status: [{ssl_color}]{ssl_status}[/{ssl_color}]")
            
            # Only show missing headers if not timeout
            if ssl_status != 'TIMEOUT' and audit.get('missing_headers'):
                if audit['missing_headers'] != 'TIMEOUT':
                    console.print(f"    Missing Headers: {', '.join(audit['missing_headers'])}")
        console.print()


def ask_save_results():
    """
    Ask user if they want to save results
    """
    console.print("\n[bold yellow]💾 Do you want to save the results?[/bold yellow]")
    console.print("  [1] Yes - Save all results (JSON, CSV, HTML report)")
    console.print("  [2] No - Exit without saving")
    
    while True:
        try:
            choice = input("\nEnter your choice (1 or 2): ").strip()
            if choice == '1':
                return True
            elif choice == '2':
                return False
            else:
                console.print("[red]Invalid choice. Please enter 1 or 2.[/red]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]No input received. Exiting without saving.[/yellow]")
            return False


def parse_arguments():
    """
    Parse command-line arguments
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='EYE - Automated Attack Surface Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py -d example.com
  python main.py --domain target.com
  python main.py -d 192.168.1.1
  python main.py -d example.com --monitor --interval 3600
  python main.py -d target.com --monitor --alert

Note: This tool is for authorized security testing only.
        """
    )
    
    parser.add_argument(
        '-d', '--domain',
        type=str,
        required=True,
        help='Target domain or IP address to scan (e.g., example.com or 192.168.1.1)'
    )
    
    parser.add_argument(
        '--no-fuzz',
        action='store_true',
        help='Skip sensitive file fuzzing'
    )
    
    parser.add_argument(
        '--monitor',
        action='store_true',
        help='Enable continuous monitoring mode (watcher)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=21600,
        help='Monitoring interval in seconds (default: 21600 = 6 hours)'
    )
    
    return parser.parse_args()


async def main(domain, skip_fuzz=False, is_monitoring=False):
    """
    Main reconnaissance workflow
    
    Args:
        domain (str): Target domain to scan
        skip_fuzz (bool): Skip sensitive file fuzzing
        is_monitoring (bool): Whether running in monitoring mode
    """
    # Display banner
    show_logo()
    
    # Display target information
    import socket
    target_display = f"[bold cyan]Target:[/bold cyan] {domain}"
    
    # Try to resolve IP if domain provided
    try:
        # Check if input is already an IP
        socket.inet_aton(domain)
        is_ip = True
        target_display = f"[bold cyan]Target IP:[/bold cyan] {domain}"
    except socket.error:
        # It's a domain, try to resolve IP
        is_ip = False
        try:
            ip_address = socket.gethostbyname(domain)
            target_display = f"[bold cyan]Target:[/bold cyan] {domain}\n[bold yellow]IP Address:[/bold yellow] {ip_address}"
        except:
            target_display = f"[bold cyan]Target:[/bold cyan] {domain}\n[bold yellow]IP Address:[/bold yellow] Unable to resolve"
    
    console.print(Panel.fit(
        target_display,
        border_style="bright_blue"
    ))
    console.print()
    
    # Phase 1: Subdomain Discovery
    console.print("[bold yellow]═══ Phase 1: Subdomain Discovery ═══[/bold yellow]")
    hunter = SubdomainHunter()
    subdomains = await hunter.find_subdomains(domain)
    
    if not subdomains:
        console.print("[!] [yellow]No subdomains discovered via Certificate Transparency[/yellow]")
        console.print(f"[*] [cyan]Continuing scan with main domain: {domain}[/cyan]")
        subdomains = {domain}  # Use main domain as fallback
    
    console.print()
    
    # Phase 2: Port Scanning
    console.print("[bold yellow]═══ Phase 2: Port Scanning ═══[/bold yellow]")
    console.print("[*] Starting port scanning...")
    console.print()
    
    # Initialize scanner
    scanner = PortScanner()
    
    # Run port scanning
    scan_results = await scanner.scan_multiple(subdomains)
    screenshot_count = 0  # Screenshots disabled
    
    # Phase 2.5: OS Detection
    console.print()
    console.print("[bold yellow]═══ Phase 2.5: Operating System Detection ═══[/bold yellow]")
    
    # Extract IP addresses from scan results
    active_ips = []
    for result in scan_results:
        if result.get('open_ports'):
            host = result['host']
            # Try to resolve to IP if it's a domain
            try:
                import socket
                socket.inet_aton(host)
                # Already an IP
                active_ips.append(host)
            except socket.error:
                # It's a domain, resolve it
                try:
                    ip = socket.gethostbyname(host)
                    active_ips.append(ip)
                except:
                    pass
    
    os_detection_results = {}
    if active_ips:
        # Remove duplicates
        active_ips = list(set(active_ips))
        os_detection_results = await detect_os_multiple(active_ips)
        
        # Map back to hostnames
        os_by_host = {}
        for result in scan_results:
            host = result['host']
            try:
                import socket
                socket.inet_aton(host)
                # It's an IP
                if host in os_detection_results:
                    os_by_host[host] = os_detection_results[host]
            except socket.error:
                # It's a domain, get its IP
                try:
                    ip = socket.gethostbyname(host)
                    if ip in os_detection_results:
                        os_by_host[host] = os_detection_results[ip]
                except:
                    pass
        
        os_detection_results = os_by_host
    else:
        console.print("[*] [dim]No active hosts for OS detection[/dim]")
    
    # Get list of active web hosts first
    web_hosts = []
    for result in scan_results:
        if result.get('open_ports'):
            host = result['host']
            open_ports = result['open_ports']
            
            # Add hosts with web ports
            if 443 in open_ports:
                web_hosts.append(f"https://{host}")
            elif 80 in open_ports:
                web_hosts.append(f"http://{host}")
    
    # Phase 3: Advanced Scanning (Parallel execution for speed)
    sensitive_findings = []
    harvest_results = {}
    cors_vulnerabilities = []
    audit_results = {}
    social_profiles = {}
    actuator_findings = {}
    bypass_results = {}
    tech_stack_results = {}
    
    if web_hosts and not skip_fuzz:
        console.print()
        console.print("[bold yellow]═══ Phase 3: Advanced Security Scanning ═══[/bold yellow]")
        console.print(f"[*] Running parallel scans on [cyan]{len(web_hosts)}[/cyan] web services...")
        
        # Initialize all scanners
        fuzzer = SensitiveFileFuzzer()
        harvester = DataHarvester()
        cors_scanner = CORSScanner()
        social_hunter = SocialHunter()
        
        # Run all scans in parallel for better performance
        results = await asyncio.gather(
            fuzzer.fuzz_multiple(web_hosts),
            harvester.harvest_multiple(web_hosts),
            cors_scanner.scan_multiple(web_hosts),
            audit.audit_multiple(web_hosts),
            social_hunter.hunt_multiple(web_hosts),
            identify_tech_multiple(web_hosts),
            return_exceptions=True
        )
        
        # Extract results
        sensitive_findings = results[0] if not isinstance(results[0], Exception) else []
        harvest_results = results[1] if not isinstance(results[1], Exception) else {}
        cors_vulnerabilities = results[2] if not isinstance(results[2], Exception) else []
        audit_results = results[3] if not isinstance(results[3], Exception) else {}
        social_profiles = results[4] if not isinstance(results[4], Exception) else []
        tech_stack_results = results[5] if not isinstance(results[5], Exception) else {}
        
        # Phase 3.5: Red Team - Spring Boot Actuator Hunt
        console.print()
        console.print("[bold red]═══ Phase 3.5: Red Team - Spring Boot Actuator Hunt ═══[/bold red]")
        actuator_findings = await hunt_actuators_multiple(web_hosts)
        
        # Phase 3.6: Red Team - 403/401 Bypass Attempts
        console.print()
        console.print("[bold red]═══ Phase 3.6: Red Team - Access Control Bypass ═══[/bold red]")
        
        # Collect all 403/401 responses from sensitive file fuzzing
        bypass_targets = []
        for finding in sensitive_findings:
            if finding.get('status') in [403, 401]:
                bypass_targets.append({
                    'url': finding['url'],
                    'status': finding['status']
                })
        
        if bypass_targets:
            bypass_results = await attempt_bypass_multiple(bypass_targets)
        else:
            console.print("[*] No 403/401 responses to attempt bypass on")
    
    elif not web_hosts:
        console.print()
        console.print("[!] [yellow]No web services found for advanced scanning[/yellow]")
    
    # Display final summary
    console.print()
    console.print("[bold green]═══ Scan Complete ═══[/bold green]")
    
    active_hosts = len([r for r in scan_results if r.get('open_ports')])
    total_open_ports = sum(len(r.get('open_ports', [])) for r in scan_results)
    total_emails = sum(len(data.get('emails', set())) for data in harvest_results.values())
    total_phones = sum(len(data.get('phones', set())) for data in harvest_results.values())
    ssl_warnings = sum(1 for data in audit_results.values() if data.get('ssl_status') in ['WARNING', 'EXPIRED'])
    total_socials = sum(len(links) for url_data in social_profiles.values() for links in url_data.values())
    total_actuators = sum(len(data.get('actuators_found', [])) for data in actuator_findings.values())
    successful_bypasses = sum(1 for data in bypass_results.values() if data.get('bypassed'))
    
    summary = f"""
[bold cyan]Target Domain:[/bold cyan] {domain}
[bold cyan]Subdomains Discovered:[/bold cyan] {len(subdomains)}
[bold cyan]Active Hosts:[/bold cyan] {active_hosts}
[bold cyan]Total Open Ports:[/bold cyan] {total_open_ports}
[bold cyan]Sensitive Files Found:[/bold cyan] [red]{len(sensitive_findings)}[/red]
[bold cyan]Emails Harvested:[/bold cyan] [green]{total_emails}[/green]
[bold cyan]Phones Harvested:[/bold cyan] [green]{total_phones}[/green]
[bold cyan]Social Profiles Found:[/bold cyan] [magenta]{total_socials}[/magenta]
[bold cyan]CORS Vulnerabilities:[/bold cyan] [red]{len(cors_vulnerabilities)}[/red]
[bold cyan]SSL Warnings:[/bold cyan] [yellow]{ssl_warnings}[/yellow]
[bold red]🔴 Spring Boot Actuators:[/bold red] [bold red]{total_actuators}[/bold red]
[bold red]🔓 Access Control Bypassed:[/bold red] [bold red]{successful_bypasses}[/bold red]
    """
    
    console.print(Panel(summary.strip(), title="[bold]Summary[/bold]", border_style="green"))
    
    # Export data to JSON and CSV (NEW)
    export_data = {
        'target_domain': domain,
        'subdomains': list(subdomains),
        'scan_results': scan_results,
        'os_detection': os_detection_results,
        'technology_stack': tech_stack_results,
        'sensitive_files': sensitive_findings,
        'harvest_data': {url: {'emails': list(data.get('emails', set())), 'phones': list(data.get('phones', set()))} for url, data in harvest_results.items()},
        'social_profiles': {url: {platform: list(links) for platform, links in profiles.items()} for url, profiles in social_profiles.items()},
        'cors_vulnerabilities': cors_vulnerabilities,
        'security_audit': audit_results,
        'redteam_actuators': actuator_findings,
        'redteam_bypasses': bypass_results,
        'statistics': {
            'total_subdomains': len(subdomains),
            'active_hosts': active_hosts,
            'total_open_ports': total_open_ports,
            'sensitive_files': len(sensitive_findings),
            'emails_found': total_emails,
            'phones_found': total_phones,
            'social_profiles_found': total_socials,
            'cors_vulnerabilities': len(cors_vulnerabilities),
            'ssl_warnings': ssl_warnings,
            'actuators_found': total_actuators,
            'successful_bypasses': successful_bypasses
        }
    }
    
    # Display detailed results on screen
    display_detailed_results(export_data)
    
    # If in monitoring mode, return data without asking
    if is_monitoring:
        return export_data
    
    # Ask user if they want to save results
    if ask_save_results():
        console.print("\n[*] Saving results...")
        
        exporter = DataExporter()
        exporter.export_all(export_data)
        
        console.print("[+] Results saved to [cyan]output/[/cyan] directory")
        
        # Generate HTML Report
        console.print("[*] Generating HTML security report...")
        
        html_reporter = HTMLReporter()
        report_path = html_reporter.generate_report(export_data)
        
        console.print(f"[+] [green]HTML Report generated:[/green] [cyan]{report_path}[/cyan]")
        console.print("[*] Open the HTML file in your browser to view the full dashboard")
    else:
        console.print("\n[yellow]Results not saved. Exiting...[/yellow]")
    
    console.print()
    if sensitive_findings:
        console.print("[!] [red]WARNING: Sensitive files were found! Review findings above.[/red]")
    
    if cors_vulnerabilities:
        console.print("[!] [red]WARNING: CORS misconfigurations detected! Review findings above.[/red]")
    
    console.print("[+] Thank you for using EYE! Stay ethical. 🔍")


def run():
    """
    Entry point for the application
    """
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Validate domain
        domain = args.domain.strip().lower()
        if not domain:
            console.print("[!] [red]Invalid domain provided[/red]")
            sys.exit(1)
        
        # Remove protocol if provided
        domain = domain.replace('http://', '').replace('https://', '')
        domain = domain.rstrip('/')
        
        # Check if monitoring mode is enabled
        if args.monitor:
            # Create a wrapper function for the watcher
            async def scan_wrapper(target, skip_f):
                return await main(target, skip_f, is_monitoring=True)
            
            # Initialize and run watcher
            async def run_watcher():
                watcher = AssetWatcher(domain, args.interval)
                await watcher.monitor_loop(scan_wrapper, domain, args.no_fuzz)
            
            asyncio.run(run_watcher())
        else:
            # Run normal single scan
            asyncio.run(main(domain, args.no_fuzz))
        
    except KeyboardInterrupt:
        console.print("\n[!] [yellow]Scan interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[!] [red]Fatal error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    run()
