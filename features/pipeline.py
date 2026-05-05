import pandas as pd
from sklearn.preprocessing import StandardScaler
from features.technical import calculate_features
from loguru import logger


class FeaturePipeline:
    def __init__(self):
        self.scalers: dict[str, StandardScaler] = {}

    def transform(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        df = calculate_features(df.copy())
        feature_cols = [c for c in df.columns if c not in ('label', 'future_return')]
        if symbol not in self.scalers:
            self.scalers[symbol] = StandardScaler()
            df[feature_cols] = self.scalers[symbol].fit_transform(df[feature_cols])
        else:
            df[feature_cols] = self.scalers[symbol].transform(df[feature_cols])
        logger.debug(f'{symbol}: {len(feature_cols)} features geradas')
        return df

    def fit(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        df = calculate_features(df.copy())
        feature_cols = [c for c in df.columns if c not in ('label', 'future_return')]
        self.scalers[symbol] = StandardScaler()
        df[feature_cols] = self.scalers[symbol].fit_transform(df[feature_cols])
        return df
