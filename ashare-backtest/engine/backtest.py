"""Daily-loop backtest engine."""
from datetime import date, timedelta
from typing import Dict

import pandas as pd

from config import config
from engine.portfolio import Portfolio
from engine.broker import execute_buy, execute_sell
from strategy.triple_limit_up import TripleLimitUpStrategy


class BacktestEngine:
    def __init__(self, stock_data: Dict[str, pd.DataFrame],
                 stock_names: Dict[str, str]):
        self.stock_data = stock_data
        self.stock_names = stock_names
        self.portfolio = Portfolio(config.initial_capital)
        self.strategy = TripleLimitUpStrategy()

        # precompute signals for all stocks
        for code, df in stock_data.items():
            name = stock_names.get(code, code)
            self.strategy.load_stock(code, name, df)

    def run(self) -> Portfolio:
        """Execute the backtest."""
        # Determine trading days from data
        all_dates = set()
        for df in self.stock_data.values():
            all_dates.update(df["date"].dt.date.tolist())
        trading_days = sorted(all_dates)

        if len(trading_days) < 30:
            print("WARNING: Less than 30 trading days of data. Results may be unreliable.")

        prev_day = None

        for i, dt in enumerate(trading_days):
            # ---- MORNING: Sell positions bought on previous day ----
            if prev_day is not None:
                for symbol, pos in list(self.portfolio.positions.items()):
                    # Positions are sold the day after entry (T+1)
                    if pos.entry_date == prev_day:
                        df = self.stock_data.get(symbol)
                        if df is None:
                            continue
                        day_data = df[df["date"] == pd.Timestamp(dt)]
                        if day_data.empty:
                            # Stock may be suspended, carry position
                            continue
                        open_price = float(day_data.iloc[0]["open"])
                        sell_result = execute_sell(symbol, pos.shares, open_price)
                        self.portfolio.remove_position(
                            symbol, sell_result["price"], dt,
                            sell_result["commission"],
                            sell_result["stamp_duty"],
                            sell_result["transfer_fee"],
                        )

            # ---- Generate buy signals ----
            signals = self.strategy.get_signals_on_date(dt)

            if not signals.empty:
                # Sort by: prefer stocks whose streak ended more recently
                available_cash_per_stock = self.portfolio.can_allocate(
                    dt, config.daily_capital_fraction
                )

                # Cap number of concurrent positions
                max_new = min(
                    len(signals),
                    config.max_stocks_per_day - len(self.portfolio.positions),
                )
                max_new = max(0, max_new)

                if max_new > 0 and available_cash_per_stock > 0:
                    cash_per_stock = available_cash_per_stock / max_new

                    filled = 0
                    for _, row in signals.iterrows():
                        if filled >= max_new:
                            break

                        code = row["code"]
                        # Skip if already holding
                        if code in self.portfolio.positions:
                            continue

                        # Check fill condition (high touch)
                        if not self.strategy.can_fill_buy(row):
                            continue

                        lu_price = float(row["limit_up_price"])
                        result = execute_buy(code, lu_price, cash_per_stock)
                        if result is None:
                            continue

                        self.portfolio.add_position(
                            code, result["shares"], result["price"], dt,
                            result["commission"], result["transfer_fee"],
                        )
                        filled += 1

            # ---- EOD: Record snapshot ----
            self.portfolio.record_daily(dt)
            prev_day = dt

        return self.portfolio
