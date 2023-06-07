import re

from django.shortcuts import render, redirect, HttpResponse
from bson import json_util
import json
from django.contrib import messages
from django.contrib.auth.models import User
from rest_framework.views import APIView

from accounts_management.mongo_crud import MongoAccountsManager
from system_management.mongo_crud import MongoSystemManager
from transactions_management.mongo_crud import MongoTransactionsManager
from users_managements.mongo_crud import MongoUsersManager


def clear(request):
    for message in messages.get_messages(request):
        pass


def Dashboard_View(request):
    if request.user.is_authenticated:

        if request.user.is_staff:
            users_manager = MongoUsersManager()
            totalUsers = users_manager.TotalMembers()
            totalIncome = MongoTransactionsManager().getTotalIncome()
            cost = MongoSystemManager().getPrice()

            return render(request, 'index.html', {"totalDeposits": 0, "cost": cost, "totalIncome": totalIncome, "totalUsers": totalUsers, "consumedLitres": 0})

        ##For users dashboard
        accounts_manager = MongoAccountsManager()
        users_manager = MongoUsersManager()
        trans_manager = MongoTransactionsManager()
        the_user = users_manager.getUserData({"mobileNo": request.user.username})
        account = accounts_manager.getAccountData({"accountNo": the_user['accountNo']})
        trans = trans_manager.getUserTransactions({"mobileNo": request.user.username})
        return render(request, 'user_dashboard.html', {"user": the_user, "account": account, 'trans': trans})

    return redirect('/login-page')



def viewMembers(request):
    if request.user.is_authenticated and request.user.is_staff:
        data = dict(request.POST.dict())
        print(data)
        users_manager = MongoUsersManager()
        if request.method == "POST":
            del data['csrfmiddlewaretoken']
            users = users_manager.getAllUsers(data)

        elif request.method == "GET":
            users = users_manager.getAllUsers()

        return render(request, 'users.html', {"users": users})

    return redirect('/login-page')


def viewUser(request, id):
    if request.user.is_authenticated and request.user.is_staff:
        print("the method", request.method)
        accounts_manager = MongoAccountsManager()
        users_manager = MongoUsersManager()
        trans_manager = MongoTransactionsManager()
        if request.method == 'GET':
            the_user = users_manager.getUserData({"id": id})
            account = accounts_manager.getAccountData({"accountNo": the_user['accountNo']})
            trans = trans_manager.getUserTransactions({"mobileNo": the_user['mobileNo']})
            return render(request, 'profile.html', {"user": the_user, "id": id, "account": account, 'trans': trans})
        if request.method == "POST":
            data = dict(request.POST.dict())
            del data['csrfmiddlewaretoken']
            print(data)
            if 'change' in data:
                if data['change'] == 'block':
                    accounts_manager.blockAccount(data)

                else:
                    print('\n \n Enable')
                    accounts_manager.enableAccount(data)

            return redirect('/user-profile/' + id)

    return redirect('/login-page')


def editUser(request, id=None):
    if request.user.is_authenticated:
        if request.method == "GET":
            if id is not None:
                if MongoUsersManager().isUser({"id": id}):
                    user = json.loads(json_util.dumps(MongoUsersManager().getUserData({"id": id})))
                    return render(request, 'registerUser.html', {"user_data": user, "id": id, "edit_mode": True})

            else:
                if MongoUsersManager().isUser({"mobileNo": str(request.user.username)}):
                    user = json.loads(json_util.dumps(MongoUsersManager().getUserData({"mobileNo": request.user.username})))
                    return render(request, 'registerUser.html', {"user_data": user, "edit_mode": True})

        if request.method == 'POST':
            data = dict(request.POST.dict())
            del data['csrfmiddlewaretoken']
            print(data)
            users_manager = MongoUsersManager()
            is_user = False

            if id is not None:
                is_user = users_manager.isUser({"id": id})

            else:
                is_user = users_manager.isUser({"mobileNo": str(request.user.username)})

            if is_user:
                update = users_manager.updateUserCred(data)

                if users_manager.is_updated:
                    user = User.objects.get(username=data['prev_mobileNo'])
                    user.username = data['mobileNo']
                    user.first_name = data['first_name']
                    user.last_name = data['last_name']
                    user.email = data['email']
                    user.save()

                    if id is not None:
                        return redirect('/user-profile/' + id)
                    else:
                        return redirect('/')
                messages.info(request, 'Error during update')
                return  redirect('/edit-user/' + id)
    return redirect('/login-page')


