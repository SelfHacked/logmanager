"""Configure logging."""
import os
import typing


class LogManager:
    """Configure logging."""

    def __init__(
            self,
            app_name: str,
            log_level: str,
            log_group: typing.Optional[str],
            log_dir: typing.Optional[str],
    ):
        """
        Initialize LogManager.

        Args:
            app_name: Name of the application.
            log_level: Log level for the logging output.
            log_group: CloudWatch log group.
            log_dir: Folder for logging.
        """
        self._app_name = app_name
        self._log_dir = log_dir
        self._log_group = log_group
        self._default_log_level = log_level

        self._config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'default': {
                    'format': '%(levelname)s [%(asctime)s] %(message)s',
                },
                'basic': {
                    'format': (
                        '%(asctime)s %(levelname)s %(processName)s %(name)s '
                        '%(message)s'
                    ),
                },
                'full': {
                    'format': (
                        '%(asctime)s %(levelname)s %(processName)s %(name)s  '
                        '%(filename)s:%(lineno)d %(message)s'
                    ),
                },
                'db': {
                    'format': '[%(asctime)s]\n%(message)s\n',
                },
            },
            'handlers': {},
            'loggers': {},
        }

        self._handlers = {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'basic',
            },
        }
        if self._log_dir:
            self._add_file_handler()

        if self._log_group:
            self._add_cloudwatch_handler()

        self._loggers: typing.Dict[str, dict] = {}

    @property
    def config(self) -> dict:
        """Get logging configuration."""
        config = self._config
        config['handlers'] = self._handlers
        config['loggers'] = self._loggers

        return config

    def add_logger(
            self,
            logger: str,
            level: str = None,
            propagate=False,
    ):
        """
        Add logger with existing handlers.

        Args:
            logger: Name of the logger.
            level: Log Level for the logger.
            propagate: Propagate downstream.
        """
        self._loggers[logger] = {
            'propagate': propagate,
            'handlers': [*self._handlers],
            'level': level or self._default_log_level,
        }

    def _add_file_handler(self, formatter='full'):
        if not os.path.exists(self._log_dir):
            os.makedirs(self._log_dir)

        self._handlers['file'] = {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': formatter,
            'filename': os.path.join(self._log_dir, f'{self._app_name}.log'),
            'when': 'midnight',
        }

    def _add_cloudwatch_handler(self, formatter='full'):
        self._handlers['cloudwatch'] = {
            'class': 'watchtower.CloudWatchLogHandler',
            'formatter': formatter,
            'log_group': self._log_group,
            'stream_name': f'{self._app_name}-{{strftime:%Y-%m-%d}}',
            'use_queues': True,
            'create_log_group': False,
        }


class DefaultLogManager(LogManager):
    """Default log manager to manage django logs."""

    def __init__(
            self,
            app_name: str,
            log_level: str = None,
            log_group: str = None,
            log_dir: str = None,
            loggers: typing.List[str] = None,
    ):
        """
        Initialize LogManager.

        Args:
            app_name: Name of the application.
            log_level: Log level for the logging output.
            log_group: CloudWatch log group.
            log_dir: Folder for logging.
            loggers: Loggers to be added to the logs.
        """
        super().__init__(app_name, log_level, log_group, log_dir)

        # add default loggers
        self._add_loggers([
            # django loggers
            'django.server', 'django.request',
            'django.security.*', 'django.db',
            # celery loggers
            'celery', 'celery.worker', 'celery.app',
            # application loggers
            'app',
        ])

        # add custom loggers
        if loggers:
            self._add_loggers(loggers)

    def _add_loggers(self, loggers: typing.List[str]):
        for logger in loggers:
            self.add_logger(logger)
