import asyncio
import schedule
import time
import MetaTrader5 as mt5
from loguru import logger

from monitoring.logger import setup_logger
from config.settings import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER
from data.collector import DataCollector
from features.pipeline import FeaturePipeline
from models.ensemble import EnsembleModel
from execution.order_manager import OrderManager
from risk.risk_manager import RiskManager
from monitoring.telegram_bot import TelegramAlerter
from data.news_feed import is_high_impact_window

setup_logger()


async def main_loop(collector: DataCollector, pipeline: FeaturePipeline,
                    model: EnsembleModel, order_mgr: OrderManager,
                    risk_mgr: RiskManager, alerter: TelegramAlerter):

    if is_high_impact_window():
        logger.warning('Evento macro detectado — trading pausado neste ciclo.')
        return

    for symbol in collector.PAIRS:
        try:
            df = collector.fetch_latest(symbol, 'M5', count=500)
            if df is None or len(df) < 200:
                continue

            df = pipeline.transform(df, symbol)

            feature_cols = [c for c in df.columns
                            if c not in ('label', 'future_return')]
            X_flat = df[feature_cols].values[-1:].reshape(1, -1)

            lstm_seq_len = 60
            X_seq = df[feature_cols].values[-lstm_seq_len:].reshape(
                1, lstm_seq_len, len(feature_cols)
            )

            signal, score = model.predict(X_seq, X_flat)
            logger.info(f'{symbol}: {signal} | score={score:.3f}')

            if signal in ('BUY', 'SELL'):
                atr = float(df['atr'].iloc[-1])
                ticket = order_mgr.open_trade(symbol, signal, atr, score)
                if ticket:
                    await alerter.trade_alert(
                        symbol, signal,
                        df['close'].iloc[-1],
                        atr * 1.5, atr * 3.0, score,
                    )

            equity = mt5.account_info().equity
            if risk_mgr.circuit_breaker(equity):
                await alerter.circuit_breaker_alert(
                    (risk_mgr.get_account_balance() - equity)
                    / risk_mgr.get_account_balance()
                )

        except Exception as e:
            logger.error(f'Erro no loop [{symbol}]: {e}')


def run_loop(collector, pipeline, model, order_mgr, risk_mgr, alerter):
    asyncio.run(main_loop(collector, pipeline, model, order_mgr, risk_mgr, alerter))


if __name__ == '__main__':
    collector = DataCollector()
    collector.connect(MT5_LOGIN, MT5_PASSWORD, MT5_SERVER)

    pipeline = FeaturePipeline()
    model = EnsembleModel.load('models/saved')
    risk_mgr = RiskManager()
    order_mgr = OrderManager(risk_mgr)
    alerter = TelegramAlerter()

    schedule.every(5).minutes.do(
        run_loop, collector, pipeline, model, order_mgr, risk_mgr, alerter
    )

    logger.info('Alladin Trader iniciado. Aguardando sinais...')
    while True:
        schedule.run_pending()
        time.sleep(10)
