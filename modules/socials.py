"""
EYE - Social Media Hunter Module
Extracts social media profile links from web pages
"""

import re
import aiohttp
import asyncio
from typing import List, Dict, Set
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse
from rich.console import Console

console = Console()


class SocialHunter:
    """
    Hunts for social media profile links across web pages
    """
    
    # Target social media platforms
    PLATFORMS = {
        'facebook.com': 'Facebook',
        'fb.com': 'Facebook',
        'twitter.com': 'Twitter',
        'x.com': 'Twitter',
        'instagram.com': 'Instagram',
        'linkedin.com': 'LinkedIn',
        'youtube.com': 'YouTube',
        'youtu.be': 'YouTube',
        'tiktok.com': 'TikTok',
        'discord.com': 'Discord',
        'discord.gg': 'Discord',
        't.me': 'Telegram',
        'github.com': 'GitHub',
        'pinterest.com': 'Pinterest',
        'reddit.com': 'Reddit',
        'medium.com': 'Medium',
        'snapchat.com': 'Snapchat',
        'whatsapp.com': 'WhatsApp'
    }
    
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=10)
    
    def extract_links(self, html_content: str) -> Dict[str, Set[str]]:
        """
        Extract social media links from HTML content
        
        Args:
            html_content: HTML source code as string
            
        Returns:
            Dictionary grouping links by platform
        """
        if not html_content:
            return {}
        
        social_links = {}
        
        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all anchor tags with href
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').lower()
                
                # Skip empty or invalid links
                if not href or href.startswith('#') or href.startswith('javascript:'):
                    continue
                
                # Check if link contains any target platform
                for domain, platform_name in self.PLATFORMS.items():
                    if domain in href:
                        # Clean the URL
                        cleaned_url = self.clean_url(href)
                        
                        if cleaned_url:
                            # Add to the appropriate platform list
                            if platform_name not in social_links:
                                social_links[platform_name] = set()
                            social_links[platform_name].add(cleaned_url)
        
        except Exception:
            pass
        
        return social_links
    
    def clean_url(self, url: str) -> str:
        """
        Clean social media URL by removing query parameters and fragments
        
        Args:
            url: Raw URL string
            
        Returns:
            Cleaned URL string
        """
        try:
            # Handle relative URLs
            if not url.startswith('http'):
                if url.startswith('//'):
                    url = 'https:' + url
                else:
                    return None
            
            # Parse URL
            parsed = urlparse(url)
            
            # Reconstruct without query parameters and fragments
            cleaned = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                '', '', ''
            ))
            
            # Remove trailing slashes
            cleaned = cleaned.rstrip('/')
            
            # Filter out generic/homepage links
            path = parsed.path.rstrip('/')
            if not path or path in ['/', '/home', '/login', '/signin', '/signup']:
                return None
            
            return cleaned
        
        except Exception:
            return None
    
    async def hunt_single(self, url: str) -> Dict[str, Dict[str, Set[str]]]:
        """
        Hunt for social media links on a single URL
        
        Args:
            url: Target URL to scan
            
        Returns:
            Dictionary containing URL and found social links
        """
        result = {
            'url': url,
            'social_links': {}
        }
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, ssl=False, allow_redirects=True) as response:
                    if response.status == 200:
                        html = await response.text()
                        result['social_links'] = self.extract_links(html)
                        
                        if result['social_links']:
                            console.print(f"[+] [cyan]{url}[/cyan]")
                            for platform, links in sorted(result['social_links'].items()):
                                console.print(f"    🔗 {platform}: [green]{len(links)} profile(s)[/green]")
                                for link in sorted(links)[:3]:  # Show first 3
                                    console.print(f"       - {link}")
                                if len(links) > 3:
                                    console.print(f"       ... and {len(links) - 3} more")
        
        except asyncio.TimeoutError:
            pass
        except Exception:
            pass
        
        return result
    
    async def hunt_multiple(self, urls: List[str]) -> Dict[str, Dict[str, Set[str]]]:
        """
        Hunt for social media links across multiple URLs concurrently
        
        Args:
            urls: List of URLs to scan
            
        Returns:
            Dictionary mapping URLs to their social media findings
        """
        console.print(f"[*] Hunting social media profiles on [cyan]{len(urls)}[/cyan] URLs...")
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(50)
        
        async def hunt_with_limit(url):
            async with semaphore:
                return await self.hunt_single(url)
        
        # Execute all hunting tasks concurrently
        tasks = [hunt_with_limit(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Organize results by URL
        hunt_data = {}
        total_profiles = 0
        platforms_found = set()
        
        for result in results:
            if isinstance(result, dict) and not isinstance(result, Exception):
                url = result['url']
                social_links = result['social_links']
                
                if social_links:
                    hunt_data[url] = social_links
                    
                    # Count totals
                    for platform, links in social_links.items():
                        total_profiles += len(links)
                        platforms_found.add(platform)
        
        # Print summary
        if hunt_data:
            platforms_str = ', '.join(sorted(platforms_found))
            console.print(f"[✓] Hunt complete: [green]{total_profiles} profiles[/green] found across [cyan]{len(platforms_found)} platforms[/cyan] ({platforms_str})")
        else:
            console.print(f"[!] No social media profiles found")
        
        return hunt_data
    
    def get_platform_stats(self, hunt_data: Dict[str, Dict[str, Set[str]]]) -> Dict[str, int]:
        """
        Calculate statistics for social media platforms found
        
        Args:
            hunt_data: Dictionary of hunt results
            
        Returns:
            Dictionary with platform counts
        """
        stats = {}
        
        for url_data in hunt_data.values():
            for platform, links in url_data.items():
                if platform not in stats:
                    stats[platform] = 0
                stats[platform] += len(links)
        
        return stats
