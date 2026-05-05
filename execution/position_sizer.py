import MetaTrader5 as mt5
from config.settings import MAX_RISK_PER_TRADE


def kelly_criterion(win_rate: float, avg_win: float, avg_loss: float) -> float:
    """Fração de Kelly para dimensionamento de posição."""
    if avg_loss == 0:
        return 0.0
    b = avg_win / avg_loss
    q = 1 - win_rate
    kelly = (b * win_rate - q) / b
    return max(0.0, min(kelly * 0.5, MAX_RISK_PER_TRADE * 2))


def fixed_fractional(balance: float, risk_pct: float,
                     sl_pips: float, symbol: str) -> float:
    """Dimensionamento por fração fixa do capital."""
    risk_amount = balance * risk_pct
    info = mt5.symbol_info(symbol)
    pip_value = info.trade_tick_value
    lots = risk_amount / (sl_pips * pip_value)
    min_lot = info.volume_min
    lots = max(min_lot, round(lots / min_lot) * min_lot)
    return min(lots, 10.0)
