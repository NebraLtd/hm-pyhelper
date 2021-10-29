from time import sleep
from hm_pyhelper.lock_singleton import LockSingleton, \
    ResourceBusyError, CannotLockError

lock = LockSingleton("some_resource")

try:
    # try to acquire the resource or may raise an exception
    lock.acquire()

    # do some work
    print("Starting work...")
    sleep(5)
    print("Finished work!")

    # release the resource
    lock.release()
except ResourceBusyError:
    print("The resource is busy now.")
except CannotLockError:
    print("Can't lock the resource for some internal issue.")
