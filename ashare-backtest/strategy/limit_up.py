"""Limit-up price calculator and streak detector utilities."""
import pandas as pd

from config import config
from data.loader import limit_up_ratio, get_stock_type


def compute_limit_up_price(prev_close: float, stock_type: str) -> float:
    """Compute theoretical limit-up price for A-shares."""
    ratio = limit_up_ratio(stock_type)
    return round(prev_close * ratio, 2)


def is_limit_up(close: float, limit_up_px: float, tolerance: float = 0.005) -> bool:
    """Check if close price is at limit-up (within tolerance)."""
    if limit_up_px <= 0:
        return False
    return close >= limit_up_px * (1 - tolerance)


def detect_streaks(df: pd.DataFrame, stock_type: str) -> pd.DataFrame:
    """Detect 3+ consecutive limit-up streaks and broken days for a stock.

    Adds columns to df:
        limit_up_price: theoretical limit-up price for the day
        is_limit_up_day: whether the stock hit limit-up that day
        consecutive_count: running count of consecutive limit-up days
        broken_days: days since last 3+ streak ended (only valid within window)
        signal: True if stock is eligible for buy (had 三连板 in last 30 days AND 断板≥2天)

    Returns the modified DataFrame.
    """
    df = df.copy()
    n = len(df)

    limit_up_prices = [0.0] * n
    is_lu = [False] * n
    consecutive = [0] * n
    broken_days_list = [None] * n
    signals = [False] * n

    # tracking state
    consec = 0
    broken = None  # None = no active streak, int = broken days count
    streak_end_date = None

    for i in range(n):
        if i == 0:
            # First day: no previous close, cannot compute limit-up price
            prev_close = 0.0
        else:
            prev_close = df.iloc[i - 1]["close"]

        lu_price = compute_limit_up_price(prev_close, stock_type)
        limit_up_prices[i] = lu_price

        close_px = float(df.iloc[i]["close"])
        today_lu = is_limit_up(close_px, lu_price)
        is_lu[i] = today_lu
        today_date = df.iloc[i]["date"]

        if today_lu:
            consec += 1
            consecutive[i] = consec
            # if we had a broken streak going, this new limit-up resets it
            broken = None
            streak_end_date = None
        else:
            if consec >= config.consecutive_limit_up_required:
                # Record a streak: ended on day i-1
                streak_end_date = df.iloc[i - 1]["date"]
                broken = 1  # first broken day
            elif broken is not None:
                broken += 1

            consecutive[i] = consec
            consec = 0

        broken_days_list[i] = broken

        # Signal: broken >= required AND streak end within 30 calendar days
        if broken is not None and broken >= config.broken_days_required and streak_end_date is not None:
            days_since_streak = (today_date - streak_end_date).days
            if days_since_streak <= config.streak_lookback_days:
                signals[i] = True

    df["limit_up_price"] = limit_up_prices
    df["is_limit_up_day"] = is_lu
    df["consecutive_count"] = consecutive
    df["broken_days"] = broken_days_list
    df["signal"] = signals
    df["stock_type"] = stock_type
    return df
