"""Portfolio: cash, positions, and equity tracking."""
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional


@dataclass
class Position:
    symbol: str
    shares: int
    entry_price: float
    entry_date: date
    buy_value: float         # entry_price * shares
    buy_commission: float
    buy_transfer_fee: float
    total_cost: float        # all-in cost basis

    @property
    def market_value(self) -> float:
        return self.shares * self.entry_price


class Portfolio:
    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.equity_history: List[tuple] = []  # (date, equity, cash, position_value)
        self.trade_log: List[dict] = []
        self._daily_cash_used: Dict[date, float] = {}

    @property
    def position_value(self) -> float:
        return sum(p.market_value for p in self.positions.values())

    @property
    def equity(self) -> float:
        return self.cash + self.position_value

    def can_allocate(self, target_date: date, max_fraction: float) -> float:
        """Return cash available for new buys on this date."""
        already_used = self._daily_cash_used.get(target_date, 0.0)
        max_alloc = self.equity * max_fraction
        return max(0.0, max_alloc - already_used)

    def add_position(self, symbol: str, shares: int, price: float,
                     trade_date: date, commission: float, transfer_fee: float):
        """Record a buy fill."""
        buy_value = shares * price
        total_cost = buy_value + commission + transfer_fee

        pos = Position(
            symbol=symbol,
            shares=shares,
            entry_price=price,
            entry_date=trade_date,
            buy_value=buy_value,
            buy_commission=commission,
            buy_transfer_fee=transfer_fee,
            total_cost=total_cost,
        )
        self.positions[symbol] = pos
        self.cash -= total_cost

        # track daily allocation
        used = self._daily_cash_used.get(trade_date, 0.0)
        self._daily_cash_used[trade_date] = used + total_cost

    def remove_position(self, symbol: str, sell_price: float, trade_date: date,
                        commission: float, stamp_duty: float, transfer_fee: float):
        """Sell a position and record the trade."""
        pos = self.positions.pop(symbol)
        sell_value = pos.shares * sell_price
        net_proceeds = sell_value - commission - stamp_duty - transfer_fee

        self.cash += net_proceeds

        pnl = net_proceeds - pos.total_cost
        ret = (net_proceeds / pos.total_cost - 1) * 100 if pos.total_cost > 0 else 0

        self.trade_log.append({
            "buy_date": pos.entry_date,
            "sell_date": trade_date,
            "code": symbol,
            "shares": pos.shares,
            "buy_price": pos.entry_price,
            "sell_price": sell_price,
            "buy_value": pos.buy_value,
            "sell_value": sell_value,
            "buy_commission": pos.buy_commission,
            "buy_transfer_fee": pos.buy_transfer_fee,
            "sell_commission": commission,
            "stamp_duty": stamp_duty,
            "sell_transfer_fee": transfer_fee,
            "total_cost": pos.total_cost,
            "net_proceeds": net_proceeds,
            "pnl": pnl,
            "return_pct": ret,
        })

    def record_daily(self, dt: date):
        """Record daily equity snapshot."""
        self.equity_history.append((dt, self.equity, self.cash, self.position_value))

    def get_positions_for_sale(self, dt: date) -> List[Position]:
        """Get positions bought on the previous trading day."""
        return [p for p in self.positions.values() if p.entry_date != dt]
