import unittest
import threading
import pytest
import mock
from time import sleep
from hm_pyhelper.interprocess_lock import ecc_lock, InterprocessLock, \
    ResourceBusyError, LOCK_ECC


# https://gist.github.com/sbrugman/59b3535ebcd5aa0e2598293cfa58b6ab
@pytest.fixture(autouse=True, scope="function")
def error_on_raise_in_thread():
    """
    Replaces Thread with a a wrapper to record any exceptions and
    re-raise them after test execution. In case multiple threads
    raise exceptions only one will be raised.
    """
    last_exception = None

    class ThreadWrapper(threading.Thread):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def run(self):
            try:
                super().run()
            except BaseException as e:
                nonlocal last_exception
                last_exception = e

    with mock.patch('threading.Thread', ThreadWrapper):
        yield
        if last_exception:
            raise last_exception


class TestInterprocessLock(unittest.TestCase):
    def test_interprocess_lock_basic(self):
        lock = InterprocessLock('test', available_resources=1, reset=True)

        self.assertFalse(lock.locked())
        lock.acquire()
        self.assertTrue(lock.locked())

        # Do some work
        sleep(0.001)

        lock.release()
        self.assertFalse(lock.locked())

    def test_interprocess_lock_timeout(self):
        """
        Start a slow running thread and then try to acquire a shared
        lock. Expect the acquire call to throw an exception.
        """
        lock = InterprocessLock('test', available_resources=1, reset=True)

        def slow_task():
            sleep(0.01)
            # lock.release()
            return True

        slow_thread = threading.Thread(target=slow_task, daemon=True)

        lock.acquire()
        slow_thread.start()

        expected_exception = False
        try:
            lock.acquire(timeout=0.00001)
        except ResourceBusyError:
            expected_exception = True

        self.assertTrue(expected_exception)

    def test_interprocess_lock_racing(self):
        def slow_task():
            lock = InterprocessLock('racing')

            lock.acquire()
            self.assertTrue(lock.locked())

            # Do some slow work
            print("Starting the slow task...")
            sleep(0.003)
            print("Finished the slow task!")

            lock.release()
            self.assertFalse(lock.locked())

        def fast_task():
            lock = InterprocessLock('racing')

            lock.acquire()
            self.assertTrue(lock.locked())

            # Do some slow work
            print("Starting the fast task...")
            sleep(0.001)
            print("Finished the fast task!")

            lock.release()
            self.assertFalse(lock.locked())

        lock = InterprocessLock('racing', available_resources=1, reset=True)

        slow_thread = threading.Thread(target=slow_task, daemon=True)
        fast_thread = threading.Thread(target=fast_task, daemon=True)

        # Ensure there is no lock before starting the work
        self.assertFalse(lock.locked())

        # Start work
        print("\n")
        print("Initiated the slow task.")
        slow_thread.start()
        print("Initiated the fast task.")
        fast_thread.start()

        # Wait to finish
        fast_thread.join()
        slow_thread.join()

        # Ensure there is no lock after finishing the work
        self.assertFalse(lock.locked())

    def test_ecc_lock_basic(self):
        @ecc_lock()
        def some_task():
            sleep(0.00001)

        lock = InterprocessLock(LOCK_ECC, available_resources=1, reset=True)
        self.assertFalse(lock.locked())

        some_task_thread = threading.Thread(target=some_task, daemon=True)
        some_task_thread.start()
        self.assertTrue(lock.locked())

        some_task_thread.join()
        self.assertFalse(lock.locked())

    def test_ecc_lock_timeout(self):
        @ecc_lock()
        def slow_task():
            sleep(0.1)

        @ecc_lock(timeout=0.01, raise_exception=True)
        def lock_with_timeout():
            pass

        lock = InterprocessLock(LOCK_ECC, available_resources=1, reset=True)
        self.assertFalse(lock.locked())

        slow_thread = threading.Thread(target=slow_task, daemon=True)
        slow_thread.start()

        expected_exception = False
        try:
            lock_with_timeout()
        except ResourceBusyError:
            expected_exception = True

        self.assertTrue(expected_exception)

    def test_ecc_lock_racing(self):
        @ecc_lock()
        def slow_task():
            # Do some slow work
            print("Starting the slow task...")
            sleep(0.003)
            print("Finished the slow task!")

        @ecc_lock()
        def fast_task():
            # Do some slow work
            print("Starting the fast task...")
            sleep(0.001)
            print("Finished the fast task!")

        lock = InterprocessLock(LOCK_ECC, available_resources=1, reset=True)
        self.assertFalse(lock.locked())

        slow_thread = threading.Thread(target=slow_task, daemon=True)
        fast_thread = threading.Thread(target=fast_task, daemon=True)

        # Start work
        print("\n")
        print("Initiated the slow task.")
        slow_thread.start()
        print("Initiated the fast task.")
        fast_thread.start()

        # Wait to finish
        fast_thread.join()
        slow_thread.join()

        # Ensure there is no lock after finishing the work
        self.assertFalse(lock.locked())
