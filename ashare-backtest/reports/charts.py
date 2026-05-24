"""Charts: equity curve, drawdown, daily returns."""
import os
from datetime import date
from typing import List

import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

from config import config


# Set Chinese-capable font
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def _ensure_output_dir():
    os.makedirs(config.output_dir, exist_ok=True)


def _to_dataframe(equity_history: List[tuple]) -> pd.DataFrame:
    df = pd.DataFrame(equity_history, columns=["date", "equity", "cash", "position_value"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    df["daily_return"] = df["equity"].pct_change()
    df["cumulative_return"] = (1 + df["daily_return"]).cumprod() - 1
    df["running_max"] = df["equity"].cummax()
    df["drawdown"] = (df["equity"] - df["running_max"]) / df["running_max"]
    return df


def plot_equity_curve(df: pd.DataFrame):
    """Plot equity curve and cumulative return."""
    _ensure_output_dir()
    fig, ax1 = plt.subplots(figsize=(14, 7))

    ax1.plot(df.index, df["equity"], color="#1f77b4", linewidth=1.5, label="Portfolio Equity")
    ax1.set_ylabel("Equity (CNY)", fontsize=12)
    ax1.set_xlabel("Date", fontsize=12)
    ax1.set_title("Equity Curve", fontsize=14, fontweight="bold")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

    ax2 = ax1.twinx()
    ax2.plot(df.index, df["cumulative_return"] * 100, color="#ff7f0e",
             linewidth=1.0, linestyle="--", alpha=0.7, label="Cumulative Return %")
    ax2.set_ylabel("Cumulative Return (%)", fontsize=12)
    ax2.legend(loc="upper right")

    fig.tight_layout()
    path = os.path.join(config.output_dir, "equity_curve.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Equity curve saved: {path}")


def plot_drawdown(df: pd.DataFrame):
    """Plot drawdown chart."""
    _ensure_output_dir()
    fig, ax = plt.subplots(figsize=(14, 5))

    ax.fill_between(df.index, 0, df["drawdown"] * 100,
                    color="#d62728", alpha=0.3, label="Drawdown")
    ax.plot(df.index, df["drawdown"] * 100, color="#d62728", linewidth=1.0)
    ax.set_ylabel("Drawdown (%)", fontsize=12)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_title("Drawdown", fontsize=14, fontweight="bold")
    ax.legend(loc="lower left")
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_formatter(ticker.PercentFormatter())

    # invert y-axis for drawdown
    ax.invert_yaxis()

    fig.tight_layout()
    path = os.path.join(config.output_dir, "drawdown.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Drawdown chart saved: {path}")


def plot_daily_returns(df: pd.DataFrame):
    """Plot daily returns as bar chart."""
    _ensure_output_dir()
    fig, ax = plt.subplots(figsize=(14, 5))

    returns_pct = df["daily_return"] * 100
    colors = ["#d62728" if r < 0 else "#2ca02c" for r in returns_pct]
    ax.bar(df.index, returns_pct, color=colors, width=0.8, alpha=0.8)
    ax.set_ylabel("Daily Return (%)", fontsize=12)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_title("Daily Returns", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")

    # cumulative overlay
    ax2 = ax.twinx()
    ax2.plot(df.index, df["cumulative_return"] * 100, color="#1f77b4",
             linewidth=1.5, alpha=0.7, label="Cumulative %")
    ax2.set_ylabel("Cumulative Return (%)", fontsize=12)
    ax2.legend(loc="upper left")

    fig.tight_layout()
    path = os.path.join(config.output_dir, "daily_returns.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Daily returns chart saved: {path}")


def generate_all_charts(equity_history: List[tuple]):
    """Generate all three charts."""
    df = _to_dataframe(equity_history)
    if df.empty:
        print("No equity history to chart.")
        return
    plot_equity_curve(df)
    plot_drawdown(df)
    plot_daily_returns(df)
