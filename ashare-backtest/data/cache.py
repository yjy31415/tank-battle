"""Cache management: save/load stock data to/from local pickle files."""
import os
from datetime import datetime, timedelta

import pandas as pd

from config import config


def cache_path(code: str) -> str:
    """Return cache file path for a stock code."""
    return os.path.join(config.cache_dir, f"{code}.pkl")


def is_cached(code: str, max_age_days: int = 1) -> bool:
    """Check if a valid cache exists for the stock."""
    path = cache_path(code)
    if not os.path.exists(path):
        return False
    mtime = datetime.fromtimestamp(os.path.getmtime(path))
    return (datetime.now() - mtime) < timedelta(days=max_age_days)


def load_from_cache(code: str) -> pd.DataFrame | None:
    """Load stock data from cache if available."""
    path = cache_path(code)
    if os.path.exists(path):
        try:
            return pd.read_pickle(path)
        except Exception:
            return None
    return None


def save_to_cache(code: str, df: pd.DataFrame):
    """Save stock data to cache."""
    path = cache_path(code)
    df.to_pickle(path)


def load_or_fetch(code: str, start_date: str, end_date: str,
                  force_refresh: bool = False) -> pd.DataFrame:
    """Load from cache or fetch from AKShare."""
    from data.loader import fetch_stock_daily

    if not force_refresh and is_cached(code):
        df = load_from_cache(code)
        if df is not None and not df.empty:
            return df

    df = fetch_stock_daily(code, start_date, end_date)
    if not df.empty:
        save_to_cache(code, df)
    return df
