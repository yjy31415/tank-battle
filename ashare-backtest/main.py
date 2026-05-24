"""Main entry point: data loading -> backtest -> reports."""
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from data.loader import fetch_stock_list, fetch_stock_daily, get_stock_type
from data.cache import load_or_fetch
from engine.backtest import BacktestEngine
from reports.charts import generate_all_charts
from reports.statement import generate_statement


def _load_one(code, name, start_date, end_date, first_error=None):
    """Load data for a single stock, return (code, name, df_or_None)."""
    try:
        df = load_or_fetch(code, start_date, end_date)
        if df is not None and not df.empty and len(df) >= 20:
            return code, name, df
    except Exception as e:
        if first_error is not None and first_error[0] is None:
            first_error[0] = f"{code}: {type(e).__name__}: {e}"
    return code, name, None


def main():
    print("=" * 60)
    print("  A股三连板断板打板策略回测系统")
    print("=" * 60)
    print(f"  初始资金:   {config.initial_capital:,.0f} CNY")
    print(f"  每日仓位:   {config.daily_capital_fraction*100:.0f}%")
    print(f"  连板要求:   {config.consecutive_limit_up_required}连板")
    print(f"  断板要求:   >= {config.broken_days_required}天")
    print(f"  回看窗口:   {config.streak_lookback_days}天")
    print(f"  成交模式:   {config.fill_simulation_mode}")
    print()

    # ---- Data Loading ----
    print("[1/3] Loading A-share data...")
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=config.lookback_months * 31)).strftime("%Y%m%d")
    print(f"  Period: {start_date} ~ {end_date}")

    # Fetch stock list
    print("  Fetching stock list...")
    stock_list = fetch_stock_list()
    if stock_list is None or stock_list.empty:
        print("  ERROR: Could not fetch stock list. Exiting.")
        return
    print(f"  Total: {len(stock_list)} stocks")

    # Filter universe
    def should_include(row):
        code = str(row["code"])
        name = str(row.get("name", ""))
        # Strip exchange prefix if present (bj/sh/sz)
        code_clean = code.replace("bj", "").replace("sh", "").replace("sz", "")
        # Exclude 北交所 (8开头 and 9开头 like 92xxx) - 30% limit
        if code_clean.startswith("8"):
            return False
        if code_clean.startswith("92"):
            return False
        # Exclude *ST
        if "*ST" in name:
            return False
        return True

    stock_list = stock_list[stock_list.apply(should_include, axis=1)].copy()
    print(f"  After filtering: {len(stock_list)} stocks")

    # Parallel data fetching
    print("  Fetching daily OHLCV data (parallel, ~10 threads)...")
    stock_data = {}
    stock_names = {}
    success = 0
    fail = 0
    first_error = [None]  # list so can be mutated inside _load_one
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(_load_one, row["code"], row.get("name", row["code"]),
                          start_date, end_date, first_error): row["code"]
            for _, row in stock_list.iterrows()
        }
        completed = 0
        total = len(futures)
        for future in as_completed(futures):
            completed += 1
            code, name, df = future.result()
            stock_names[code] = name
            if df is not None:
                stock_data[code] = df
                success += 1
            else:
                fail += 1
                if first_error[0] is not None and fail == 1:
                    pass  # will print below
            if completed % 200 == 0 or completed == total:
                elapsed = time.time() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                eta = (total - completed) / rate if rate > 0 else 0
                print(f"    Progress: {completed}/{total} "
                      f"({rate:.1f}/s, ok={success}, fail={fail}, ETA {eta:.0f}s)")

    elapsed = time.time() - start_time
    print(f"  Data loading complete in {elapsed:.0f}s: {success} stocks loaded, {fail} skipped")
    if first_error[0] is not None:
        print(f"  First error sample: {first_error[0]}")

    if success == 0:
        print("ERROR: No stock data loaded. Check network or AKShare availability.")
        return

    # ---- Backtest ----
    print("\n[2/3] Running backtest...")
    engine = BacktestEngine(stock_data, stock_names)
    portfolio = engine.run()

    print(f"  Backtest complete: {len(portfolio.trade_log)} trades")
    print(f"  Final equity: {portfolio.equity:,.2f} CNY")
    total_return = (portfolio.equity / config.initial_capital - 1) * 100
    print(f"  Total return: {total_return:.2f}%")

    # ---- Reports ----
    print("\n[3/3] Generating reports...")
    generate_all_charts(portfolio.equity_history)
    generate_statement(portfolio.trade_log, portfolio.equity_history)

    print("\nDone! Check ./output/ for charts and trade statement.")


if __name__ == "__main__":
    main()
