import time
from hm_pyhelper.lock_singleton import LockSingleton, LOCK_ECC

lock = LockSingleton(LOCK_ECC)

print('initial', ', resource:', lock.value(), ', Locked:', lock.locked())

lock.acquire()
print('acquired', ', resource:', lock.value(), ', Locked:', lock.locked())

print('Start working...')
time.sleep(5)
print('Work finished!')

lock.release()
print('released', ', resource:', lock.value(), ', Locked:', lock.locked())
