from sawtooth_sdk.messaging.stream import Stream

from .utils import Singleton


class Stream(Stream, metaclass=Singleton):
    pass
