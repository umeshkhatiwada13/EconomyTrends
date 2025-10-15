# EconomyTrends

EconomyTrends is an automated GitHub-based pipeline that fetches macroeconomic indicators from FRED, processes them, generates charts, and commits results to this repository on a schedule.

## What it does
- Downloads key economic indicators from FRED (CPI, Unemployment, Fed funds rate, GDP, etc.)
- Produces CSVs and charts
- Writes a short insights markdown file
- Runs automatically in GitHub Actions (daily by default)

## How to run locally
1. Get a FRED API key: https://fred.stlouisfed.org/
2. Set env var: `export FRED_API_KEY="your_key_here"`
3. Install deps: `pip install -r requirements.txt`
4. Run: `python scripts/fetch_data.py`

## Automation
A GitHub Actions workflow (in `.github/workflows/update_data.yml`) runs daily and commits updates.

## License
MIT
