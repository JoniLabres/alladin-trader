import MetaTrader5 as mt5
from loguru import logger
from risk.risk_manager import RiskManager

SYSTEM_MAGIC = 202600


class OrderManager:
    def __init__(self, risk_manager: RiskManager):
        self.rm = risk_manager

    def open_trade(self, symbol: str, direction: str,
                   atr: float, signal_score: float) -> int | None:
        safe, reason = self.rm.is_safe_to_trade(symbol, signal_score)
        if not safe:
            logger.info(f'Trade bloqueado [{symbol}]: {reason}')
            return None

        tick = mt5.symbol_info_tick(symbol)
        price = tick.ask if direction == 'BUY' else tick.bid

        sl_points = atr * 1.5
        sl = price - sl_points if direction == 'BUY' else price + sl_points
        tp = price + sl_points * 2 if direction == 'BUY' else price - sl_points * 2

        lots = self.rm.calculate_position_size(symbol, sl_points * 10)

        request = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': symbol,
            'volume': lots,
            'type': mt5.ORDER_TYPE_BUY if direction == 'BUY' else mt5.ORDER_TYPE_SELL,
            'price': price,
            'sl': round(sl, 5),
            'tp': round(tp, 5),
            'deviation': 10,
            'magic': SYSTEM_MAGIC,
            'comment': f'Alladin|{direction}|score:{signal_score:.2f}',
            'type_time': mt5.ORDER_TIME_GTC,
        }

        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            logger.success(
                f'Ordem aberta: {direction} {symbol} {lots} lotes @ {price:.5f} '
                f'SL={sl:.5f} TP={tp:.5f}'
            )
            self.rm.open_positions.append({
                'symbol': symbol,
                'ticket': result.order,
                'direction': direction,
            })
            return result.order
        else:
            logger.error(f'Ordem falhou [{symbol}]: {result.comment}')
            return None

    def close_position(self, ticket: int) -> bool:
        positions = mt5.positions_get(ticket=ticket)
        if not positions:
            return False
        pos = positions[0]
        direction = mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY
        tick = mt5.symbol_info_tick(pos.symbol)
        price = tick.bid if pos.type == 0 else tick.ask

        request = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': pos.symbol,
            'volume': pos.volume,
            'type': direction,
            'position': ticket,
            'price': price,
            'deviation': 10,
            'magic': SYSTEM_MAGIC,
            'comment': 'Alladin|close',
        }
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            self.rm.open_positions = [
                p for p in self.rm.open_positions if p['ticket'] != ticket
            ]
            logger.info(f'Posição {ticket} fechada.')
            return True
        logger.error(f'Falha ao fechar {ticket}: {result.comment}')
        return False
