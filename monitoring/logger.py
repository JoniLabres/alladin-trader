import sys
from loguru import logger


def setup_logger(log_dir: str = 'logs'):
    logger.remove()
    logger.add(sys.stdout, level='INFO',
               format='<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}')
    logger.add(
        f'{log_dir}/trading_{{time:YYYY-MM-DD}}.log',
        rotation='1 day',
        retention='30 days',
        level='DEBUG',
        encoding='utf-8',
    )
    logger.add(
        f'{log_dir}/errors.log',
        rotation='1 week',
        retention='90 days',
        level='ERROR',
        encoding='utf-8',
    )
    return logger
