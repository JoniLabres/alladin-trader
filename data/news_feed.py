import feedparser
import requests
from datetime import datetime
from loguru import logger

FEEDS = [
    'https://feeds.reuters.com/reuters/businessNews',
    'https://www.investing.com/rss/news_25.rss',
]

HIGH_IMPACT_EVENTS = ['NFP', 'CPI', 'FOMC', 'GDP', 'PMI', 'interest rate']


def fetch_news(max_per_feed: int = 20) -> list[dict]:
    articles = []
    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_per_feed]:
                articles.append({
                    'title': entry.title,
                    'summary': getattr(entry, 'summary', ''),
                    'published': getattr(entry, 'published', ''),
                    'source': url,
                })
        except Exception as e:
            logger.warning(f'Feed falhou ({url}): {e}')
    return articles


def is_high_impact_window() -> bool:
    """Retorna True se estamos dentro de 30 min de um evento de alto impacto."""
    now = datetime.utcnow()
    # Integre com API de calendário econômico para produção
    return False
