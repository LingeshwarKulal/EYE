"""
EYE - Security Audit Module
Checks SSL certificate expiration and security headers
"""

import ssl
import socket
import aiohttp
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from rich.console import Console
from urllib.parse import urlparse

console = Console()


async def check_security(url: str) -> Dict:
    """
    Performs comprehensive security audit on a URL
    Checks SSL certificate expiration and security headers
    
    Args:
        url: Target URL to audit
        
    Returns:
        Dictionary containing SSL days remaining and missing security headers
    """
    result = {
        'url': url,
        'ssl_days': None,
        'ssl_status': 'N/A',
        'missing_headers': [],
        'security_score': 0
    }
    
    # Parse URL to get hostname
    parsed = urlparse(url)
    hostname = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    
    # Only check SSL for HTTPS URLs
    if parsed.scheme == 'https':
        result['ssl_days'], result['ssl_status'] = await check_ssl_expiration(hostname, port)
    
    # Check security headers
    result['missing_headers'] = await check_security_headers(url)
    
    # Calculate security score (100 = perfect)
    score = 100
    if result['ssl_days'] is not None:
        if result['ssl_days'] < 0:
            score -= 30  # Expired certificate
        elif result['ssl_days'] < 30:
            score -= 15  # Expiring soon
    
    # Deduct points for missing headers
    score -= len(result['missing_headers']) * 10
    result['security_score'] = max(0, score)
    
    return result


async def check_ssl_expiration(hostname: str, port: int = 443) -> tuple[Optional[int], str]:
    """
    Check SSL certificate expiration date
    
    Args:
        hostname: Domain name to check
        port: SSL port (default 443)
        
    Returns:
        Tuple of (days_remaining, status_message)
    """
    try:
        # Create SSL context
        context = ssl.create_default_context()
        
        # Run socket operation in executor to avoid blocking
        loop = asyncio.get_event_loop()
        
        def get_cert():
            with socket.create_connection((hostname, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    return ssock.getpeercert()
        
        cert = await loop.run_in_executor(None, get_cert)
        
        # Parse expiration date
        expiry_date_str = cert['notAfter']
        expiry_date = datetime.strptime(expiry_date_str, '%b %d %H:%M:%S %Y %Z')
        
        # Calculate days remaining
        days_remaining = (expiry_date - datetime.now()).days
        
        # Determine status
        if days_remaining < 0:
            status = "EXPIRED"
        elif days_remaining < 30:
            status = "WARNING"
        else:
            status = "VALID"
        
        return days_remaining, status
    
    except socket.timeout:
        return None, "TIMEOUT"
    except ssl.SSLError:
        return None, "SSL_ERROR"
    except Exception:
        return None, "ERROR"


async def check_security_headers(url: str) -> List[str]:
    """
    Check for missing security headers in HTTP response
    
    Args:
        url: Target URL to check headers
        
    Returns:
        List of missing security header names
    """
    # Important security headers to check
    security_headers = {
        'X-Frame-Options': 'X-Frame-Options',
        'Content-Security-Policy': 'CSP',
        'Strict-Transport-Security': 'HSTS',
        'X-Content-Type-Options': 'X-Content-Type-Options',
        'X-XSS-Protection': 'X-XSS-Protection',
        'Referrer-Policy': 'Referrer-Policy'
    }
    
    missing_headers = []
    
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, ssl=False, allow_redirects=True) as response:
                # Check which headers are missing
                for header, short_name in security_headers.items():
                    if header not in response.headers:
                        missing_headers.append(short_name)
    
    except asyncio.TimeoutError:
        missing_headers = ["TIMEOUT"]
    except Exception:
        missing_headers = ["ERROR"]
    
    return missing_headers


async def audit_multiple(urls: List[str]) -> Dict[str, Dict]:
    """
    Audit security for multiple URLs concurrently
    
    Args:
        urls: List of URLs to audit
        
    Returns:
        Dictionary mapping URLs to their audit results
    """
    console.print(f"[*] Auditing SSL and security headers for [cyan]{len(urls)}[/cyan] URLs...")
    
    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(30)
    
    async def audit_with_limit(url):
        async with semaphore:
            return await check_security(url)
    
    # Execute all audit tasks concurrently
    tasks = [audit_with_limit(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Organize results
    audit_data = {}
    ssl_warnings = 0
    header_issues = 0
    
    for result in results:
        if isinstance(result, dict) and not isinstance(result, Exception):
            url = result['url']
            audit_data[url] = result
            
            # Print individual results
            parsed = urlparse(url)
            if parsed.scheme == 'https' and result['ssl_days'] is not None:
                if result['ssl_status'] == 'WARNING':
                    console.print(f"[!] [yellow]{url}[/yellow]")
                    console.print(f"    ⚠️  SSL Expires in: [yellow]{result['ssl_days']} days[/yellow]")
                    ssl_warnings += 1
                elif result['ssl_status'] == 'EXPIRED':
                    console.print(f"[!] [red]{url}[/red]")
                    console.print(f"    ❌ SSL Certificate: [red]EXPIRED[/red]")
                    ssl_warnings += 1
            
            if result['missing_headers'] and 'ERROR' not in result['missing_headers']:
                if result['ssl_status'] not in ['WARNING', 'EXPIRED']:
                    console.print(f"[!] [cyan]{url}[/cyan]")
                headers_str = ', '.join(result['missing_headers'])
                console.print(f"    🔒 Missing Headers: [yellow]{headers_str}[/yellow]")
                console.print(f"    📊 Security Score: [{'green' if result['security_score'] >= 70 else 'yellow' if result['security_score'] >= 50 else 'red'}]{result['security_score']}/100[/{'green' if result['security_score'] >= 70 else 'yellow' if result['security_score'] >= 50 else 'red'}]")
                header_issues += 1
    
    # Print summary
    if ssl_warnings or header_issues:
        console.print(f"[✓] Audit complete: [yellow]{ssl_warnings} SSL warnings, {header_issues} header issues[/yellow]")
    else:
        console.print(f"[✓] Audit complete: [green]All checks passed[/green]")
    
    return audit_data
