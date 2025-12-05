"""
EYE - Technology Stack Detection Module
CMS, Framework, and Server fingerprinting
"""

import re
import asyncio
import aiohttp
from rich.console import Console

console = Console()


async def identify_tech(url: str) -> dict:
    """
    Identify technology stack for a given URL
    
    Args:
        url: Target URL (with protocol)
        
    Returns:
        Dictionary with technology detection results
    """
    result = {
        'url': url,
        'server': None,
        'powered_by': None,
        'cms': [],
        'frameworks': [],
        'languages': [],
        'cdn': None,
        'waf': None,
        'headers': {}
    }
    
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, ssl=False, allow_redirects=True) as response:
                # Get headers
                headers = response.headers
                body = await response.text()
                
                # Server detection
                if 'Server' in headers:
                    server = headers['Server']
                    result['server'] = server
                    result['headers']['Server'] = server
                    
                    # Detect WAF from server header
                    if any(waf in server.lower() for waf in ['cloudflare', 'akamai', 'incapsula', 'sucuri']):
                        result['waf'] = server
                
                # Powered-By detection
                if 'X-Powered-By' in headers:
                    powered_by = headers['X-Powered-By']
                    result['powered_by'] = powered_by
                    result['headers']['X-Powered-By'] = powered_by
                    
                    # Language detection from X-Powered-By
                    if 'PHP' in powered_by:
                        result['languages'].append(f"PHP {re.search(r'PHP/([0-9.]+)', powered_by).group(1) if re.search(r'PHP/([0-9.]+)', powered_by) else ''}")
                    elif 'ASP.NET' in powered_by:
                        result['languages'].append('ASP.NET')
                
                # CDN detection
                if 'CF-RAY' in headers or 'cf-cache-status' in headers:
                    result['cdn'] = 'Cloudflare'
                elif 'X-Amz-Cf-Id' in headers:
                    result['cdn'] = 'AWS CloudFront'
                elif 'X-Cache' in headers and 'akamai' in headers['X-Cache'].lower():
                    result['cdn'] = 'Akamai'
                
                # Additional security headers
                security_headers = ['X-Frame-Options', 'X-Content-Type-Options', 'Content-Security-Policy', 
                                   'Strict-Transport-Security', 'X-XSS-Protection']
                for header in security_headers:
                    if header in headers:
                        result['headers'][header] = headers[header]
                
                # Body-based detection
                body_lower = body.lower()
                
                # CMS Detection
                if 'wp-content' in body_lower or 'wp-includes' in body_lower:
                    result['cms'].append('WordPress')
                    # Try to get WordPress version
                    wp_version = re.search(r'wordpress["\s]+([0-9.]+)', body_lower)
                    if wp_version:
                        result['cms'][-1] = f"WordPress {wp_version.group(1)}"
                
                if 'joomla' in body_lower:
                    result['cms'].append('Joomla')
                
                if 'drupal' in body_lower or '/sites/default/' in body_lower:
                    result['cms'].append('Drupal')
                
                if 'magento' in body_lower or 'mage/cookies' in body_lower:
                    result['cms'].append('Magento')
                
                if 'shopify' in body_lower or 'cdn.shopify.com' in body_lower:
                    result['cms'].append('Shopify')
                
                if 'wix.com' in body_lower or 'wixstatic.com' in body_lower:
                    result['cms'].append('Wix')
                
                # Framework Detection
                if 'laravel_session' in body_lower or 'laravel' in body_lower:
                    result['frameworks'].append('Laravel')
                
                if 'django' in body_lower or 'csrfmiddlewaretoken' in body_lower:
                    result['frameworks'].append('Django')
                
                if 'react' in body_lower or 'react-root' in body_lower or '__react' in body_lower:
                    result['frameworks'].append('React')
                
                if 'vue' in body_lower or 'vue.js' in body_lower or '__vue' in body_lower:
                    result['frameworks'].append('Vue.js')
                
                if 'angular' in body_lower or 'ng-version' in body_lower:
                    result['frameworks'].append('Angular')
                
                if 'next.js' in body_lower or '_next/' in body_lower:
                    result['frameworks'].append('Next.js')
                
                if 'nuxt' in body_lower or '__nuxt' in body_lower:
                    result['frameworks'].append('Nuxt.js')
                
                if 'express' in body_lower or 'x-powered-by: express' in body_lower:
                    result['frameworks'].append('Express.js')
                
                if 'strapi' in body_lower:
                    result['frameworks'].append('Strapi')
                
                # Additional language detection from body
                if '<jsp:' in body or '<%@' in body:
                    result['languages'].append('JSP/Java')
                
                if '<?php' in body or '<?=' in body:
                    if not any('PHP' in lang for lang in result['languages']):
                        result['languages'].append('PHP')
                
                # JavaScript libraries
                js_libs = []
                if 'jquery' in body_lower:
                    jquery_version = re.search(r'jquery[/-]([0-9.]+)', body_lower)
                    js_libs.append(f"jQuery {jquery_version.group(1) if jquery_version else ''}")
                
                if 'bootstrap' in body_lower:
                    js_libs.append('Bootstrap')
                
                if 'tailwind' in body_lower:
                    js_libs.append('Tailwind CSS')
                
                if js_libs:
                    result['js_libraries'] = js_libs
                
                # Check for common meta tags
                generator = re.search(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)', body, re.IGNORECASE)
                if generator:
                    result['generator'] = generator.group(1)
                    
                    # Parse generator for CMS/Framework info
                    gen_lower = generator.group(1).lower()
                    if 'wordpress' in gen_lower and 'WordPress' not in ' '.join(result['cms']):
                        result['cms'].append(f"WordPress {re.search(r'([0-9.]+)', generator.group(1)).group(1) if re.search(r'([0-9.]+)', generator.group(1)) else ''}")
                
                return result
                
    except asyncio.TimeoutError:
        result['error'] = 'Timeout'
        return result
    except Exception as e:
        result['error'] = str(e)
        return result


