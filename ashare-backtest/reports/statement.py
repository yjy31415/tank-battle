"""Trading statement / delivery note (交割单) export."""
import os
from typing import List

import numpy as np
import pandas as pd
from tabulate import tabulate

from config import config


def generate_statement(trade_log: List[dict], equity_history: List[tuple]):
    """Generate 交割单 CSV and print summary to console."""
    os.makedirs(config.output_dir, exist_ok=True)

    if not trade_log:
        print("No trades executed. No statement generated.")
        return

    df = pd.DataFrame(trade_log)

    # Format columns
    df_out = pd.DataFrame()
    df_out["成交日期"] = df["sell_date"].apply(lambda d: d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d))
    df_out["证券代码"] = df["code"]
    df_out["买入日期"] = df["buy_date"].apply(lambda d: d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d))
    df_out["卖出日期"] = df["sell_date"].apply(lambda d: d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d))
    df_out["成交数量"] = df["shares"]
    df_out["买入价"] = df["buy_price"].round(2)
    df_out["卖出价"] = df["sell_price"].round(2)
    df_out["买入金额"] = df["buy_value"].round(2)
    df_out["卖出金额"] = df["sell_value"].round(2)
    df_out["买入佣金"] = df["buy_commission"].round(2)
    df_out["卖出佣金"] = df["sell_commission"].round(2)
    df_out["印花税"] = df["stamp_duty"].round(2)
    df_out["过户费(买)"] = df["buy_transfer_fee"].round(2)
    df_out["过户费(卖)"] = df["sell_transfer_fee"].round(2)
    df_out["总成本"] = df["total_cost"].round(2)
    df_out["净收入"] = df["net_proceeds"].round(2)
    df_out["盈亏金额"] = df["pnl"].round(2)
    df_out["收益率%"] = df["return_pct"].round(2)

    # Save CSV
    csv_path = os.path.join(config.output_dir, "trade_statement.csv")
    df_out.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"  Statement saved: {csv_path}")

    # ---- Summary Statistics ----
    print("\n" + "=" * 70)
    print("  交 割 单 统 计 摘 要")
    print("=" * 70)

    n_trades = len(df)
    n_wins = (df["pnl"] > 0).sum()
    n_losses = (df["pnl"] <= 0).sum()
    win_rate = n_wins / n_trades * 100 if n_trades > 0 else 0

    total_pnl = df["pnl"].sum()
    total_commission = df["buy_commission"].sum() + df["sell_commission"].sum()
    total_stamp_duty = df["stamp_duty"].sum()
    total_transfer = df["buy_transfer_fee"].sum() + df["sell_transfer_fee"].sum()
    total_cost_total = total_commission + total_stamp_duty + total_transfer

    avg_return = df["return_pct"].mean() if n_trades > 0 else 0
    max_return = df["return_pct"].max() if n_trades > 0 else 0
    min_return = df["return_pct"].min() if n_trades > 0 else 0
    avg_win = df[df["pnl"] > 0]["return_pct"].mean() if n_wins > 0 else 0
    avg_loss = df[df["pnl"] <= 0]["return_pct"].mean() if n_losses > 0 else 0

    # Final equity
    if equity_history:
        final_equity = equity_history[-1][1]
        initial_equity = equity_history[0][1]
        total_return = (final_equity / initial_equity - 1) * 100
    else:
        final_equity = 0
        initial_equity = 0
        total_return = 0

    # Max drawdown
    eq_df = pd.DataFrame(equity_history, columns=["date", "equity", "cash", "position_value"])
    if not eq_df.empty:
        eq_df["running_max"] = eq_df["equity"].cummax()
        eq_df["drawdown"] = (eq_df["equity"] - eq_df["running_max"]) / eq_df["running_max"]
        max_dd = eq_df["drawdown"].min() * 100
    else:
        max_dd = 0

    # Sharpe ratio (annualized)
    if not eq_df.empty:
        daily_ret = eq_df["equity"].pct_change().dropna()
        if len(daily_ret) > 1 and daily_ret.std() > 0:
            sharpe = (daily_ret.mean() / daily_ret.std()) * np.sqrt(252)
        else:
            sharpe = 0
    else:
        sharpe = 0

    print(f"  初始资金:      {initial_equity:>12,.2f} CNY")
    print(f"  最终权益:      {final_equity:>12,.2f} CNY")
    print(f"  总收益率:      {total_return:>11.2f}%")
    print(f"  总盈亏金额:    {total_pnl:>12,.2f} CNY")
    print(f"  最大回撤:      {max_dd:>11.2f}%")
    print(f"  年化夏普比率:  {sharpe:>11.2f}")
    print("-" * 70)
    print(f"  总交易次数:    {n_trades:>11}")
    print(f"  盈利次数:      {n_wins:>11}  (胜率 {win_rate:.1f}%)")
    print(f"  亏损次数:      {n_losses:>11}")
    print(f"  平均收益率:    {avg_return:>11.2f}%")
    print(f"  最大单笔盈利:  {max_return:>11.2f}%")
    print(f"  最大单笔亏损:  {min_return:>11.2f}%")
    print(f"  平均盈利:      {avg_win:>11.2f}%")
    print(f"  平均亏损:      {avg_loss:>11.2f}%")
    print("-" * 70)
    print(f"  总佣金:        {total_commission:>12,.2f} CNY")
    print(f"  总印花税:      {total_stamp_duty:>12,.2f} CNY")
    print(f"  总过户费:      {total_transfer:>12,.2f} CNY")
    print(f"  总交易成本:    {total_cost_total:>12,.2f} CNY")
    print("=" * 70)
