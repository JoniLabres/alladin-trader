import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau


class LSTMModel:
    def __init__(self, seq_len: int = 60, n_features: int = 80):
        self.seq_len = seq_len
        self.n_features = n_features
        self.model = self._build()

    def _build(self) -> Sequential:
        m = Sequential([
            LSTM(128, return_sequences=True,
                 input_shape=(self.seq_len, self.n_features)),
            BatchNormalization(),
            Dropout(0.2),
            LSTM(64, return_sequences=False),
            BatchNormalization(),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dense(1, activation='sigmoid'),
        ])
        m.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
        return m

    def prepare_sequences(self, X: np.ndarray) -> np.ndarray:
        seqs = []
        for i in range(self.seq_len, len(X)):
            seqs.append(X[i - self.seq_len:i])
        return np.array(seqs)

    def train(self, X_train, y_train, X_val, y_val):
        callbacks = [
            EarlyStopping(patience=10, restore_best_weights=True),
            ReduceLROnPlateau(factor=0.5, patience=5),
        ]
        return self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=100, batch_size=32,
            callbacks=callbacks, verbose=1,
        )

    def predict(self, X_seq: np.ndarray) -> np.ndarray:
        return self.model.predict(X_seq, verbose=0)

    def save(self, path: str):
        self.model.save(f'{path}/lstm_model.keras')

    def load(self, path: str):
        self.model = load_model(f'{path}/lstm_model.keras')