def editUserPassword(request, id=None):
    if request.user.is_authenticated:
        if request.method == 'GET':
            users_manager = MongoUsersManager()

            if id is not None:
                user = users_manager.getUserData({"id": id})
                return render(request, 'changePassword.html', {"the_user": user, "id": id})

            else:
                user = users_manager.getUserData({"mobileNo": str(request.user.username)})
                return render(request, 'changePassword.html', {"the_user": user})

        if request.method == 'POST':
                data = dict(request.POST.dict())
                print(data)
                del data['csrfmiddlewaretoken']
                print(data)

                user = User.objects.get(username=data['mobileNo'])

                if data['password1'] == data['password2']:
                    user.set_password(data['password2'])
                    user.save()
                    if id is not None:
                        return redirect('/user-profile/' + id)

                    else:
                        return redirect('/')
                clear(request)
                messages.info(request, 'Passwords do not match')
                if id is not None:
                    return redirect('/change-password/' + str(id))
                else:
                    return redirect('/change-password')

    return redirect('/login-page')

def deleteUser(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == "POST":
            data = dict(request.POST.dict())
            if MongoUsersManager().isUser({"mobileNo": data['mobileNo']}):
                delete = MongoUsersManager().deleteUser(data)
                user = User.objects.get(username=data['mobileNo'])
                user.delete()

                return redirect('/view-members')
    return redirect('/login-page')


def DepositCash(request, id):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == "GET":
                users_manager = MongoUsersManager()
                accounts_manager = MongoAccountsManager()
                the_user = users_manager.getUserData({"id": id})
                account = accounts_manager.getAccountData({"accountNo": the_user['accountNo']})

                return render(request, 'deposit-page.html', {"user": the_user, "id": id, "account": account})
        if request.method == "POST":
            if request.user.is_authenticated and request.user.is_staff:
                data = dict(request.POST.dict())
                print(data)

                deposit_manager = MongoTransactionsManager()
                deposit_request = deposit_manager.depositCash(data)

                if deposit_request:
                    return redirect('/user-profile/' + id)

                clear(request)
                messages.info(request, deposit_manager.feedback)
                return redirect('/deposit-cash/' + id)

    return redirect('/login-page')


def purchaseUnits(request):
        if request.user.is_authenticated:
            if request.method == 'GET':
                users_manager = MongoUsersManager()
                accounts_manager = MongoAccountsManager()
                the_user = users_manager.getUserData({"mobileNo": request.user.username})
                account = accounts_manager.getAccountData({"accountNo": the_user['accountNo']})

                return render(request, 'purchase-page.html', {"user": the_user, "account": account})

            if request.method == 'POST':
                data = dict(request.POST.dict())
                purchase_manager = MongoTransactionsManager()
                purchase_request = purchase_manager.purchaseUnits(data)

                if purchase_manager.is_purchased:
                    return redirect('/token/' + str(purchase_manager.token_id))

                clear(messages)
                messages.info(request, purchase_manager.feedback)
                return redirect('/purchase-units')

        return redirect('/login-page')


def purchaseUnits_Page(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == "POST":
            if request.user.is_authenticated:
                data = dict(request.POST.dict())

                users_manager = MongoUsersManager()
                accounts_manager = MongoAccountsManager()
                the_user = users_manager.getUserData(data)
                account = accounts_manager.getAccountData({"accountNo": the_user['accountNo']})

                return render(request, 'purchase-page.html', {"user": the_user, "account": account})

    return redirect('/login-page')


def changePrice(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == "POST":
            data = dict(request.POST.dict())
            MongoSystemManager().changePrice(data)
            return redirect('/')
        clear(request)
        price = MongoSystemManager().getPrice()
        return render(request, 'changePrice.html', {"current_price": price})

    return redirect('/login-page')


def viewToken(request, pk):
    if request.user.is_authenticated:
        if request.method == "GET":
            token = MongoTransactionsManager().get_token(pk)
            token['token'] = re.sub(r"(?<=\d)(?=(\d{3})+(?!\d))", "-", token['token'])
            if token is not None:
                return render(request, 'token-view.html', {'token': token})
            return redirect('/')

    return redirect('/login-page')

