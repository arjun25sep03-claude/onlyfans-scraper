import os
import time
import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from scraper import OnlyFansScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SupabaseWorker:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL', '').strip()
        self.supabase_key = os.getenv('SUPABASE_KEY', '').strip()

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        logger.info(f"Connecting to Supabase: {self.supabase_url}")
        self.headers = {
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json'
        }
        self.scraper = OnlyFansScraper()
        self.max_workers = int(os.getenv('MAX_WORKERS', 10))
        self.batch_size = int(os.getenv('BATCH_SIZE', 50))
        logger.info("Supabase connection initialized")

    def get_pending_jobs(self, limit: int = 50) -> list:
        """Fetch pending jobs from Supabase REST API"""
        try:
            url = f"{self.supabase_url}/rest/v1/scrape_jobs?status=eq.pending&limit={limit}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json() if response.json() else []
        except Exception as e:
            logger.error(f"Error fetching jobs: {str(e)}")
            return []

    def update_job_status(self, job_id: int, status: str, **kwargs) -> bool:
        """Update job status via REST API"""
        try:
            url = f"{self.supabase_url}/rest/v1/scrape_jobs?id=eq.{job_id}"
            data = {'status': status, **kwargs}
            response = requests.patch(url, json=data, headers=self.headers)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error updating job {job_id}: {str(e)}")
            return False

    def insert_result(self, result_data: dict) -> bool:
        """Insert result via REST API"""
        try:
            url = f"{self.supabase_url}/rest/v1/scrape_results"
            response = requests.post(url, json=result_data, headers=self.headers)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error inserting result: {str(e)}")
            return False

    def process_job(self, job: dict) -> bool:
        """Process a single job"""
        job_id = job['id']
        username = job['username']

        try:
            # Update status to processing
            self.update_job_status(job_id, 'processing')

            # Scrape profile
            result = self.scraper.scrape_profile(username)

            if result is None:
                self.update_job_status(job_id, 'failed', error='Scraping failed')
                return False

            # Store results
            result_data = {
                'username': username,
                'instagram': result['links'].get('instagram'),
                'twitter': result['links'].get('twitter'),
                'tiktok': result['links'].get('tiktok'),
                'telegram': result['links'].get('telegram'),
                'youtube': result['links'].get('youtube'),
                'snapchat': result['links'].get('snapchat'),
                'twitch': result['links'].get('twitch'),
                'reddit': result['links'].get('reddit'),
                'github': result['links'].get('github'),
                'linkedin': result['links'].get('linkedin'),
                'raw_bio': result['bio'],
                'job_id': job_id
            }

            self.insert_result(result_data)

            # Mark job as completed
            self.update_job_status(job_id, 'completed')

            logger.info(f"Completed job {job_id}: {username}")
            return True

        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")
            self.update_job_status(job_id, 'failed', error=str(e))
            return False

    def run_worker(self):
        """Main worker loop"""
        logger.info(f"Worker started with {self.max_workers} parallel threads")

        while True:
            jobs = self.get_pending_jobs(self.batch_size)

            if not jobs:
                logger.info("No pending jobs, waiting...")
                time.sleep(5)
                continue

            logger.info(f"Processing {len(jobs)} jobs")

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(self.process_job, job): job for job in jobs}

                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Unexpected error: {str(e)}")

            time.sleep(1)

if __name__ == '__main__':
    worker = SupabaseWorker()
    worker.run_worker()
