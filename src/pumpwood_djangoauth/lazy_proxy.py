"""Lazy proxy helper for deferred singleton initialization.

Use ``LazyProxy`` to defer creation of network clients until first use.
This keeps gunicorn master preload from opening shared sockets before
worker fork.
"""
import threading

_UNSET = object()
_INIT_LOCK = threading.Lock()


class LazyProxy:
    """Wrap a factory and instantiate its result on first access.

    Args:
        factory (callable):
            Callable that returns the object to proxy.
    """

    def __init__(self, factory):
        """Initialize proxy with a factory callable."""
        object.__setattr__(self, '_factory', factory)
        object.__setattr__(self, '_instance', _UNSET)

    def _get_instance(self):
        """Return cached instance or build it via factory."""
        instance = object.__getattribute__(self, '_instance')
        if instance is not _UNSET:
            return instance
        with _INIT_LOCK:
            instance = object.__getattribute__(self, '_instance')
            if instance is not _UNSET:
                return instance
            factory = object.__getattribute__(self, '_factory')
            instance = factory()
            object.__setattr__(self, '_instance', instance)
        return instance

    def get_instance(self):
        """Return the wrapped instance, building it when needed.

        Returns:
            object:
                Instance returned by the factory, which may be ``None``.
        """
        return self._get_instance()

    def reset(self):
        """Drop cached instance and close it when supported."""
        with _INIT_LOCK:
            instance = object.__getattribute__(self, '_instance')
            if instance is not _UNSET and instance is not None:
                close_method = getattr(instance, 'close', None)
                if callable(close_method):
                    close_method()
            object.__setattr__(self, '_instance', _UNSET)

    def __getstate__(self):
        """Return picklable proxy state."""
        return {
            '_factory': object.__getattribute__(self, '_factory'),
            '_instance': object.__getattribute__(self, '_instance'),
        }

    def __setstate__(self, state):
        """Restore proxy state after unpickling."""
        object.__setattr__(self, '_factory', state['_factory'])
        object.__setattr__(self, '_instance', state['_instance'])

    def __getattr__(self, name):
        """Forward attribute access to the wrapped instance."""
        instance = self._get_instance()
        if instance is None:
            msg = 'LazyProxy singleton is not configured'
            raise AttributeError(msg)
        return getattr(instance, name)

    def __call__(self, *args, **kwargs):
        """Forward call to the wrapped instance when callable."""
        instance = self._get_instance()
        if instance is None:
            msg = 'LazyProxy singleton is not configured'
            raise TypeError(msg)
        return instance(*args, **kwargs)

    def __repr__(self):
        """Return proxy representation."""
        instance = object.__getattribute__(self, '_instance')
        if instance is _UNSET:
            return '<LazyProxy (uninitialized)>'
        if instance is None:
            return '<LazyProxy (not configured)>'
        return repr(instance)
