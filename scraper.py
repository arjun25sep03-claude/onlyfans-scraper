import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OnlyFansScraper:
    def __init__(self):
        self.base_url = "https://onlyfans.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # Regex patterns for social media
        self.patterns = {
            'instagram': r'(?:instagram\.com|ig\.me)/(\w+)',
            'twitter': r'(?:twitter\.com|x\.com)/(\w+)',
            'tiktok': r'(?:tiktok\.com|vm\.tiktok\.com)/?(@?\w+)',
            'telegram': r'(?:t\.me|telegram\.me)/(\w+)',
            'youtube': r'(?:youtube\.com|youtu\.be)/(?:@|channel/|c/)?(\w+)',
            'snapchat': r'snapchat\.com/add/(\w+)',
            'website': r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})'
        }

    def scrape_profile(self, username: str) -> Optional[Dict]:
        """Scrape OnlyFans profile and extract social media links"""
        try:
            url = f"{self.base_url}/{username}"
            logger.info(f"Scraping {url}")

            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract bio/about section
            bio_text = self._extract_bio(soup)

            if not bio_text:
                logger.warning(f"No bio found for {username}")
                return {'username': username, 'bio': '', 'links': {}}

            # Extract all links
            links = self._extract_links(bio_text)

            return {
                'username': username,
                'bio': bio_text[:500],  # Store first 500 chars
                'links': links
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Error scraping {username}: {str(e)}")
            return None

    def _extract_bio(self, soup: BeautifulSoup) -> str:
        """Extract bio text from page"""
        # Try multiple selectors for bio section
        selectors = [
            'p[class*="about"]',
            'div[class*="bio"]',
            'div[class*="description"]',
            '[data-testid="profile-bio"]'
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)

        # Fallback: get all text and search for social patterns
        text = soup.get_text()
        return text

    def _extract_links(self, text: str) -> Dict[str, str]:
        """Extract social media links using regex patterns"""
        links = {}

        for platform, pattern in self.patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Take first match, clean up
                match = matches[0]
                if isinstance(match, tuple):
                    match = next((m for m in match if m), '')
                links[platform] = match.lstrip('@')

        return links
