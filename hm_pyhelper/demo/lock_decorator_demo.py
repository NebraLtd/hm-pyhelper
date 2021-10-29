import time
from hm_pyhelper.lock_singleton import ecc_lock


@ecc_lock
def worker_process(name):
    print(name)
    print('Start working...')
    time.sleep(5)
    print('Work finished!')


worker_process('worker 1')
