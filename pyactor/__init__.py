"""
PyActor: Python Actorlibrary
"""

__all__ = ['version_info', 'version']

#: Version information ``(major, minor, revision)``.
version_info = (1, 4, 0)
#: Version string ``'major.minor.revision'``.
version = '.'.join(map(str, version_info))
