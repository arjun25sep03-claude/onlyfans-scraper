import os
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from supabase import create_client, Client
from scraper import OnlyFansScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SupabaseWorker:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        self.scraper = OnlyFansScraper()
        self.max_workers = int(os.getenv('MAX_WORKERS', 10))
        self.batch_size = int(os.getenv('BATCH_SIZE', 50))

    def get_pending_jobs(self, limit: int = 50) -> list:
        """Fetch pending jobs from Supabase"""
        try:
            response = self.supabase.table('scrape_jobs').select('id, username').eq('status', 'pending').limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching jobs: {str(e)}")
            return []

    def process_job(self, job: dict) -> bool:
        """Process a single job"""
        job_id = job['id']
        username = job['username']

        try:
            # Update status to processing
            self.supabase.table('scrape_jobs').update({'status': 'processing', 'started_at': 'now()'}).eq('id', job_id).execute()

            # Scrape profile
            result = self.scraper.scrape_profile(username)

            if result is None:
                self.supabase.table('scrape_jobs').update({
                    'status': 'failed',
                    'error': 'Scraping failed',
                    'completed_at': 'now()'
                }).eq('id', job_id).execute()
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
                'website': result['links'].get('website'),
                'raw_bio': result['bio'],
                'job_id': job_id
            }

            self.supabase.table('scrape_results').upsert(result_data).execute()

            # Mark job as completed
            self.supabase.table('scrape_jobs').update({
                'status': 'completed',
                'completed_at': 'now()'
            }).eq('id', job_id).execute()

            logger.info(f"Completed job {job_id}: {username}")
            return True

        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")
            self.supabase.table('scrape_jobs').update({
                'status': 'failed',
                'error': str(e),
                'completed_at': 'now()'
            }).eq('id', job_id).execute()
            return False

    def run_worker(self):
        """Main worker loop - continuously process jobs"""
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

            time.sleep(1)  # Small delay before next batch

if __name__ == '__main__':
    worker = SupabaseWorker()
    worker.run_worker()
