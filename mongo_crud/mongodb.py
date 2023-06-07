from pymongo import MongoClient


class MongoDB:
    def __init__(self) -> None:
        self.client = MongoClient('mongodb://127.0.0.1:27017/')
        db = 'PWM_ANGEL'
        self.DB_NAME = db
        self.users_coll = self.client[db]['Users']
        self.account_coll = self.client[db]['Accounts']
        self.deposits_coll = self.client[db]['Deposits']
        self.devices_coll = self.client[db]['Devices']
        self.transactions_coll = self.client[db]['Transactions']
        self.tokens_coll = self.client[db]['Tokens']
        self.tariffs_coll = self.client[db]['Tariff']
        self.regAcc_coll = self.client[db]['RegAccounts']
        self.loggs_coll = self.client[db]['LOGGS']
        self.system_coll = self.client[db]['System']