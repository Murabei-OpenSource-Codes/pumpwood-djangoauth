"""Gunicorn hooks for Pumpwood Django Auth singleton lifecycle.

Example gunicorn configuration:

```python
# gunicorn.conf.py
from pumpwood_djangoauth.gunicorn_hooks import post_fork

# gunicorn loads callables listed in this module by name.
```

Or pass the hook on the command line:

```bash
gunicorn core.wsgi:application \
    --preload \
    --config python:pumpwood_djangoauth.gunicorn_hooks
```
"""


def post_fork(server, worker):
    """Initialize singletons inside each worker after fork.

    Args:
        server:
            Gunicorn arbiter instance.
        worker:
            Gunicorn worker instance.
    """
    from pumpwood_djangoauth.config import reset_config_singletons
    reset_config_singletons()
