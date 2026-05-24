"""三连板 + 断板≥2天 strategy signal generator."""
from datetime import date
from typing import Dict, List, Optional

import pandas as pd

from config import config
from strategy.limit_up import detect_streaks
from data.loader import get_stock_type


class TripleLimitUpStrategy:
    """Strategy: buy stocks with 3 consecutive limit-ups in 30 days, broken ≥2 days."""

    def __init__(self):
        self.stock_data: Dict[str, pd.DataFrame] = {}
        self.signals: Dict[str, pd.DataFrame] = {}

    def load_stock(self, code: str, name: str, df: pd.DataFrame):
        """Load OHLCV data for a stock and precompute signals."""
        stock_type = get_stock_type(code, name)
        df_with_signals = detect_streaks(df, stock_type)
        self.stock_data[code] = df_with_signals

    def get_signals_on_date(self, target_date: date) -> pd.DataFrame:
        """Get all buy signals on a given date.

        Returns DataFrame with columns: code, name, limit_up_price, close
        """
        results = []
        for code, df in self.stock_data.items():
            day_data = df[df["date"] == pd.Timestamp(target_date)]
            if day_data.empty:
                continue
            row = day_data.iloc[0]
            if row["signal"]:
                results.append({
                    "code": code,
                    "limit_up_price": row["limit_up_price"],
                    "close": row["close"],
                    "high": row["high"],
                })
        return pd.DataFrame(results) if results else pd.DataFrame(
            columns=["code", "limit_up_price", "close", "high"])

    def can_fill_buy(self, row: pd.Series) -> bool:
        """Check if a buy order can be filled based on fill mode."""
        mode = config.fill_simulation_mode
        if mode == "high_touch":
            return float(row["high"]) >= float(row["limit_up_price"])
        elif mode == "close_match":
            return float(row["close"]) >= float(row["limit_up_price"]) * 0.995
        return True
