from transformers import pipeline
from loguru import logger
from data.news_feed import fetch_news

CURRENCY_KEYWORDS = {
    'USD': ['dollar', 'fed', 'federal reserve', 'us economy'],
    'EUR': ['euro', 'ecb', 'european central bank', 'eurozone'],
    'GBP': ['pound', 'sterling', 'bank of england', 'boe'],
    'JPY': ['yen', 'boj', 'bank of japan'],
    'XAU': ['gold', 'xau', 'precious metals'],
}


class SentimentAnalyzer:
    def __init__(self):
        logger.info('Carregando FinBERT (~400MB no primeiro uso)...')
        self.nlp = pipeline(
            'text-classification',
            model='ProsusAI/finbert',
            return_all_scores=True,
        )
        logger.info('FinBERT carregado.')

    def score(self, text: str) -> float:
        result = self.nlp(text[:512])[0]
        scores = {r['label']: r['score'] for r in result}
        return scores.get('positive', 0) - scores.get('negative', 0)

    def currency_sentiment(self) -> dict[str, float]:
        news = fetch_news()
        out: dict[str, list[float]] = {c: [] for c in CURRENCY_KEYWORDS}
        for art in news:
            text = (art['title'] + ' ' + art['summary']).lower()
            for currency, kws in CURRENCY_KEYWORDS.items():
                if any(kw in text for kw in kws):
                    out[currency].append(self.score(art['title']))
        return {c: (sum(v) / len(v) if v else 0.0) for c, v in out.items()}
