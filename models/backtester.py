import pandas as pd
import vectorbt as vbt
from sklearn.model_selection import TimeSeriesSplit
from loguru import logger


def walk_forward_validation(df: pd.DataFrame, model, n_splits: int = 5) -> list[dict]:
    tscv = TimeSeriesSplit(n_splits=n_splits)
    results = []

    for fold, (train_idx, test_idx) in enumerate(tscv.split(df)):
        train = df.iloc[train_idx]
        test = df.iloc[test_idx]

        model.fit(train)
        signals = model.predict(test)

        portfolio = vbt.Portfolio.from_signals(
            test['close'],
            entries=signals == 'BUY',
            exits=signals == 'SELL',
            sl_stop=0.02,
            tp_stop=0.04,
            freq='5min',
        )

        metrics = {
            'fold': fold,
            'sharpe': portfolio.sharpe_ratio(),
            'max_drawdown': portfolio.max_drawdown(),
            'win_rate': portfolio.win_rate(),
            'profit_factor': portfolio.profit_factor(),
            'total_return': portfolio.total_return(),
        }
        results.append(metrics)

        logger.info(
            f'Fold {fold}: Sharpe={metrics["sharpe"]:.2f} '
            f'DD={metrics["max_drawdown"]:.1%} '
            f'WR={metrics["win_rate"]:.1%}'
        )

    return results


def check_production_ready(results: list[dict]) -> bool:
    avg_sharpe = sum(r['sharpe'] for r in results) / len(results)
    avg_dd = sum(r['max_drawdown'] for r in results) / len(results)
    avg_wr = sum(r['win_rate'] for r in results) / len(results)

    logger.info(f'Médias — Sharpe: {avg_sharpe:.2f} | DD: {avg_dd:.1%} | WR: {avg_wr:.1%}')

    return avg_sharpe > 1.0 and avg_dd < 0.20 and avg_wr > 0.48
