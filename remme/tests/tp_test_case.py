import os
import unittest

from sawtooth_processor_test.mock_validator import MockValidator

from remme.settings import TP_HANDLERS


class TransactionProcessorTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        url = os.getenv('TEST_BIND', 'tcp://127.0.0.1:4004')

        cls.validator = MockValidator()

        cls.validator.listen(url)

        for item in TP_HANDLERS:
            if not cls.validator.register_processor():
                raise Exception('Failed to register processor')

        cls.factory = None

    @classmethod
    def tearDownClass(cls):
        try:
            cls.validator.close()
        except AttributeError:
            pass