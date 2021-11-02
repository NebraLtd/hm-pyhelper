import functools
import os
import posix_ipc
from hm_pyhelper.logger import get_logger

LOGGER = get_logger(__name__)

LOCK_ECC = 'LOCK_ECC'
DEFAULT_TIMEOUT = 2.0  # 2 seconds


class InterprocessLock(object):
    _prefix = "LockSingleton."
    _mode = 0o644

    def __init__(self, name, available_resources=1, reset=False):
        """
        name: uniquely identifies the `LockSingleton` across processes
        available_resources: the count of the available resources
        reset: set True to reset the available_resources

        The available_resources of a `InterprocessLock` get reset on every
        restart of the system or docker container. It's tested in Ubuntu
        20.04 desktop and diagnostics container in a Hotspot.
        Resetting the available_resources by passing the `reset=True` should be
        used with a caution and it can be used in a very specific scenarios
        such as in the development environment. It's designed for facilitating
        the development. It's not recommended to be used in production.
        """
        self._name = self._prefix + name
        # so it doesn't interfere with our semaphore mode
        old_umask = os.umask(0)
        try:
            self._sem = posix_ipc.Semaphore(self._name,
                                            mode=self._mode,
                                            flags=posix_ipc.O_CREAT,
                                            initial_value=available_resources)

            if reset:
                """ Some hack to set the Semaphore's read-only value
https://github.com/rwarren/SystemEvent/blob/87422d850a3f0a4631528f5fbee23904170c0703/SystemEvent/__init__.py#L47
https://github.com/GEANT/CAT/blob/b53bc299c7e822c7abd8deb1ee1a9e44f3f465da/ansible/ManagedSP/templates/daemon/fr_restart.py#L46
https://github.com/south-coast-science/scs_host_rpi/blob/50b6277b4281b043d7c8f340371183faea4c5b8c/src/scs_host/sync/binary_semaphore.py#L54
                """
                while available_resources > self._sem.value:
                    self._sem.release()
                while available_resources < self._sem.value:
                    self._sem.acquire()

        finally:
            os.umask(old_umask)

    def acquire(self, timeout=DEFAULT_TIMEOUT):
        """Acquire the lock
        """
        try:
            self._sem.acquire(timeout)
        except posix_ipc.BusyError:
            raise ResourceBusyError()
        except posix_ipc.Error:  # Catch all IPC Errors except BusyError
            raise CannotLockError()

    def release(self):
        """Release the lock
        """
        self._sem.release()

    def locked(self):
        return self.value() == 0

    def value(self):
        return self._sem.value


class ResourceBusyError(posix_ipc.Error):
    """
    Raised when a call times out
    """

    def __init__(self, *args, **kwargs):
        pass


class CannotLockError(posix_ipc.Error):
    """
    Raised when can not lock the resource due to the permission issue,
    wrong IPC object or whatever internal issue.
    """

    def __init__(self, *args, **kwargs):
        pass


def ecc_lock(timeout=DEFAULT_TIMEOUT, raise_exception=False):
    """
    Returns an ECC LOCK decorator.

    timeout: timeout value. DEFAULT_TIMEOUT = 2 seconds.
    raise_exception: set True to raise exception in case of timeout and error.
                    Otherwise just log the error msg
    """

    def decorator_ecc_lock(func):
        lock = InterprocessLock(LOCK_ECC)

        @functools.wraps(func)
        def wrapper_ecc_lock(*args, **kwargs):
            try:
                # try to acquire the ECC resource or may raise an exception
                lock.acquire(timeout=timeout)

                value = func(*args, **kwargs)

                # release the resource
                lock.release()

                return value
            except ResourceBusyError as ex:
                LOGGER.error("ECC is busy now.")
                if raise_exception:
                    raise ex
            except CannotLockError as ex:
                LOGGER.error("Can't lock the ECC for some internal issue.")
                if raise_exception:
                    raise ex

        return wrapper_ecc_lock

    return decorator_ecc_lock
