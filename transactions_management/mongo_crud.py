import uuid
from datetime import datetime

from bson.objectid import ObjectId

from mongo_crud.mongodb import MongoDB


class MongoTransactionsManager(MongoDB):
    def __init__(self):
        super().__init__()

        self.token_id = None
        self.is_purchased = False

    def create(self, data):
        try:
            user = self.users_coll.find_one({"mobileNo": data['mobileNo']})
            self.account = self.account_coll.find_one({"accountNo": user['accountNo']})
            print(user)
            data['at'] = datetime.now()
            data['accountNo'] = user['accountNo']
            data['type'] = data['type']
            print('Hellooo')
            _id = self.transactions_coll.insert_one(data).inserted_id
            print('Adding token')
            self.add_token(user['deviceNo'], data['units'], str(_id))
            print('Added')
            return True
        except Exception as e:
            print('Error', e)
            return False

    def generate_unique_id(self):
        unique_id = str(uuid.uuid4().int)[0:12]
        if self.tokens_coll.find({'token': unique_id}) is not None:
            return unique_id
        return self.generate_unique_id()

    def add_token(self, deviceNo, units, transaction_id):
        print('here token')

        self.token_id = self.tokens_coll.insert_one({
            'deviceNo': deviceNo,
            'units': float(units),
            'token': self.generate_unique_id(),
            'transaction_id': transaction_id,
            'at': datetime.now()
        }).inserted_id
        print('added token')

    def get_token(self, token_id):
        return self.tokens_coll.find_one({'_id': ObjectId(token_id)})

    def depositCash(self, data):
        user = self.users_coll.find_one({"mobileNo": data['mobileNo']})
        account = self.account_coll.find_one({"accountNo": user['accountNo']})
        if account is not None:
            self.create({"mobileNo": data['mobileNo'], 'amount': data['amount'], "type": "Deposit"})
            new_balance = float(account['current_balance']) + float(data['amount'])
            self.account_coll.update_one({"accountNo": user['accountNo']}, {"$set": {
                "current_balance": new_balance
            }})
            self.feedback = f"Deposit successfull to {user['first_name']}"
            return True
        self.feedback = f"Unknown error"
        return None

    def purchaseUnits(self, data):
        user = self.users_coll.find_one({"mobileNo": data['mobileNo']})
        account = self.account_coll.find_one({"accountNo": user['accountNo']})
        cost = self.system_coll.find_one({"data": "cost"})

        if cost is None:
            self.feedback = f"Unknown error"
            return None
        if float(account['current_balance']) <= float(data['amount']):
            self.feedback = f"Insufficient balance"
            return False

        units = float(data['amount']) / float(cost['price'])
        print("The Units", units)

        account['water_units'] = str(round(float(account['water_units']) + units, 3))
        new_balance = float(account['current_balance']) - float(data['amount'])
        self.create({"mobileNo": data['mobileNo'], "amount": data['amount'], "type": "Purchase", 'units': units})
        self.account_coll.update_one({"accountNo": user['accountNo']}, {"$set": {
            'water_units': account['water_units'],
            'current_balance': new_balance
        }}, upsert=False)
        self.is_purchased = True
        return True

    def getTotalIncome(self):
        total = 0
        deposits = self.transactions_coll.find()
        for x in deposits:
            if 'amount' in x and x['type'] == 'Deposit':
                total = total + float(x['amount'])

        return total

    def getUserTransactions(self, data):
        user = self.users_coll.find_one({"mobileNo": data['mobileNo']})
        if user is not None:
            trans = self.transactions_coll.find({"mobileNo": data['mobileNo']})
            feed = []

            for tran in trans:
                feed.append(tran)

            return feed

        return []


class Tariff(MongoDB):
    def __init__(self):
        super().__init__()

    def getTariff(self):
        pass

    def changeTariff(self):
        pass


class MongoPurchaseWater(MongoDB):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.sufficient_balance = False

        self.check = self.transactionCredibility()
        if self.check and self.sufficient_balance:
            self.conducct = self.conductTransaction()

    def transactionCredibility(self):
        try:
            self.user_account = self.account_coll.find_one({"accountNo": self.data['accountNo']})

            if self.user_account is not None:
                the_tariff = self.tariffs_coll.find_one({"tariff_type": self.user_account['tariff_type']})
                self.tariff = the_tariff['cost']
                self.bill = int(self.tariff) * int(self.data['litres'])

                if int(self.user_account['current_balance']) > int(self.bill):
                    self.sufficient_balance = True
                    return True

                return True

            return True

        except:
            return False

    def conductTransaction(self):
        try:
            if self.user_account is not None:
                self.new_balance = int(self.user_account['current_balance']) - int(self.bill)
                self.total_consumes_litres = int(self.user_account['consumed_litres']) + int(self.data['litres'])
                self.total_cash_used = int(self.user_account['cash_used']) + int(self.bill)

                self.account_coll.update_one({"accountNo": self.data['accountNo']}, {"$set":
                    {"current_balance": str(
                        self.new_balance),
                        "cash_used": str(
                            self.total_cash_used),
                        "consumed_litres": str(
                            self.total_consumes_litres)}})

            return True

        except:
            return False

    def feedback(self):
        pass


class MongoGetTransactions(MongoDB):
    def __init__(self):
        super().__init__()

    def getAllTransactions(self):
        all_transactions = self.trasactions_coll.find()
        return all_transactions

    def getUserTransactions(self, query):
        transactions = self.trasactions_coll.find({"acccountNo": query['accountNo']})

        return transactions

    def getTotalTransactions(self):
        all_transactions = self.getAllTransactions()
        total = 0
        for item in all_transactions:
            total = int(total) + int(all_transactions['amount'])

        return total


class MongoUnitsUpdate(MongoDB):
    def __init__(self, data):
        super().__init__()
        self.account = None
        self.data = data
        self.updated = self.updateUnits()

    def updateUnits(self):
        self.account = self.account_coll.find_one({"deviceNo": self.data['deviceNo']})

        if float(self.account['water_units']) > float(self.data['units']):
            used_units = float(self.account['water_units']) - float(self.data['units'])
            self.account['consumed_litres'] = str(float(self.account['consumed_litres']) + float(used_units))

        self.account_coll.update_one({"deviceNo": self.data['deviceNo']}, {"$set":
                                                                               {"water_units": self.data['units'],
                                                                                "consumed_litres": self.account[
                                                                                    'consumed_litres']}})

        return True

    def feedback(self):
        return self.updated
