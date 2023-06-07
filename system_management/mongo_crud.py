from mongo_crud.mongodb import MongoDB


class MongoLOGG(MongoDB):
    def __init__(self):
        super().__init__()

    def logg(self):
        pass


class MongoSystemManager(MongoDB):
    def changePrice(self, data):
        cost = self.system_coll.find_one({"data": "cost"})
        if cost is not None:
            self.system_coll.update_one({"data": "cost"}, {"$set": {"price": float(data['amount'])}})
            return True
        else:
            self.system_coll.insert_one({'data': 'cost', 'price': float(data['amount'])})

        return False
    def getPrice(self):
        cost = self.system_coll.find_one({"data": "cost"})
        if cost is not None:
            return float(cost['price'])

        return 0.0
