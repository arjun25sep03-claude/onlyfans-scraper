import requests
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OnlyFansScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # Platform URLs to check for username existence
        self.platforms = {
            'instagram': 'https://www.instagram.com/{username}/',
            'twitter': 'https://twitter.com/{username}',
            'tiktok': 'https://www.tiktok.com/@{username}',
            'youtube': 'https://www.youtube.com/@{username}',
            'snapchat': 'https://www.snapchat.com/add/{username}',
            'telegram': 'https://t.me/{username}',
            'twitch': 'https://www.twitch.tv/{username}',
            'reddit': 'https://www.reddit.com/u/{username}',
            'github': 'https://github.com/{username}',
            'linkedin': 'https://www.linkedin.com/in/{username}/'
        }

    def scrape_profile(self, username: str) -> Optional[Dict]:
        """Search for username across social media platforms"""
        try:
            logger.info(f"Searching for username: {username}")

            links = {}

            # Check each platform for username existence
            for platform, url_template in self.platforms.items():
                url = url_template.format(username=username)
                try:
                    response = requests.head(url, headers=self.headers, timeout=5, allow_redirects=True)
                    # 2xx status means profile found
                    if 200 <= response.status_code < 300:
                        links[platform] = url
                        logger.info(f"Found {platform}: {url}")
                except requests.exceptions.RequestException as e:
                    logger.debug(f"Error checking {platform}: {str(e)}")

            return {
                'username': username,
                'bio': f'Found on {len(links)} platform(s)',
                'links': links
            }

        except Exception as e:
            logger.error(f"Error processing {username}: {str(e)}")
            return None
