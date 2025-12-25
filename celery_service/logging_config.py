import os


def setup_separate_logging():
    """Настройка раздельного логирования"""

    log_dir = '/var/log/celery'
    os.makedirs(log_dir, exist_ok=True)

    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '[%(asctime)s] %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
        },
        'handlers': {
            'system_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'detailed',
                'filename': os.path.join(log_dir, 'celery_system.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 3,
                'encoding': 'utf8'
            },
            'tasks_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'standard',
                'filename': os.path.join(log_dir, 'celery_tasks.log'),
                'maxBytes': 10485760,
                'backupCount': 3,
                'encoding': 'utf8'
            },
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'WARNING',
                'formatter': 'detailed',
                'stream': 'ext://sys.stdout'
            },
        },
        'loggers': {
            'celery': {
                'level': 'INFO',
                'handlers': ['system_file', 'console'],
                'propagate': False
            },
            'celery.beat': {
                'level': 'INFO',
                'handlers': ['system_file'],
                'propagate': False
            },
            'celery.worker': {
                'level': 'INFO',
                'handlers': ['system_file'],
                'propagate': False
            },
            'lesson_tasks': {
                'level': 'INFO',
                'handlers': ['tasks_file'],
                'propagate': False
            },
            'py.warnings': {
                'level': 'ERROR',
                'propagate': False
            },
        },
        'root': {
            'level': 'WARNING',
            'handlers': []
        }
    }

    return logging_config


# Создаем конфигурацию
logging_config = setup_separate_logging()