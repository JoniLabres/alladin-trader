import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger
from config.pairs import PAIRS, TIMEFRAMES, ACTIVE_TIMEFRAMES


class DataCollector:
    PAIRS = PAIRS
    TIMEFRAMES = TIMEFRAMES

    def connect(self, login, password, server):
        if not mt5.initialize(login=login, password=password, server=server):
            raise ConnectionError(f'MT5 falhou: {mt5.last_error()}')
        logger.info('MT5 conectado com sucesso')

    def disconnect(self):
        mt5.shutdown()
        logger.info('MT5 desconectado')

    def fetch_history(self, symbol, tf_name, days=365):
        tf = self.TIMEFRAMES[tf_name]
        end = datetime.now()
        start = end - timedelta(days=days)
        rates = mt5.copy_rates_range(symbol, tf, start, end)
        if rates is None:
            logger.error(f'Sem dados: {symbol} {tf_name}')
            return None
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        logger.info(f'{symbol} {tf_name}: {len(df)} candles')
        return df

    def fetch_latest(self, symbol, tf_name, count=500):
        tf = self.TIMEFRAMES[tf_name]
        rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
        if rates is None:
            logger.error(f'Sem dados recentes: {symbol} {tf_name}')
            return None
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        return df

    def fetch_all(self, days=365):
        data = {}
        for pair in self.PAIRS:
            data[pair] = {}
            for tf in ACTIVE_TIMEFRAMES:
                data[pair][tf] = self.fetch_history(pair, tf, days)
        return data
