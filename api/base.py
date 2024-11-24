def once(func):
    initialized = False
    def wrapper(*args, **kwargs):
        nonlocal initialized
        if not initialized:
            func(*args, **kwargs)
            initialized = True
    return wrapper

class Singleton(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Singleton, cls).__new__(cls)
        return cls.instance