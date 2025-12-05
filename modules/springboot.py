"""
EYE - Spring Boot Actuator Hunter Module
Discovers exposed Spring Boot actuator endpoints
"""

import aiohttp
import asyncio
from typing import List, Dict, Set
from rich.console import Console

console = Console()


# Critical Spring Boot actuator endpoints
ACTUATOR_ENDPOINTS = [
    '/actuator',
    '/actuator/env',
    '/actuator/health',
    '/actuator/info',
    '/actuator/metrics',
    '/actuator/heapdump',
    '/actuator/threaddump',
    '/actuator/mappings',
    '/actuator/configprops',
    '/actuator/beans',
    '/actuator/trace',
    '/actuator/httptrace',
    '/actuator/dump',
    '/actuator/sessions',
    '/actuator/shutdown',
    '/actuator/loggers',
    '/actuator/auditevents',
    '/actuator/scheduledtasks',
    '/actuator/conditions',
    '/actuator/caches',
    # Legacy Spring Boot 1.x endpoints
    '/env',
    '/health',
    '/info',
    '/metrics',
    '/heapdump',
    '/threaddump',
    '/mappings',
    '/configprops',
    '/beans',
    '/trace',
    '/dump'
]


async def check_actuator(url: str) -> Dict:
    """
    Check for exposed Spring Boot actuator endpoints
    
    Args:
        url: Base URL to check (e.g., https://example.com)
        
    Returns:
        Dictionary with actuator findings
    """
    result = {
        'url': url,
        'actuators_found': [],
        'critical_count': 0,
        'info_count': 0
    }
    
    timeout = aiohttp.ClientTimeout(total=10)
    
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Create tasks for all endpoints
            tasks = []
            for endpoint in ACTUATOR_ENDPOINTS:
                test_url = url.rstrip('/') + endpoint
                tasks.append(check_single_endpoint(session, test_url, endpoint))
            
            # Execute all checks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for endpoint_result in results:
                if isinstance(endpoint_result, dict) and endpoint_result.get('exposed'):
                    result['actuators_found'].append(endpoint_result)
                    
                    if endpoint_result['severity'] == 'CRITICAL':
                        result['critical_count'] += 1
                    else:
                        result['info_count'] += 1
    
    except Exception:
        pass
    
    return result


async def check_single_endpoint(session: aiohttp.ClientSession, test_url: str, endpoint: str) -> Dict:
    """
    Check a single actuator endpoint
    
    Args:
        session: aiohttp session
        test_url: Full URL to test
        endpoint: Endpoint path
        
    Returns:
        Dictionary with endpoint result
    """
    result = {
        'endpoint': endpoint,
        'url': test_url,
        'exposed': False,
        'status': None,
        'content_type': None,
        'severity': 'INFO',
        'size': 0
    }
    
    try:
        async with session.get(test_url, ssl=False, allow_redirects=False) as response:
            result['status'] = response.status
            result['content_type'] = response.headers.get('Content-Type', '').lower()
            
            # Check if endpoint is exposed
            if response.status == 200:
                content = await response.text()
                result['size'] = len(content)
                
                # Verify it's actually an actuator endpoint
                is_json = 'application/json' in result['content_type']
                is_octet = 'application/octet-stream' in result['content_type']
                has_actuator_data = any(keyword in content.lower() for keyword in ['actuator', 'spring', 'boot'])
                
                if is_json or is_octet or has_actuator_data:
                    result['exposed'] = True
                    
                    # Determine severity
                    critical_endpoints = [
                        'heapdump', 'threaddump', 'env', 'configprops', 
                        'beans', 'shutdown', 'trace', 'httptrace', 'dump'
                    ]
                    
                    if any(critical in endpoint for critical in critical_endpoints):
                        result['severity'] = 'CRITICAL'
    
    except Exception:
        pass
    
    return result


async def hunt_actuators_multiple(urls: List[str]) -> Dict[str, Dict]:
    """
    Hunt for Spring Boot actuators across multiple URLs
    
    Args:
        urls: List of URLs to check
        
    Returns:
        Dictionary mapping URLs to their actuator findings
    """
    console.print(f"[*] Hunting Spring Boot actuators on [cyan]{len(urls)}[/cyan] URLs...")
    
    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(20)
    
    async def hunt_with_limit(url):
        async with semaphore:
            return await check_actuator(url)
    
    # Execute all hunting tasks concurrently
    tasks = [hunt_with_limit(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Organize results
    actuator_data = {}
    total_critical = 0
    total_info = 0
    affected_hosts = 0
    
    for result in results:
        if isinstance(result, dict) and not isinstance(result, Exception):
            url = result['url']
            
            if result['actuators_found']:
                actuator_data[url] = result
                total_critical += result['critical_count']
                total_info += result['info_count']
                affected_hosts += 1
                
                # Print findings
                console.print(f"\n[bold red]⚠️  ACTUATORS FOUND![/bold red] [cyan]{url}[/cyan]")
                
                for actuator in result['actuators_found']:
                    severity_color = 'red' if actuator['severity'] == 'CRITICAL' else 'yellow'
                    console.print(
                        f"    [{severity_color}]{actuator['severity']}[/{severity_color}]: "
                        f"{actuator['endpoint']} (Status: {actuator['status']}, Size: {actuator['size']} bytes)"
                    )
    
    # Print summary
    if actuator_data:
        console.print(
            f"\n[✓] Actuator hunt complete: "
            f"[red]{total_critical} critical[/red], "
            f"[yellow]{total_info} info[/yellow] "
            f"endpoints on [cyan]{affected_hosts} host(s)[/cyan]"
        )
    else:
        console.print(f"[!] No Spring Boot actuators found")
    
    return actuator_data
