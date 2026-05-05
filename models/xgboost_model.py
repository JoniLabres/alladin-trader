import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from loguru import logger
import joblib


class XGBoostModel:
    def __init__(self):
        self.model = xgb.XGBClassifier(
            n_estimators=500,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            use_label_encoder=False,
            eval_metric='logloss',
            random_state=42,
        )

    def train(self, X: np.ndarray, y: np.ndarray):
        X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.2, shuffle=False)
        self.model.fit(
            X_tr, y_tr,
            eval_set=[(X_val, y_val)],
            early_stopping_rounds=30,
            verbose=False,
        )
        logger.info(f'XGBoost treinado — best iteration: {self.model.best_iteration}')

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)

    def save(self, path: str):
        joblib.dump(self.model, f'{path}/xgb_model.pkl')

    def load(self, path: str):
        self.model = joblib.load(f'{path}/xgb_model.pkl')
