class CachedAwaitable:
    def __init__(self, awaitable):
        self.awaitable = awaitable
        self.result = None

    def __await__(self):
        if self.result is None:
            self.result = yield from self.awaitable.__await__()
        return self.result


def rewaitable(func):
    def wrapper(*args, **kwargs):
        return CachedAwaitable(func(*args, **kwargs))

    return wrapper
