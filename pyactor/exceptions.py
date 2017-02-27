'''
PyActor exceptions.
'''


class TimeoutError(Exception):
    def __init__(self, meth='Not specified'):
        self.method = meth

    def __str__(self):
        return ("Timeout triggered: %r" % self.method)


class AlreadyExistsError(Exception):
    def __init__(self, value='Not specified'):
        self.value = value

    def __str__(self):
        return ("Repeated ID: %r" % self.value)


class NotFoundError(Exception):
    def __init__(self, value='Not specified'):
        self.value = value

    def __str__(self):
        return ("Not found ID: %r" % self.value)


class HostDownError(Exception):
    def __str__(self):
        return ("The host is down.")


class HostError(Exception):
    def __init__(self, value='Not specified'):
        self.value = value

    def __str__(self):
        return ("Host ERROR: %r" % self.value)


class FutureError(Exception):
    def __init__(self, value='Not specified'):
        self.value = value

    def __str__(self):
        return ("Future ERROR: %r" % self.value)


class IntervalError(Exception):
    def __init__(self, value='Not specified'):
        self.value = value

    def __str__(self):
        return ("Interval ERROR: %r" % self.value)
