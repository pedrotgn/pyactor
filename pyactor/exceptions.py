"""
PyActor exceptions.
"""


class PyActorTimeoutError(Exception):
    """Wait time expired."""

    def __init__(self, method='Not specified'):
        self.method = method

    def __str__(self):
        return f"Timeout triggered: {self.method!r}"


class AlreadyExistsError(Exception):
    """Actor ID repeated."""

    def __init__(self, value='Not specified'):
        self.value = value

    def __str__(self):
        return f"Repeated ID: {self.value!r}"


class NotFoundError(Exception):
    """Actor not found in Host."""

    def __init__(self, value='Not specified'):
        self.value = value

    def __str__(self):
        return f"Not found ID: {self.value!r}"


class HostDownError(Exception):
    """The Host is down."""

    def __str__(self):
        return "The host is down."


class HostError(Exception):
    """Some problem with the Host."""

    def __init__(self, value='Not specified'):
        self.value = value

    def __str__(self):
        return f"Host ERROR: {self.value!r}"


class FutureError(Exception):
    """Some problem with the Future."""

    def __init__(self, value='Not specified'):
        self.value = value

    def __str__(self):
        return f"Future ERROR: {self.value!r}"


class IntervalError(Exception):
    """Some problem with the interval."""

    def __init__(self, value='Not specified'):
        self.value = value

    def __str__(self):
        return f"Interval ERROR: {self.value!r}"
