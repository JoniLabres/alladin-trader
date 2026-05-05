import pandas as pd
import pandas_ta as ta


def calculate_features(df: pd.DataFrame) -> pd.DataFrame:
    # Tendência
    df['ema_20'] = ta.ema(df['close'], 20)
    df['ema_50'] = ta.ema(df['close'], 50)
    df['ema_200'] = ta.ema(df['close'], 200)
    macd = ta.macd(df['close'])
    df['macd'] = macd['MACD_12_26_9']
    df['macd_signal'] = macd['MACDs_12_26_9']
    df['macd_hist'] = macd['MACDh_12_26_9']
    adx = ta.adx(df['high'], df['low'], df['close'])
    df['adx'] = adx['ADX_14']
    df['adx_pos'] = adx['DMP_14']
    df['adx_neg'] = adx['DMN_14']

    # Osciladores
    df['rsi'] = ta.rsi(df['close'], 14)
    stoch = ta.stoch(df['high'], df['low'], df['close'])
    df['stoch_k'] = stoch['STOCHk_14_3_3']
    df['stoch_d'] = stoch['STOCHd_14_3_3']
    df['cci'] = ta.cci(df['high'], df['low'], df['close'], 20)
    df['williams_r'] = ta.willr(df['high'], df['low'], df['close'], 14)
    df['roc'] = ta.roc(df['close'], 10)

    # Volatilidade
    df['atr'] = ta.atr(df['high'], df['low'], df['close'], 14)
    bb = ta.bbands(df['close'], 20)
    df['bb_upper'] = bb['BBU_20_2.0']
    df['bb_lower'] = bb['BBL_20_2.0']
    df['bb_mid'] = bb['BBM_20_2.0']
    df['bb_pct'] = bb['BBP_20_2.0']
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_mid']

    # Volume
    df['obv'] = ta.obv(df['close'], df['tick_volume'])
    df['mfi'] = ta.mfi(df['high'], df['low'], df['close'], df['tick_volume'], 14)

    # Sessão de mercado (feature binária)
    h = df.index.hour
    df['london_session'] = ((h >= 8) & (h < 17)).astype(int)
    df['new_york_session'] = ((h >= 13) & (h < 22)).astype(int)
    df['tokyo_session'] = ((h >= 0) & (h < 9)).astype(int)
    df['overlap_session'] = ((h >= 13) & (h < 17)).astype(int)

    # Retorno futuro — label do modelo (BUY=1 se subir > 3 pips em 5 candles)
    df['future_return'] = df['close'].shift(-5) / df['close'] - 1
    df['label'] = (df['future_return'] > 0.0003).astype(int)

    return df.dropna()
