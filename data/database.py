import pandas as pd
from sqlalchemy import create_engine, text
from loguru import logger
from config.settings import DB_URL


class Database:
    def __init__(self):
        self.engine = create_engine(DB_URL)

    def save_ohlcv(self, df: pd.DataFrame, symbol: str, timeframe: str):
        table = f'ohlcv_{symbol.lower()}_{timeframe.lower()}'
        try:
            df.to_sql(table, self.engine, if_exists='append', index=True)
            logger.info(f'Salvo {len(df)} candles em {table}')
        except Exception as e:
            logger.error(f'Erro ao salvar {table}: {e}')

    def load_ohlcv(self, symbol: str, timeframe: str, days: int = 365) -> pd.DataFrame:
        table = f'ohlcv_{symbol.lower()}_{timeframe.lower()}'
        query = f"SELECT * FROM {table} WHERE time >= NOW() - INTERVAL '{days} days' ORDER BY time"
        try:
            df = pd.read_sql(query, self.engine, index_col='time', parse_dates=['time'])
            return df
        except Exception as e:
            logger.error(f'Erro ao carregar {table}: {e}')
            return pd.DataFrame()

    def save_trade(self, trade: dict):
        df = pd.DataFrame([trade])
        try:
            df.to_sql('trades', self.engine, if_exists='append', index=False)
        except Exception as e:
            logger.error(f'Erro ao salvar trade: {e}')
