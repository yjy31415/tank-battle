"""Data loader: fetch all A-share stock daily OHLCV data via AKShare."""
import os
import sys
import time
import traceback
from datetime import datetime, timedelta

import akshare as ak
import pandas as pd

from config import config


def fetch_stock_list() -> pd.DataFrame:
    """Fetch all A-share stock codes and names.
    Tries multiple sources and returns the one with the most stocks."""
    best_df = None
    best_len = 0

    sources = [
        ("info", lambda: ak.stock_info_a_code_name()),
        ("sina", lambda: _rename_cn_cols(ak.stock_zh_a_spot())),
        ("em", lambda: _rename_cn_cols(ak.stock_zh_a_spot_em())),
    ]

    for _name, fetcher in sources:
        try:
            df = fetcher()
            if df is not None and not df.empty and len(df) > best_len:
                best_df = df
                best_len = len(df)
        except Exception:
            continue

    if best_df is not None:
        return best_df
    return pd.DataFrame(columns=["code", "name"])


def _rename_cn_cols(df):
    """Rename Chinese columns to English."""
    df = df[["代码", "名称"]].copy()
    df.columns = ["code", "name"]
    return df


def fetch_stock_daily(code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch daily OHLCV for a single stock via Tencent source.

    Returns DataFrame with columns:
        date, open, high, low, close, amount
    """
    try:
        # Strip any existing exchange prefix (bj/sh/sz)
        code_clean = code.replace("bj", "").replace("sh", "").replace("sz", "")
        # Determine market prefix for Tencent source
        if code_clean.startswith(("6", "5")):
            symbol = f"sh{code_clean}"
        else:
            symbol = f"sz{code_clean}"

        df = ak.stock_zh_a_hist_tx(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
        )
        if df is None or df.empty:
            return pd.DataFrame()

        df = df.rename(columns={
            "date": "date",
            "open": "open",
            "close": "close",
            "high": "high",
            "low": "low",
            "amount": "amount",
        })
        df["date"] = pd.to_datetime(df["date"])
        # Ensure numeric types
        for col in ["open", "high", "low", "close", "amount"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Add a synthetic volume column (not provided by Tencent source, use 0)
        df["volume"] = 0

        df = df[["date", "open", "high", "low", "close", "volume", "amount"]].copy()
        df["code"] = code
        return df.dropna(subset=["open", "close"])
    except Exception:
        return pd.DataFrame()


def is_st_stock(code: str, name: str) -> bool:
    """Check if stock is ST or *ST."""
    return "ST" in name


def is_star_stock(code: str, name: str) -> bool:
    """Check if stock is *ST (delisting risk)."""
    return "*ST" in name or "ST" == name[:2]


def get_stock_type(code: str, name: str) -> str:
    """Determine stock type for limit-up ratio.

    Returns: 'st' | 'star' | 'gem' | 'star_market' | 'bse' | 'normal'
    """
    if is_star_stock(code, name):
        return "star"
    if is_st_stock(code, name):
        return "st"
    # Strip exchange prefix if present
    code_clean = code.replace("bj", "").replace("sh", "").replace("sz", "")
    if code_clean.startswith("300") or code_clean.startswith("301"):
        return "gem"
    if code_clean.startswith("688"):
        return "star_market"
    if code_clean.startswith("8") or code_clean.startswith("92"):
        return "bse"
    return "normal"


def limit_up_ratio(stock_type: str) -> float:
    """Return limit-up ratio for stock type."""
    ratios = {
        "st": 1.05,
        "star": 1.05,
        "gem": 1.20,
        "star_market": 1.20,
        "bse": 1.30,
        "normal": 1.10,
    }
    return ratios.get(stock_type, 1.10)
