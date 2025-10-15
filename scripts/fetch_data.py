"""
EconomyTrends - fetch_data.py

Fetches key economic series from FRED, saves CSVs, produces charts,
and writes a short CSV summary. Reads FRED API key from env var:
FRED_API_KEY (set locally in .env for dev, and add as GitHub Action secret).
"""

import os
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from fredapi import Fred

# --- Config ---
OUTPUT_RAW = "data/raw"
OUTPUT_PROCESSED = "data/processed"
CHART_DIR = "charts"

# Indicators to fetch: {fred_code: friendly_name}
INDICATORS = {
    "CPIAUCSL": "CPI (All Items, monthly)",
    "UNRATE": "Unemployment Rate (monthly)",
    "FEDFUNDS": "Federal Funds Rate (daily)",
    "GDP": "Real GDP (quarterly)",
    "PAYEMS": "Nonfarm Payrolls (monthly)",
    # add more codes you want to track
}

# Create dirs
os.makedirs(OUTPUT_RAW, exist_ok=True)
os.makedirs(OUTPUT_PROCESSED, exist_ok=True)
os.makedirs(CHART_DIR, exist_ok=True)

# --- Get FRED API key from env var ---
FRED_API_KEY = os.getenv("FRED_API_KEY")
if not FRED_API_KEY:
    raise SystemExit("FRED_API_KEY environment variable not set. Obtain one at https://fred.stlouisfed.org/")

fred = Fred(api_key=FRED_API_KEY)

def fetch_series(code):
    """Fetch a series and return a DataFrame with a friendly column name."""
    print(f"Fetching {code} ...")
    series = fred.get_series(code)
    df = pd.DataFrame(series, columns=[INDICATORS.get(code, code)])
    df.index.name = "Date"
    return df

def main():
    data_frames = {}
    for code in INDICATORS:
        try:
            df = fetch_series(code)
            # Save raw CSV (timestamped)
            raw_path = os.path.join(OUTPUT_RAW, f"{code}.csv")
            df.to_csv(raw_path)
            data_frames[INDICATORS[code]] = df
        except Exception as e:
            print(f"Warning: failed to fetch {code}: {e}")

    # Merge by date (outer join)
    combined = pd.concat(data_frames.values(), axis=1)
    combined.sort_index(inplace=True)

    # Save processed combined file (rolling up only latest X years to save repo space)
    cutoff = combined.index.max() - pd.DateOffset(years=10)  # keep last 10 years by default
    processed = combined.loc[cutoff:]
    processed_path = os.path.join(OUTPUT_PROCESSED, "economic_summary_{}.csv".format(datetime.utcnow().strftime("%Y%m%d")))
    processed.to_csv(processed_path)
    print(f"Processed data saved to {processed_path}")

    # Create simple line charts for each column (last N years)
    for col in processed.columns:
        plt.figure(figsize=(10, 4))
        series = processed[col].dropna()
        if series.empty:
            continue
        # Plot last 5 years if daily/weekly, else last 10 for monthly/quarterly
        try:
            # automatic resampling for daily series to monthly for neat charts
            if (series.index.freq is None) and (len(series) > 365):
                plot_series = series.resample('M').mean()
            else:
                plot_series = series
        except Exception:
            plot_series = series

        plot_series.plot(title=col)
        plt.grid(True)
        plt.tight_layout()
        filename = os.path.join(CHART_DIR, f"{col.lower().replace(' ', '_')}.png")
        plt.savefig(filename)
        plt.close()
        print(f"Saved chart: {filename}")

    # Small human-readable summary (last value changes)
    summary_rows = []
    for col in processed.columns:
        s = processed[col].dropna()
        if s.empty:
            continue
        last = s.iloc[-1]
        prev = s.iloc[-2] if len(s) >= 2 else None
        pct_change = None
        if prev is not None and prev != 0:
            try:
                pct_change = (last - prev) / abs(prev) * 100
            except Exception:
                pct_change = None
        summary_rows.append({
            "indicator": col,
            "last_date": s.index[-1].strftime("%Y-%m-%d"),
            "last_value": last,
            "prev_value": prev,
            "pct_change": round(pct_change, 4) if pct_change is not None else ""
        })

    summary_df = pd.DataFrame(summary_rows)
    summary_csv = os.path.join(OUTPUT_PROCESSED, "latest_summary_{}.csv".format(datetime.utcnow().strftime("%Y%m%d")))
    summary_df.to_csv(summary_csv, index=False)
    print(f"Summary saved to {summary_csv}")

    print("EconomyTrends update completed at", datetime.utcnow().isoformat())

if __name__ == "__main__":
    main()
