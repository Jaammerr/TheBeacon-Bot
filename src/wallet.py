from eth_account import Account
from eth_account.hdaccount import Mnemonic
from eth_account.messages import encode_defunct
from web3 import Web3
from web3.types import Nonce

from models import LoginData
from loader import config

mnemo = Mnemonic("english")
Account.enable_unaudited_hdwallet_features()


class Wallet(Web3, Account):
    def __init__(self, mnemonic: str = None):
        super().__init__(Web3.HTTPProvider(str(config.eth_rpc)))
        self.mnemonic = mnemo.generate() if not mnemonic else mnemonic
        self.keypair = (
            self.eth.account.from_mnemonic(self.mnemonic)
            if len(self.mnemonic.split()) in (12, 24)
            else self.eth.account.from_key(mnemonic)
        )

    @property
    def address(self) -> str:
        return self.keypair.address

    @property
    def transactions_count(self) -> Nonce:
        return self.eth.get_transaction_count(self.keypair.address)

    @property
    def get_sign_message(self) -> str:
        message = "This is used to prove you own your account"
        return message

    def sign_login_message(self) -> LoginData:
        encoded_message = encode_defunct(text=self.get_sign_message)
        signed_message = self.keypair.sign_message(encoded_message)
        return LoginData(
            message=self.get_sign_message, signed_message=signed_message.signature.hex()
        )
