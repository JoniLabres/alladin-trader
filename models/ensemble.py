import numpy as np
from models.lstm_model import LSTMModel
from models.xgboost_model import XGBoostModel
from sklearn.ensemble import RandomForestClassifier
import joblib
from loguru import logger


class EnsembleModel:
    def __init__(self, lstm: LSTMModel, xgb: XGBoostModel, rf: RandomForestClassifier):
        self.lstm = lstm
        self.xgb = xgb
        self.rf = rf
        # Pesos calibrados por performance histórica de cada modelo
        self.weights = [0.40, 0.35, 0.25]  # LSTM, XGB, RF

    def predict(self, X_seq: np.ndarray, X_flat: np.ndarray,
                sentiment_score: float = 0.0) -> tuple[str, float]:
        p_lstm = float(self.lstm.predict(X_seq)[0])
        p_xgb = float(self.xgb.predict_proba(X_flat)[:, 1])
        p_rf = float(self.rf.predict_proba(X_flat)[:, 1])

        sentiment_boost = sentiment_score * 0.05

        score = (
            self.weights[0] * p_lstm +
            self.weights[1] * p_xgb +
            self.weights[2] * p_rf
        ) + sentiment_boost

        score = max(0.0, min(1.0, score))

        if score > 0.65:
            return 'BUY', score
        if score < 0.35:
            return 'SELL', 1 - score
        return 'HOLD', score

    def save(self, path: str):
        self.lstm.save(path)
        self.xgb.save(path)
        joblib.dump(self.rf, f'{path}/rf_model.pkl')
        logger.info(f'Ensemble salvo em {path}')

    @classmethod
    def load(cls, path: str) -> 'EnsembleModel':
        lstm = LSTMModel()
        lstm.load(path)
        xgb_model = XGBoostModel()
        xgb_model.load(path)
        rf = joblib.load(f'{path}/rf_model.pkl')
        logger.info(f'Ensemble carregado de {path}')
        return cls(lstm, xgb_model, rf)
