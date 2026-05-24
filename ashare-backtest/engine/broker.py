"""Broker: order execution simulation with lot rounding and fees."""
from datetime import date

from config import config


def calculate_commission(trade_value: float) -> float:
    """Commission: 万2.5, min 5 CNY."""
    fee = trade_value * config.commission_rate
    return max(fee, config.commission_min)


def calculate_stamp_duty(sell_value: float) -> float:
    """Stamp duty: 万5, sell only."""
    return sell_value * config.stamp_duty_rate


def calculate_transfer_fee(trade_value: float) -> float:
    """Transfer fee: 十万分之一, both sides."""
    return trade_value * config.transfer_fee_rate


def round_lot(shares: int) -> int:
    """Round down to nearest lot (100 shares)."""
    return (shares // config.lot_size) * config.lot_size


def compute_buy_shares(allocated_cash: float, limit_up_price: float) -> int:
    """Compute how many shares can be bought with allocated cash at limit-up price,
    rounding down to lot size."""
    if limit_up_price <= 0:
        return 0
    ideal = allocated_cash / limit_up_price
    return round_lot(int(ideal))


def execute_buy(symbol: str, limit_up_price: float, available_cash: float) -> dict | None:
    """Simulate a buy order. Returns order dict or None if not enough cash."""
    shares = compute_buy_shares(available_cash, limit_up_price)
    if shares <= 0:
        return None

    trade_value = shares * limit_up_price
    commission = calculate_commission(trade_value)
    transfer_fee = calculate_transfer_fee(trade_value)
    total_required = trade_value + commission + transfer_fee

    # re-check cash sufficiency with fees
    if total_required > available_cash:
        # reduce shares until we fit
        while shares >= config.lot_size:
            shares -= config.lot_size
            trade_value = shares * limit_up_price
            commission = calculate_commission(trade_value)
            transfer_fee = calculate_transfer_fee(trade_value)
            total_required = trade_value + commission + transfer_fee
            if total_required <= available_cash:
                break
        if shares <= 0:
            return None

    return {
        "symbol": symbol,
        "shares": shares,
        "price": limit_up_price,
        "trade_value": trade_value,
        "commission": commission,
        "transfer_fee": transfer_fee,
        "total_required": total_required,
    }


def execute_sell(symbol: str, shares: int, open_price: float) -> dict:
    """Simulate a sell at market open. Returns proceeds dict."""
    sell_value = shares * open_price
    commission = calculate_commission(sell_value)
    stamp_duty = calculate_stamp_duty(sell_value)
    transfer_fee = calculate_transfer_fee(sell_value)
    net_proceeds = sell_value - commission - stamp_duty - transfer_fee

    return {
        "symbol": symbol,
        "shares": shares,
        "price": open_price,
        "sell_value": sell_value,
        "commission": commission,
        "stamp_duty": stamp_duty,
        "transfer_fee": transfer_fee,
        "net_proceeds": net_proceeds,
    }
