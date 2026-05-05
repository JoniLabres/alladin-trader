# Preencha com suas credenciais da BlackBull Markets
MT5_LOGIN = 123456789
MT5_PASSWORD = 'sua_senha'
MT5_SERVER = 'BlackBull-Live'

# Gestão de risco
MAX_RISK_PER_TRADE = 0.02   # 2% por trade
MAX_DAILY_LOSS = 0.05       # 5% do capital por dia
MAX_DRAWDOWN = 0.15         # 15% máximo mensal
SIGNAL_THRESHOLD = 0.65     # Score mínimo para entrar
MIN_RR = 2.0                # Risco:Retorno mínimo

# Database
DB_URL = 'postgresql://user:pass@localhost:5432/trading'
REDIS_URL = 'redis://localhost:6379/0'

# Telegram
TELEGRAM_TOKEN = 'seu_token_bot'
TELEGRAM_CHAT_ID = 'seu_chat_id'