async def identify_tech_multiple(urls: list) -> dict:
    """
    Identify technology stack for multiple URLs
    
    Args:
        urls: List of URLs
        
    Returns:
        Dictionary mapping URL -> tech results
    """
    if not urls:
        return {}
    
    console.print(f"[*] Running technology fingerprinting on [cyan]{len(urls)}[/cyan] services...")
    
    tasks = [identify_tech(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    tech_map = {}
    for url, result in zip(urls, results):
        if isinstance(result, Exception):
            console.print(f"  [{url}] [red]Error: {str(result)}[/red]")
            tech_map[url] = {'error': str(result)}
        else:
            tech_map[url] = result
            
            # Display results
            tech_parts = []
            if result.get('server'):
                tech_parts.append(f"Server: [cyan]{result['server']}[/cyan]")
            if result.get('cms'):
                tech_parts.append(f"CMS: [yellow]{', '.join(result['cms'])}[/yellow]")
            if result.get('frameworks'):
                tech_parts.append(f"Framework: [magenta]{', '.join(result['frameworks'])}[/magenta]")
            if result.get('languages'):
                tech_parts.append(f"Language: [green]{', '.join(result['languages'])}[/green]")
            if result.get('cdn'):
                tech_parts.append(f"CDN: [blue]{result['cdn']}[/blue]")
            if result.get('waf'):
                tech_parts.append(f"WAF: [red]{result['waf']}[/red]")
            
            if tech_parts:
                console.print(f"  [{url}]")
                for part in tech_parts:
                    console.print(f"    {part}")
            else:
                console.print(f"  [{url}] [dim]No specific fingerprints detected[/dim]")
    
    return tech_map


def get_tech_summary(tech_data: dict) -> str:
    """
    Get a concise summary of detected technologies
    
    Args:
        tech_data: Technology detection result
        
    Returns:
        Summary string
    """
    parts = []
    
    if tech_data.get('cms'):
        parts.append(', '.join(tech_data['cms']))
    
    if tech_data.get('frameworks'):
        parts.append(', '.join(tech_data['frameworks']))
    
    if tech_data.get('server') and not tech_data.get('cms') and not tech_data.get('frameworks'):
        parts.append(tech_data['server'])
    
    if tech_data.get('languages') and not parts:
        parts.append(', '.join(tech_data['languages']))
    
    return ' | '.join(parts) if parts else 'Unknown'


def get_tech_icon(tech_data: dict) -> str:
    """
    Get emoji icon for technology
    
    Args:
        tech_data: Technology detection result
        
    Returns:
        Emoji icon
    """
    # Check CMS first
    if tech_data.get('cms'):
        cms_lower = ' '.join(tech_data['cms']).lower()
        if 'wordpress' in cms_lower:
            return '📝'
        elif 'shopify' in cms_lower:
            return '🛒'
        elif 'magento' in cms_lower:
            return '🛍️'
    
    # Check frameworks
    if tech_data.get('frameworks'):
        fw_lower = ' '.join(tech_data['frameworks']).lower()
        if 'react' in fw_lower or 'vue' in fw_lower or 'angular' in fw_lower:
            return '⚛️'
        elif 'django' in fw_lower:
            return '🐍'
        elif 'laravel' in fw_lower:
            return '🎨'
    
    # Check server
    if tech_data.get('server'):
        server_lower = tech_data['server'].lower()
        if 'nginx' in server_lower:
            return '🟢'
        elif 'apache' in server_lower:
            return '🪶'
        elif 'iis' in server_lower or 'microsoft' in server_lower:
            return '🪟'
    
    return '🔧'
