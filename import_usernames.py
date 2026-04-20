import os
import sys
import csv
import logging
from supabase import create_client, Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UsernameImporter:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

    def import_from_csv(self, csv_file: str):
        """Import usernames from CSV file"""
        usernames = []

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                # If first column is username
                reader = csv.DictReader(f)
                for row in reader:
                    # Assuming first column has username
                    username = row[list(row.keys())[0]].strip()
                    if username:
                        usernames.append({'username': username, 'status': 'pending'})

        except Exception as e:
            logger.error(f"Error reading CSV: {str(e)}")
            return False

        if not usernames:
            logger.warning("No usernames found in CSV")
            return False

        # Insert in batches
        batch_size = 1000
        for i in range(0, len(usernames), batch_size):
            batch = usernames[i:i+batch_size]
            try:
                self.supabase.table('scrape_jobs').upsert(batch).execute()
                logger.info(f"Imported {min(batch_size, len(usernames)-i)} usernames")
            except Exception as e:
                logger.error(f"Error importing batch: {str(e)}")

        logger.info(f"✅ Successfully imported {len(usernames)} usernames")
        return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python import_usernames.py <csv_file>")
        sys.exit(1)

    importer = UsernameImporter()
    importer.import_from_csv(sys.argv[1])
