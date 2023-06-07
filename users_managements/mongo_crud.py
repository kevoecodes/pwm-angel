from bson import json_util, objectid
import json
from datetime import datetime
from mongo_crud.mongodb import MongoDB


class MongoUsersManager(MongoDB):
    def __init__(self) -> None:
        super().__init__()
        self.is_updated = False

    def isUser(self, data):
        user = None
        if 'id' in data:
            user = self.users_coll.find_one({"_id": objectid.ObjectId(str(data['id']))})
        if "mobileNo" in data:
            user = self.users_coll.find_one({"mobileNo": data['mobileNo']})

        if user is not None:
            return True
        return False

    def createUser(self, data):
        try:
            data['created_at'] = datetime.now()
            data['online'] = False

            print(data)

            self.users_coll.insert_one(data)
            return True
        except:
            return False

    def getUserData(self, data):
        user = None
        if 'mobileNo' in data:
            user = self.users_coll.find_one({"mobileNo": data['mobileNo']})
        elif 'id' in data:
            user = self.users_coll.find_one({"_id": objectid.ObjectId(str(data['id']))})
        return user

    def getAllUsers(self, data=None):
        the_members = []
        if data == None:
            members = self.users_coll.find()

        elif data is not None:
            if 'mobileNo' in data:
                members = self.users_coll.find({"mobileNo": data['mobileNo']})
                if members.collection.count_documents({"mobileNo": data['mobileNo']}) < 1:
                    members = self.users_coll.find({"deviceNo": data['mobileNo']})

        for i in members:
            the_members.append({
                "created_at": i["created_at"],
                "mobileNo": i['mobileNo'],
                "accountNo": i['accountNo'],
                "full_name": f"{i['first_name']} {i['last_name']}",
                "deviceNo": i['deviceNo'],
                "id": i['_id']

            })

        return the_members

    def deleteUser(self, data):
        if 'id' in data:
            self.users_coll.delete_one({"_id": objectid.ObjectId(str(data['id']))})

            return True
        elif 'mobileNo' in data:
            self.users_coll.delete_one({'mobileNo': data['mobileNo']})

        return False

    def updateUserCred(self, data):

        self.users_coll.update_one({"mobileNo": data['prev_mobileNo']}, {"$set": {
            "mobileNo": data['mobileNo'],
            "email": data['email'],
            "first_name": data['first_name'],
            "last_name": data['last_name'],
            "nidaNo": data['nidaNo'],
            "city": data['city']
        }})
        self.is_updated = True

        return True

    def TotalMembers(self):
        members = self.getAllUsers()
        total = len(members)
        return total


class OnlineUpdate(MongoDB):
    def __init__(self, status, accountNo):
        super().__init__()
        self.status = status
        self.accountNo = accountNo
        self.update()

    def update(self):
        self.users_coll.update_one({"accountNo": self.accountNo}, {"$set": {"online_status": self.status}}, upsert=True)


class MongoCheck(MongoDB):
    def __init__(self, data):
        super().__init__()
        self.data = data

    def user_exists(self):
        self.user = self.users_coll.find_one({"mobileNo": self.data['mobileNo']})

        if self.user is not None:
            return True

        return False

    def isOnline(self):
        user = self.users_coll.find_one({"accountNo": self.data['accountNo']})
        if user['online'] == True:
            return True

        return False


class MongoGetUserData(MongoDB):
    def __init__(self, query):
        super().__init__()
        self.query = query

    def getData(self):
        self.user = self.users_coll.find_one({"mobileNo": self.query['mobileNo']})
        return self.user

    def getAccountData(self):
        account = self.account_coll.find_one({"accountNo": self.user['accountNo']})

        print("The Account", json.loads(json_util.dumps(account)))
        return account

    def changeUserCred(self, data):
        self.users_coll.update_one({"mobileNo": data['mobileNo']}, {"$set": data})


class MongoUpdateUserCred(MongoDB):
    def __init__(self, data):
        print(data)
        self.data = data

        self.ismember = self.check()

        if self.ismember:
            self.isupdated = self.update()

    def check(self):
        self.user = self.users_coll.find_one({"mobileNo": self.data['mobileNo']})

        if self.user is not None:
            return True

        return False

    def update(self):
        self.users_coll.update_one({"mobileNo": self.data['mobileNo']}, {"$set": self.data})
        return True

    def feedback(self):
        if self.ismember and self.isupdated:
            return True
        return False


class MongoGetAllUsers(MongoDB):
    def __init__(self):
        super().__init__()
        self.pledges = []
        self.members = []
        # self.getAllUsers()
        # self.pledge_coll = self.client['CHURCH']['pledges']

    def getUser(self, data):
        the_members = self.users_coll.find(data)

        for i in the_members:
            self.members.append({
                "created_at": i["created_at"],
                "mobileNo": i['mobileNo'],
                "accountNo": i['accountNo'],
                "full_name": f"{i['first_name']} {i['last_name']}",
                "deviceNo": i['deviceNo']
            })

        print(self.members)

        return self.members

    def getAllUsers(self):
        members = self.users_coll.find()

        for i in members:
            self.members.append({
                "created_at": i["created_at"],
                "mobileNo": i['mobileNo'],
                "accountNo": i['accountNo'],
                "full_name": f"{i['first_name']} {i['last_name']}",
                "deviceNo": i['deviceNo']

            })

        return self.members

    def TotalMembers(self):
        self.getAllUsers()
        self.total = len(self.members)
        print(self.total)
        return self.total


class MongoUpdateUserCred(MongoDB):
    def __init__(self, data):
        super().__init__()
        self.data = data

        self.isupdated = self.update()

    def update(self):
        self.users_coll.update_one({"mobileNo": self.data['mobileNo']}, {"$set": self.data})
        return True

    def isUpdated(self):
        if self.isupdated:
            return True
        return False


class DeleteMember(MongoDB):
    def __init__(self, data):
        super().__init__()
        self.data = data

        self.isdeleted = self.delete()

    def delete(self):
        try:
            self.users_coll.delete_one({"mobileNo": self.data['mobileNo']})
            return True
        except:
            return False

    def isDeleted(self):
        if self.isdeleted:
            return True
        return False

    def feedback(self):
        if self.isdeleted:
            return "Member Deleted"
        return "Something went wrong"

