# OnlyFans Social Media Scraper

Bulk scraper to extract social media links (Instagram, Twitter, TikTok, etc.) from OnlyFans profiles at scale.

## Setup

### 1. Supabase Setup

1. Go to [supabase.com](https://supabase.com) and login
2. Create a new project or use existing
3. Go to SQL Editor → Create new query
4. Copy-paste the entire `supabase_schema.sql` file and run it
5. Note your `Project URL` and `Anon Key` (Settings → API)

### 2. Local Development

```bash
# Clone repo
git clone <your-repo> && cd onlyfans-scraper

# Create .env file
cp .env.example .env

# Edit .env with your Supabase credentials
# SUPABASE_URL=https://xxx.supabase.co
# SUPABASE_KEY=xxx

# Install dependencies
pip install -r requirements.txt

# Import your usernames
python import_usernames.py your_usernames.csv

# Run worker locally (processes jobs)
python worker.py
```

### 3. Deploy to Railway

1. Push to GitHub
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. Go to [railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select this repository
5. Add environment variables (Settings):
   - `SUPABASE_URL` = your Supabase URL
   - `SUPABASE_KEY` = your Supabase anon key
   - `MAX_WORKERS` = 10 (for free tier)
   - `BATCH_SIZE` = 50

6. Railway will automatically read `Procfile` and deploy

### 4. Import Usernames

Your CSV should have usernames in first column. Example:

```
username
johnsmith
janesmith
testuser
```

Then run:
```bash
python import_usernames.py usernames.csv
```

## How It Works

1. **Scraper** - Fetches OnlyFans profile page and extracts social media links from bio
2. **Worker** - Continuously pulls pending jobs from Supabase and processes them in parallel
3. **Results** - Stores all found social media links in `scrape_results` table

## Monitoring

Check progress in Supabase:
```sql
-- Check how many completed
SELECT COUNT(*) FROM scrape_jobs WHERE status = 'completed';

-- Check failed jobs
SELECT * FROM scrape_jobs WHERE status = 'failed' LIMIT 10;

-- View results
SELECT * FROM scrape_results LIMIT 100;
```

## Performance

- **Workers:** 10 parallel threads per instance
- **Batch size:** 50 usernames per batch
- **Est. time for 100k:** ~20-30 hours (can scale up workers)

## Environment Variables

- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon key
- `MAX_WORKERS` - Number of parallel threads (default: 10)
- `BATCH_SIZE` - Jobs to fetch per cycle (default: 50)

## Scaling

To process faster:
1. Increase `MAX_WORKERS` (e.g., 20-30)
2. Deploy multiple worker instances on Railway
3. Increase `BATCH_SIZE`

## Extracted Data

Results table contains:
- `username` - OnlyFans username
- `instagram`, `twitter`, `tiktok`, `telegram`, `youtube`, `snapchat`, `website` - Extracted handles
- `raw_bio` - Full bio text
- `scraped_at` - When it was scraped

## Export Results

```bash
# From Supabase SQL
SELECT * FROM scrape_results WHERE instagram IS NOT NULL;
```

Then download as CSV from Supabase UI or use Python:
```python
from supabase import create_client
client = create_client(url, key)
results = client.table('scrape_results').select('*').execute()
```
