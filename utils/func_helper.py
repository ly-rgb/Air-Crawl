from functools import wraps


def func_retry(retry: int = 0):
    def decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            count = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if count >= retry:
                        raise e
                    count += 1
        return wrapped_function
    return decorator
