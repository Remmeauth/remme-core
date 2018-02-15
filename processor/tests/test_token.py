from protobuf_to_dict import protobuf_to_dict

from processor.protos.token_pb2 import Transfer
from processor.tests.test_helper import HelperTestCase
from processor.token.token_handler import TokenHandler, METHOD_TRANSFER


class TokenTest(HelperTestCase):
    @classmethod
    def setUpClass(cls):
        account_signer1 = cls.get_new_signer()
        cls.token_handler = TokenHandler()
        super().setUpClass(cls.token_handler.get_factory(account_signer1))
        cls.account_address1 = cls.token_handler.make_address(account_signer1)
        account_signer2 = cls.get_new_signer()
        cls.account_address2 = cls.token_handler.make_address(account_signer2)

    def test_transfer(self):
        transfer = Transfer()
        transfer.address_to = self.account_address2
        transfer.amount = 200
        self.send_transaction(METHOD_TRANSFER, protobuf_to_dict(transfer),[self.account_address1, self.account_address2])
        self.expect_ok()
