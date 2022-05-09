import sys

from mock import MagicMock

def pytest_sessionstart(session):
    sys.modules['jwt'] = MagicMock()
    sys.modules['jwt.utils'] = MagicMock()

