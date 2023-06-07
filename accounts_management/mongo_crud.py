from mongo_crud.mongodb import MongoDB


class MongoAccountsManager(MongoDB):
    def isAccount(self, data):
        if "mobileNo" in data:
            acc = self.account_coll.find_one({"mobileNo": data['mobileNo']})
        elif "accountNo" in data:
            acc = self.account_coll.find_one({"accountNo": data['accountNo']})

        if acc is not None:
            return True

        return False

    def createAccount(self, data):
        account_data = {}

        account_data['accountNo'] = data['accountNo']
        account_data['deviceNo'] = data['deviceNo']
        account_data['active'] = True
        account_data['current_balance'] = 0
        account_data['water_units'] = 0
        account_data['consumed_litres'] = 0
        account_data['total_deposits'] = 0
        account_data['cash_used'] = 0
        self.account_coll.insert_one(account_data)

        return True

    def isActive(self, data):
        user_account = self.account_coll.find_one({"accountNo": data['accountNo']})
        if user_account['active'] == True:
            return True

        return False

    def getAccountData(self, data):
        if "mobileNo" in data:
            account = self.account_coll.find_one({"mobileNo": data['mobileNo']})
        elif "accountNo" in data:
            account = self.account_coll.find_one({"accountNo": data['accountNo']})

        # print("The Account", json.loads(json_util.dumps(account)))
        return account

    def blockAccount(self, data):
        self.account_coll.update_one({"accountNo": data['accountNo']}, {'$set': {"active": False}})

    def enableAccount(self, data):
        self.account_coll.update_one({"accountNo": data['accountNo']}, {"$set": {"active": True}})



