"""
EYE - OS Detection Module
TTL-based operating system fingerprinting
"""

import asyncio
import subprocess
import re
import platform
from rich.console import Console

console = Console()


async def detect_os(ip_address: str) -> dict:
    """
    Detect operating system using TTL fingerprinting
    
    Args:
        ip_address: Target IP address
        
    Returns:
        Dictionary with OS detection results
    """
    try:
        # Determine ping command based on host OS
        system = platform.system().lower()
        
        if system == "windows":
            # Windows: ping -n 1 -w 1000 IP
            cmd = ["ping", "-n", "1", "-w", "1000", ip_address]
        else:
            # Linux/Mac: ping -c 1 -W 1 IP
            cmd = ["ping", "-c", "1", "-W", "1", ip_address]
        
        # Execute ping command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        output = stdout.decode('utf-8', errors='ignore')
        
        # Extract TTL value from output
        ttl_match = re.search(r'(?:ttl|TTL)=(\d+)', output, re.IGNORECASE)
        
        if not ttl_match:
            return {
                'os_guess': 'Unknown (No response)',
                'ttl': None,
                'confidence': 'Low',
                'raw_output': output[:200]
            }
        
        ttl = int(ttl_match.group(1))
        
        # OS Detection based on TTL
        if ttl <= 64:
            os_guess = "Linux/Unix"
            confidence = "High" if ttl in [64, 63, 62] else "Medium"
        elif ttl <= 128:
            os_guess = "Windows"
            confidence = "High" if ttl in [128, 127, 126] else "Medium"
        elif ttl <= 255:
            os_guess = "Cisco/Solaris/Network Device"
            confidence = "High" if ttl in [255, 254, 253] else "Medium"
        else:
            os_guess = "Unknown"
            confidence = "Low"
        
        # Additional heuristics
        if ttl == 64:
            os_guess = "Linux/Unix/macOS"
        elif ttl == 128:
            os_guess = "Windows"
        elif ttl == 255:
            os_guess = "Cisco IOS/Solaris"
        
        return {
            'os_guess': os_guess,
            'ttl': ttl,
            'confidence': confidence,
            'method': 'TTL Fingerprinting',
            'raw_output': output[:200]
        }
        
    except asyncio.TimeoutError:
        return {
            'os_guess': 'Unknown (Timeout)',
            'ttl': None,
            'confidence': 'Low',
            'method': 'TTL Fingerprinting'
        }
    except Exception as e:
        console.print(f"[!] [red]OS detection error for {ip_address}: {str(e)}[/red]")
        return {
            'os_guess': 'Unknown (Error)',
            'ttl': None,
            'confidence': 'Low',
            'error': str(e)
        }


async def detect_os_multiple(ip_addresses: list) -> dict:
    """
    Detect OS for multiple IP addresses
    
    Args:
        ip_addresses: List of IP addresses
        
    Returns:
        Dictionary mapping IP -> OS detection results
    """
    console.print(f"[*] Running OS detection on [cyan]{len(ip_addresses)}[/cyan] hosts...")
    
    tasks = [detect_os(ip) for ip in ip_addresses]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    os_map = {}
    for ip, result in zip(ip_addresses, results):
        if isinstance(result, Exception):
            os_map[ip] = {
                'os_guess': 'Unknown (Error)',
                'ttl': None,
                'confidence': 'Low'
            }
        else:
            os_map[ip] = result
            
            # Display result
            if result.get('ttl'):
                console.print(f"  [{ip}] TTL={result['ttl']} → [cyan]{result['os_guess']}[/cyan] ({result['confidence']} confidence)")
            else:
                console.print(f"  [{ip}] [dim]{result['os_guess']}[/dim]")
    
    return os_map


def get_os_icon(os_guess: str) -> str:
    """
    Get emoji icon for OS type
    
    Args:
        os_guess: OS guess string
        
    Returns:
        Emoji icon
    """
    os_lower = os_guess.lower()
    
    if 'windows' in os_lower:
        return '🪟'
    elif 'linux' in os_lower or 'unix' in os_lower:
        return '🐧'
    elif 'mac' in os_lower or 'darwin' in os_lower:
        return '🍎'
    elif 'cisco' in os_lower or 'network' in os_lower:
        return '🌐'
    elif 'solaris' in os_lower:
        return '☀️'
    else:
        return '❓'
