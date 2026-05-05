import MetaTrader5 as mt5

PAIRS = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'USDCHF']

TIMEFRAMES = {
    'M1':  mt5.TIMEFRAME_M1,
    'M5':  mt5.TIMEFRAME_M5,
    'M15': mt5.TIMEFRAME_M15,
    'H1':  mt5.TIMEFRAME_H1,
    'H4':  mt5.TIMEFRAME_H4,
    'D1':  mt5.TIMEFRAME_D1,
}

ACTIVE_TIMEFRAMES = ['M5', 'M15', 'H1', 'D1']

# Correlações conhecidas — evitar exposição dupla
CORRELATED_PAIRS = {
    'EURUSD': ['GBPUSD', 'AUDUSD'],
    'USDJPY': ['USDCHF'],
}
