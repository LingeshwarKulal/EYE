"""
EYE - Data Harvester Module
Extracts emails and phone numbers from web pages
"""

import re
import aiohttp
import asyncio
from typing import List, Dict, Set
from rich.console import Console

console = Console()


class DataHarvester:
    """
    Harvests sensitive data like emails and phone numbers from web pages
    """
    
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=10)
        self.email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        self.phone_pattern = re.compile(r"(\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9})")
    
    def extract_emails(self, html_content: str) -> Set[str]:
        """
        Extract email addresses from HTML content using regex
        
        Args:
            html_content: HTML source code as string
            
        Returns:
            Set of unique email addresses found
        """
        if not html_content:
            return set()
        
        emails = set(self.email_pattern.findall(html_content))
        return emails
    
    def extract_phones(self, html_content: str) -> Set[str]:
        """
        Extract phone numbers from HTML content using regex
        Filters out false positives like dates/timestamps/port numbers
        
        Args:
            html_content: HTML source code as string
            
        Returns:
            Set of unique phone numbers found
        """
        if not html_content:
            return set()
        
        # Find all potential phone matches
        matches = self.phone_pattern.findall(html_content)
        
        # Filter out false positives
        valid_phones = set()
        for match in matches:
            # Remove all non-digit characters to count digits
            digits_only = re.sub(r'\D', '', match)
            
            # Phone numbers should be 7-15 digits
            if len(digits_only) < 7 or len(digits_only) > 15:
                continue
            
            # Skip if it looks like a port number or range (e.g., +8080-8081, +2000-206)
            # Pattern: +DIGITS-DIGITS where both parts are short (< 5 digits each)
            if re.match(r'^\+?\d{1,5}-\d{1,5}$', match.strip()):
                continue
            
            # Skip patterns that look like: +12345-123 (likely port/range)
            if re.match(r'^\+?\d{4,6}-\d{1,4}$', match.strip()):
                continue
            
            # Skip if it looks like a date (YYYY-MM-DD or DD-MM-YYYY or similar)
            if re.match(r'^\d{4}[-./]\d{1,2}[-./]\d{1,2}$', match.strip()):
                continue
            if re.match(r'^\d{1,2}[-./]\d{1,2}[-./]\d{2,4}$', match.strip()):
                continue
            
            # Skip if it looks like a time (HH:MM:SS or HH:MM)
            if re.match(r'^\d{1,2}:\d{2}(:\d{2})?$', match.strip()):
                continue
            
            # Skip version numbers (1.0.0, 2.3.4, etc.)
            if re.match(r'^\d+\.\d+\.\d+', match.strip()):
                continue
            
            # Skip decimal numbers (123.456, 1.234, etc.)
            if re.match(r'^\d+\.\d+$', match.strip()) and '.' in match:
                continue
            
            # Skip IP addresses or similar patterns
            if re.match(r'^\d+\.\d+\.\d+\.\d+', match.strip()):
                continue
            
            # Skip if it's all the same digit repeated (000-000-0000)
            if len(set(digits_only)) == 1:
                continue
            
            # Skip numbers with too few digit groups for a phone (e.g., just two groups)
            # Valid phone: (123) 456-7890, +1-234-567-8900
            # Invalid: +1234-567 (only 2 groups)
            groups = re.findall(r'\d+', match)
            if len(groups) < 2:
                continue
            
            # If it starts with +, ensure the country code looks reasonable (1-3 digits)
            if match.strip().startswith('+'):
                country_code_match = re.match(r'^\+(\d+)', match.strip())
                if country_code_match:
                    country_code = country_code_match.group(1)
                    # Country codes are typically 1-3 digits
                    # But the total should still form a valid phone structure
                    if len(country_code) > 3:
                        # If "country code" is > 3 digits, it's suspicious
                        # Check if remaining part makes sense
                        remaining = match.strip()[len(country_code)+1:]
                        if not remaining or len(re.sub(r'\D', '', remaining)) < 6:
                            continue
            
            # Additional check: if the number has only 2 parts separated by dash
            # and both parts are short, skip it (likely not a phone)
            parts = match.strip().replace('+', '').split('-')
            if len(parts) == 2:
                part1_digits = re.sub(r'\D', '', parts[0])
                part2_digits = re.sub(r'\D', '', parts[1])
                # Both parts very short = suspicious (e.g., 2000-206)
                if len(part1_digits) <= 4 and len(part2_digits) <= 4:
                    continue
            
            # Clean up the phone number (remove extra spaces)
            cleaned = re.sub(r'\s+', ' ', match.strip())
            valid_phones.add(cleaned)
        
        return valid_phones
    
    async def harvest_single(self, url: str) -> Dict[str, Set[str]]:
        """
        Harvest emails and phone numbers from a single URL
        
        Args:
            url: Target URL to harvest data from
            
        Returns:
            Dictionary containing emails and phones found
        """
        result = {
            'url': url,
            'emails': set(),
            'phones': set()
        }
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, ssl=False, allow_redirects=True) as response:
                    if response.status == 200:
                        html = await response.text()
                        result['emails'] = self.extract_emails(html)
                        result['phones'] = self.extract_phones(html)
                        
                        if result['emails'] or result['phones']:
                            console.print(f"[+] [cyan]{url}[/cyan]")
                            if result['emails']:
                                console.print(f"    📧 Emails: {len(result['emails'])} found")
                            if result['phones']:
                                console.print(f"    📞 Phones: {len(result['phones'])} found")
        
        except asyncio.TimeoutError:
            pass
        except Exception:
            pass
        
        return result
    
    async def harvest_multiple(self, urls: List[str]) -> Dict[str, Dict[str, Set[str]]]:
        """
        Harvest data from multiple URLs concurrently
        
        Args:
            urls: List of URLs to harvest from
            
        Returns:
            Dictionary mapping URLs to their harvested data
        """
        console.print(f"[*] Harvesting emails and phone numbers from [cyan]{len(urls)}[/cyan] URLs...")
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(50)
        
        async def harvest_with_limit(url):
            async with semaphore:
                return await self.harvest_single(url)
        
        # Execute all harvesting tasks concurrently
        tasks = [harvest_with_limit(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Organize results by URL
        harvest_data = {}
        for result in results:
            if isinstance(result, dict) and not isinstance(result, Exception):
                url = result['url']
                harvest_data[url] = {
                    'emails': result['emails'],
                    'phones': result['phones']
                }
        
        # Print summary
        total_emails = sum(len(data['emails']) for data in harvest_data.values())
        total_phones = sum(len(data['phones']) for data in harvest_data.values())
        
        if total_emails or total_phones:
            console.print(f"[✓] Harvesting complete: [green]{total_emails} emails, {total_phones} phones[/green]")
        else:
            console.print(f"[!] No emails or phones found")
        
        return harvest_data
