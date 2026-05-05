from telegram import Bot
from loguru import logger
from config.settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID


class TelegramAlerter:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_TOKEN)
        self.chat_id = TELEGRAM_CHAT_ID

    async def send(self, message: str):
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown',
            )
        except Exception as e:
            logger.error(f'Telegram erro: {e}')

    async def trade_alert(self, symbol: str, direction: str,
                          price: float, sl: float, tp: float, score: float):
        msg = (
            f'*NOVO TRADE — ALLADIN*\n'
            f'Par: `{symbol}`\n'
            f'Direção: *{direction}*\n'
            f'Preço: `{price:.5f}`\n'
            f'Stop Loss: `{sl:.5f}`\n'
            f'Take Profit: `{tp:.5f}`\n'
            f'Score ML: `{score:.2f}`'
        )
        await self.send(msg)

    async def circuit_breaker_alert(self, daily_loss_pct: float):
        msg = (
            f'*CIRCUIT BREAKER ATIVADO*\n'
            f'Perda diária: `{daily_loss_pct:.1%}`\n'
            f'Trading pausado automaticamente.'
        )
        await self.send(msg)

    async def daily_report(self, pnl: float, trades: int,
                           win_rate: float, drawdown: float):
        status = 'POSITIVO' if pnl >= 0 else 'NEGATIVO'
        msg = (
            f'*RELATÓRIO DIÁRIO — {status}*\n'
            f'P&L: `${pnl:.2f}`\n'
            f'Trades: `{trades}`\n'
            f'Win Rate: `{win_rate:.1%}`\n'
            f'Drawdown: `{drawdown:.1%}`'
        )
        await self.send(msg)
