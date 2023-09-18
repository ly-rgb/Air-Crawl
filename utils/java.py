import threading

import jpype

__vm_lock__ = threading.Lock()


def start_jvm():
    __vm_lock__.acquire()
    try:
        if not jpype.isJVMStarted():
            jpype.startJVM(classpath=['lib/crypto-1.0.jar'])
    except Exception:
        pass
    finally:
        __vm_lock__.release()


def get_jvm():
    start_jvm()
    return jpype
