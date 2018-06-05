import os
import unittest
from unittest import mock
from contextlib import suppress

from sawtooth_processor_test.mock_validator import MockValidator

from remme.__main__ import TP_HANDLERS


class RemmeMockValidator(MockValidator):

    def wait_for_ready(self):
        pass


class TransactionProcessorTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        url = os.getenv('TEST_BIND', 'tcp://127.0.0.1:4004')

        cls.validator = RemmeMockValidator()

        cls.validator.listen(url)

        for item in TP_HANDLERS:
            if not cls.validator.register_processor():
                raise Exception('Failed to register processor')

        cls.factory = None

        cls._zmq_patcher = mock.patch('remme.shared.basic_client.Stream',
                                      return_value=cls.validator)
        cls._zmq_patcher_obj = cls._zmq_patcher.start()

    @classmethod
    def tearDownClass(cls):
        with suppress(AttributeError):
            cls.validator.close()
        cls._zmq_patcher.stop()
