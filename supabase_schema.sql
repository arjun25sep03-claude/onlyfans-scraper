-- Jobs table to track processing status
CREATE TABLE IF NOT EXISTS scrape_jobs (
  id BIGSERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  status TEXT DEFAULT 'pending', -- pending, processing, completed, failed
  created_at TIMESTAMP DEFAULT NOW(),
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  error TEXT
);

-- Results table to store extracted social media links
CREATE TABLE IF NOT EXISTS scrape_results (
  id BIGSERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  instagram TEXT,
  twitter TEXT,
  tiktok TEXT,
  telegram TEXT,
  youtube TEXT,
  snapchat TEXT,
  website TEXT,
  raw_bio TEXT,
  scraped_at TIMESTAMP DEFAULT NOW(),
  job_id BIGINT REFERENCES scrape_jobs(id)
);

-- Create indexes for fast queries
CREATE INDEX idx_jobs_status ON scrape_jobs(status);
CREATE INDEX idx_jobs_created ON scrape_jobs(created_at);
CREATE INDEX idx_results_username ON scrape_results(username);
