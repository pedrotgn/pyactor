'''
PyActor exceptions.
'''


class TimeoutError(Exception):
    """Wait time expired."""
    def __init__(self, meth='Not specified'):
        self.method = meth

    def __str__(self):
        return ("Timeout triggered: %r" % self.method)


class AlreadyExistsError(Exception):
    """Actor ID repeated."""
    def __init__(self, value='Not specified'):
        self.value = value

    def __str__(self):
        return ("Repeated ID: %r" % self.value)


class NotFoundError(Exception):
    """Actor not found in Host."""
    def __init__(self, value='Not specified'):
        self.value = value

    def __str__(self):
        return ("Not found ID: %r" % self.value)


class HostDownError(Exception):
    """The Host is down."""
    def __str__(self):
        return ("The host is down.")


class HostError(Exception):
    """Some problem with the Host."""
    def __init__(self, value='Not specified'):
        self.value = value

    def __str__(self):
        return ("Host ERROR: %r" % self.value)


class FutureError(Exception):
    """Some problem with the Future."""
    def __init__(self, value='Not specified'):
        self.value = value

    def __str__(self):
        return ("Future ERROR: %r" % self.value)


class IntervalError(Exception):
    """Some problem with the interval."""
    def __init__(self, value='Not specified'):
        self.value = value

    def __str__(self):
        return ("Interval ERROR: %r" % self.value)
