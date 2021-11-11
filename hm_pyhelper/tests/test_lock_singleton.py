import unittest
import threading
import pytest
import mock
from time import sleep
from hm_pyhelper.lock_singleton import LockSingleton, ResourceBusyError, \
    lock_ecc


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


class TestLockSingleton(unittest.TestCase):
    def test_lock_singleton_simple(self):
        lock = LockSingleton()

        self.assertFalse(lock.locked())
        lock.acquire()

        # Do some work
        sleep(0.001)

        lock.release()
        self.assertFalse(lock.locked())

    def test_lock_singleton_timeout(self):
        """
        Start a slow running thread and then try to acquire a shared
        lock. Expect the acquire call to throw an exception.
        """

        def slow_task():
            sleep(0.1)
            lock.release()
            return True

        lock = LockSingleton()

        # ECC is going to be occupied by `slow_task`.
        slow_thread = threading.Thread(target=slow_task, daemon=True)
        lock.acquire()
        slow_thread.start()

        self.assertTrue(lock.locked())

        # Try to acquire the ECC that is occupied by `slow_task` currently.
        expected_exception = False
        try:
            lock.acquire(timeout=0.00001)
        except ResourceBusyError:
            expected_exception = True

        self.assertTrue(expected_exception)

    def test_lock_singleton_racing(self):
        def slow_task():
            lock = LockSingleton()

            lock.acquire()
            self.assertTrue(lock.locked())

            # Do some slow work
            print("Starting the slow task...")
            sleep(0.01)
            print("Finished the slow task!")

            lock.release()
            self.assertFalse(lock.locked())

        def fast_task():
            lock = LockSingleton()

            lock.acquire()
            self.assertTrue(lock.locked())

            # Do some slow work
            print("Starting the fast task...")
            sleep(0.001)
            print("Finished the fast task!")

            lock.release()
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
        try:
            fast_thread.join()
            slow_thread.join()
        except Exception as ex:
            print(ex)

    def test_lock_ecc_simple(self):
        @lock_ecc()
        def some_task():
            sleep(0.00001)

        some_task_thread = threading.Thread(target=some_task, daemon=True)
        some_task_thread.start()

        some_task_thread.join()

    def test_lock_ecc_timeout(self):
        @lock_ecc()
        def slow_task():
            sleep(0.01)

        @lock_ecc(timeout=0.001, raise_resource_busy_exception=True)
        def lock_with_timeout():
            pass

        slow_thread = threading.Thread(target=slow_task, daemon=True)
        slow_thread.start()

        expected_exception = False
        try:
            lock_with_timeout()
        except ResourceBusyError:
            expected_exception = True

        self.assertTrue(expected_exception)

    def test_lock_ecc_racing(self):
        @lock_ecc()
        def slow_task():
            # Do some slow work
            print("Starting the slow task...")
            sleep(0.003)
            print("Finished the slow task!")

        @lock_ecc()
        def fast_task():
            # Do some slow work
            print("Starting the fast task...")
            sleep(0.001)
            print("Finished the fast task!")

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

    def test_lock_ecc_forward_exception(self):
        @lock_ecc()
        def faulty_task():
            print("Starting the faulty task...")
            sleep(0.001)
            raise Exception("Intended faulty occurred!")

        expected_exception = False
        try:
            faulty_task()
        except Exception:
            expected_exception = True

        self.assertTrue(expected_exception)
