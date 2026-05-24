from dataclasses import dataclass, field


@dataclass
class BacktestConfig:
    # ---- Data ----
    lookback_months: int = 4          # fetch 4 months of data
    backtest_months: int = 3          # actual backtest period
    streak_lookback_days: int = 30    # 三连板 must be within 30 calendar days
    cache_dir: str = "./cache"

    # ---- Universe ----
    exclude_st: bool = False          # exclude ST stocks
    exclude_star: bool = True         # exclude *ST (delisting risk) stocks

    # ---- Capital ----
    initial_capital: float = 1_000_000.0
    daily_capital_fraction: float = 0.10    # 1/10 of equity per day
    max_stocks_per_day: int = 5             # cap concurrent buys

    # ---- Strategy ----
    consecutive_limit_up_required: int = 3   # 三连板
    broken_days_required: int = 2            # 断板超过2天
    fill_simulation_mode: str = "high_touch" # "high_touch" | "close_match"

    # ---- Lot ----
    lot_size: int = 100                      # A-share lot size

    # ---- Costs ----
    commission_rate: float = 0.00025         # 万2.5
    commission_min: float = 5.0              # 最低5元
    stamp_duty_rate: float = 0.0005          # 卖出万5
    transfer_fee_rate: float = 0.00001       # 十万分之一

    # ---- Output ----
    output_dir: str = "./output"
    benchmark_symbol: str = "sh000001"       # SSE Composite for overlay

    # ---- Derived ----
    python_exe: str = "C:/Users/Administrator/AppData/Local/Programs/Python/Python312/python.exe"


# singleton
config = BacktestConfig()
