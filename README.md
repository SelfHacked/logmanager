# Log Manager
Manage logging operations.


## Installation

```bash
pip install -e git+git://github.com/SelfHacked/logmanager.git#egg=logmanager
```

## Configuration

Use `DefaultLogManager` or `LogManager` to configure Django application logging. `DefaultLogManager` add loggers for Django modules and an additional logger named `app`.

Example:
Add following code snippet to `settings.py` of the Django Application with following environment variables. 
- `LOG_GROUP`: Name of a CloudWatch group.
- `LOG_LEVEL`: Desired log level for the output filtering.

```python
from logmanager import DefaultLogManager

LOGGING = DefaultLogManager(
    app_name='application-name',
    log_group=os.environ.get('LOG_GROUP'),
    log_level=os.environ.get('LOG_LEVEL', 'DEBUG' if DEBUG else 'INFO'),
    loggers=[],
).config

```

Note: Any custom loggers (ex: application modules) should be included in `loggers`. 

## Logging with default logger

Use `logger` from `logmanager` to log with `app` logger.

```python
from logmanager import logger

logger.info('Test Log Message!')
```

## Logging with custom logger

Use built-in logger to log with module logger (or custom logger). If module logger (or a custom logger) is used, name of the logger should be added to `logger` argument of `DefaultLogManager`.

```python
import logging

logger = logging.getLogger(__name__)
logger.info('Test Log Message!')
```

## Adding Request Logger

Add `LogRequestMiddleware` to log requests. Middleware should be included after Authentication middleware to log user id.

```python
MIDDLEWARE = [
    # middleware
    'logmanager.middleware.LogRequestMiddleware',
    # middleware
]
```