import MetaTrader5 as mt5
from loguru import logger
from config.settings import (
    MAX_RISK_PER_TRADE, MAX_DAILY_LOSS, SIGNAL_THRESHOLD
)
from config.pairs import CORRELATED_PAIRS


class RiskManager:
    def __init__(self):
        self.daily_pnl = 0.0
        self.open_positions: list[dict] = []
        self.trading_active = True

    def get_account_balance(self) -> float:
        info = mt5.account_info()
        return info.balance if info else 0.0

    def calculate_position_size(self, symbol: str, sl_pips: float) -> float:
        balance = self.get_account_balance()
        risk_amount = balance * MAX_RISK_PER_TRADE
        symbol_info = mt5.symbol_info(symbol)
        pip_value = symbol_info.trade_tick_value
        lots = risk_amount / (sl_pips * pip_value)
        min_lot = symbol_info.volume_min
        lots = max(min_lot, round(lots / min_lot) * min_lot)
        return min(lots, 10.0)

    def check_correlation(self, new_symbol: str) -> bool:
        open_syms = [p['symbol'] for p in self.open_positions]
        for corr in CORRELATED_PAIRS.get(new_symbol, []):
            if corr in open_syms:
                logger.warning(f'Correlação detectada: {new_symbol} + {corr}')
                return False
        return True

    def circuit_breaker(self, current_equity: float) -> bool:
        balance = self.get_account_balance()
        if balance == 0:
            return False
        daily_loss = (balance - current_equity) / balance
        if daily_loss >= MAX_DAILY_LOSS:
            self.trading_active = False
            logger.critical(
                f'CIRCUIT BREAKER ATIVADO! Perda diária: {daily_loss:.1%}'
            )
            return True
        return False

    def is_safe_to_trade(self, symbol: str, signal_score: float) -> tuple[bool, str]:
        if not self.trading_active:
            return False, 'Circuit breaker ativo'
        if signal_score < SIGNAL_THRESHOLD:
            return False, f'Score baixo ({signal_score:.2f} < {SIGNAL_THRESHOLD})'
        if len(self.open_positions) >= 4:
            return False, 'Máximo de posições abertas atingido'
        if not self.check_correlation(symbol):
            return False, 'Par correlacionado já aberto'
        return True, 'OK'
