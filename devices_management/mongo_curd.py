from mongo_crud.mongodb import MongoDB


class MongoDevicesManager(MongoDB):
    def __init__(self):
        super().__init__()
        self.new_units = None

    def isDevice(self, data):
        device = self.account_coll.find_one({'deviceNo': data['deviceNo']})
        if device is not None:
            return True
        return False

    def isBlocked(self, data):
        device = self.account_coll.find_one({'deviceNo': data['deviceNo']})
        if device is not None and device['active'] is not False:
            return False
        return True

    def deduce_token(self, data):
        if 'token' in data and 'deviceNo' in data:
            device = self.tokens_coll.find_one({'deviceNo': data['deviceNo'], 'token': data['token']})
            if device is not None:
                if 'used' in device:
                    if device['used'] is False:
                        self.tokens_coll.update_one({"deviceNo": data['deviceNo'], 'token': data['token']}, {"$set": {
                            "used": True,
                        }})
                        return device['units']
                    return 0.0

                self.tokens_coll.update_one({"deviceNo": data['deviceNo'], 'token': data['token']}, {"$set": {
                    "used": True,
                }})
                return device['units']
        return 0.0

    def deviceUpdate(self, data):
        if 'deviceNo' in data:
            account = self.account_coll.find_one({"deviceNo": data['deviceNo']})
            if account is not None:
                current_units = account['water_units']
                new_units = round((float(current_units) - float(data['units'])), 3)

                consumed_units = float(account['consumed_litres'])
                if float(new_units) < 0:
                    new_units = 0
                else:
                    consumed_units = round((float(account['consumed_litres']) + float(data['units'])), 3)

                self.account_coll.update_one({"deviceNo": data['deviceNo']}, {"$set": {
                    "water_units": new_units,
                    "consumed_litres": consumed_units
                }})

                self.new_units = new_units
                return True

        return None


