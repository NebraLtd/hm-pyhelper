import functools
import threading
from hm_pyhelper.logger import get_logger

LOGGER = get_logger(__name__)

DEFAULT_TIMEOUT = 2.0  # 2 seconds


class LockSingleton(object):
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(LockSingleton, cls).__new__(cls)
        return cls._instance

    def acquire(self, timeout=DEFAULT_TIMEOUT):
        if not self._lock.acquire(blocking=True, timeout=timeout):
            raise ResourceBusyError()

    def release(self):
        self._lock.release()

    def locked(self):
        return self._lock.locked()


class ResourceBusyError(Exception):
    """Raised when the resource is busy"""
    pass


def lock_ecc(timeout=DEFAULT_TIMEOUT, raise_resource_busy_exception=True):
    """
    Returns a decorator that locks the ECC.

    timeout: timeout value. DEFAULT_TIMEOUT = 2 seconds.
    raise_resource_busy_exception: set True to raise exception
                    in case of lock acquire timeout and error.
                    Otherwise just log the error msg
    """

    def decorator_lock_ecc(func):
        lock = LockSingleton()

        @functools.wraps(func)
        def wrapper_lock_ecc(*args, **kwargs):
            try:
                # try to acquire the ECC resource or may raise an exception
                lock.acquire(timeout=timeout)

                try:
                    value = func(*args, **kwargs)
                except Exception as ex:
                    lock.release()
                    raise ex

                # release the resource
                lock.release()

                return value
            except ResourceBusyError as ex:
                LOGGER.error("ECC is busy now.")
                if raise_resource_busy_exception:
                    raise ex
            except Exception as ex:
                raise ex

        return wrapper_lock_ecc

    return decorator_lock_ecc
