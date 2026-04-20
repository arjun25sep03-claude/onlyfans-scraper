#!/bin/bash

echo "🚀 OnlyFans Scraper Setup"
echo "========================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

echo "✅ Python found"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Create .env from template
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ .env created - please edit with your Supabase credentials"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your Supabase URL and Key"
echo "2. Run Supabase SQL from supabase_schema.sql"
echo "3. Prepare your CSV file with usernames"
echo "4. Run: python import_usernames.py your_file.csv"
echo "5. Run: python worker.py"
