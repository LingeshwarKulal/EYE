"""
EYE - Data Exporter Module
Exports scan results to JSON and CSV formats
"""

import json
import csv
import os
from datetime import datetime
from rich.console import Console

console = Console()


class DataExporter:
    """
    Exports reconnaissance data to various formats
    """
    
    def __init__(self, output_dir="output"):
        """
        Initialize data exporter
        
        Args:
            output_dir (str): Directory to save export files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def save_json(self, data, filename="scan_results.json"):
        """
        Save scan data to JSON file
        
        Args:
            data (dict): Scan data dictionary
            filename (str): Output filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            filepath = os.path.join(self.output_dir, filename)
            
            # Add metadata
            export_data = {
                'scan_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'tool': 'EYE v1.1',
                    'target': data.get('target_domain', 'N/A')
                },
                'results': data
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            console.print(f"[+] JSON saved: [cyan]{filepath}[/cyan]")
            return True
            
        except Exception as e:
            console.print(f"[!] [red]Failed to save JSON: {str(e)}[/red]")
            return False
    
    def save_csv(self, data, filename="scan_results.csv"):
        """
        Save scan data to CSV file
        
        Args:
            data (dict): Scan data dictionary
            filename (str): Output filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            filepath = os.path.join(self.output_dir, filename)
            
            # Prepare CSV rows
            rows = []
            
            # Extract data from results
            scan_results = data.get('scan_results', [])
            email_data = data.get('emails', {})
            cors_data = data.get('cors_vulnerabilities', [])
            sensitive_files = data.get('sensitive_files', [])
            
            # Create a mapping for quick lookups
            cors_map = {item['url']: item for item in cors_data}
            sensitive_map = {}
            for sf in sensitive_files:
                url = sf.get('url', '').split('/')[0:3]
                base = '/'.join(url) if len(url) >= 3 else sf.get('url', '')
                if base not in sensitive_map:
                    sensitive_map[base] = []
                sensitive_map[base].append(sf.get('path', ''))
            
            # Build rows from scan results
            for result in scan_results:
                host = result.get('host', 'N/A')
                open_ports = result.get('open_ports', [])
                ports_str = ','.join(map(str, open_ports)) if open_ports else 'None'
                
                # Check for emails
                emails_found = []
                for url, emails in email_data.items():
                    if host in url:
                        emails_found.extend(emails)
                emails_str = ','.join(set(emails_found)) if emails_found else 'None'
                
                # Check CORS status
                cors_status = 'SAFE'
                for url_pattern in [f"https://{host}", f"http://{host}"]:
                    if url_pattern in cors_map:
                        cors_status = f"VULNERABLE ({cors_map[url_pattern]['type']})"
                        break
                
                # Check sensitive files
                sensitive_count = 0
                for url_pattern in [f"https://{host}", f"http://{host}"]:
                    if url_pattern in sensitive_map:
                        sensitive_count = len(sensitive_map[url_pattern])
                        break
                
                row = {
                    'Subdomain': host,
                    'Status': result.get('status', 'unknown'),
                    'Open_Ports': ports_str,
                    'Emails_Found': emails_str,
                    'CORS_Status': cors_status,
                    'Sensitive_Files': sensitive_count
                }
                rows.append(row)
            
            # Write CSV
            if rows:
                fieldnames = ['Subdomain', 'Status', 'Open_Ports', 'Emails_Found', 'CORS_Status', 'Sensitive_Files']
                
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
                
                console.print(f"[+] CSV saved: [cyan]{filepath}[/cyan]")
                console.print(f"[+] Total records: [green]{len(rows)}[/green]")
                return True
            else:
                console.print("[!] [yellow]No data to export to CSV[/yellow]")
                return False
                
        except Exception as e:
            console.print(f"[!] [red]Failed to save CSV: {str(e)}[/red]")
            return False
    
    def export_all(self, data):
        """
        Export data to both JSON and CSV formats
        
        Args:
            data (dict): Scan data dictionary
            
        Returns:
            tuple: (json_success, csv_success)
        """
        console.print("\n[bold yellow]═══ Exporting Scan Results ═══[/bold yellow]")
        
        json_success = self.save_json(data)
        csv_success = self.save_csv(data)
        
        if json_success and csv_success:
            console.print("\n[+] [green]Data saved to JSON & CSV format for analysis.[/green]")
        elif json_success or csv_success:
            console.print("\n[+] [yellow]Data partially exported.[/yellow]")
        else:
            console.print("\n[!] [red]Failed to export data.[/red]")
        
        return (json_success, csv_success)
