from django.shortcuts import render, redirect
from django.http import QueryDict
from bson import json_util
import json

from django.contrib.auth import authenticate, login, logout

from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework.authtoken.models import Token
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from authentications_management.mongo_crud import MongoCreateUser
from authentications_management.seriliazers import LoginSerializer, UserSerializer
from users_managements.mongo_crud import MongoCheck, MongoGetUserData


class RegisterUser(APIView):
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        user_dict = request.data
        user = QueryDict('', mutable=True)
        user.update(user_dict)
        serializer = UserSerializer(data=user)
        if serializer.is_valid():
            if User.objects.filter(username=user["mobileNo"]).exists() or User.objects.filter(
                    first_name=user["full_name"]).exists():
                feed = {
                    "iscreated": False,
                    "destail": "user already exists"
                }
                return Response(feed)
            else:
                print(f'Creating {user["username"]}')
                # serializer.save()
                create_user = MongoCreateUser(user)
                if create_user.isCreated():
                    new = User()
                    new.username = user['username']
                    new.email = user['email']
                    new.first_name = user['full_name']
                    # new.email = user['username']
                    new.set_password(user['password'])
                    new.save()

                    the_user = authenticate(username=user['username'], password=user['password'])
                    if user is not None:
                        token = Token.objects.get_or_create(user=the_user)

                        user_data = json.loads(json_util.dumps(MongoGetUserData(user_dict).getData()))
                        feed = {
                            "token": f'Token {str(token[0])}',
                            "user": user_data
                        }
                        return Response(feed)

                    else:
                        return Response(False)

                return Response('Error')

        return Response(serializer.errors)


class LoginUser(APIView):
    # authentication_classes = (SessionAuthAll,)
    def post(self, request, *args, **kwargs):
        user_dict = request.data
        user = QueryDict('', mutable=True)
        user.update(user_dict)
        login_form = LoginSerializer(data=user)
        if login_form.is_valid():
            the_user = authenticate(username=user['mobileNo'], password=user['password'])
            if the_user is not None:
                token = Token.objects.get_or_create(user=the_user)
                the_data = MongoGetUserData(user_dict)
                user_data = json.loads(json_util.dumps(the_data.getData()))
                account = json.loads(json_util.dumps(the_data.getAccountData()))
                feed = {
                    "token": f'Token {str(token[0])}',
                    "user": user_data,
                    "account": account
                }
                return Response(feed)

        return Response(login_form.errors)


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("/")
            else:
                messages.error(request, "Invalid username or password.")
                return redirect('login-page')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login-page')


##Admin Authentications and creatiom functions

def register_user(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == "POST":
            data = {}
            data = dict(request.POST.dict())
            del data['csrfmiddlewaretoken']

            form = UserSerializer(data=request.POST)

            if form.is_valid():
                if not MongoCheck({"mobileNo": data['mobileNo']}).user_exists():
                    new_user = MongoCreateUser(data)
                    print(new_user.isCreated())

                    if new_user.isCreated():
                        new = User()
                        new.username = data['mobileNo']
                        new.email = data['email']
                        new.first_name = data['first_name']
                        new.last_name = data['last_name']
                        new.set_password(data['mobileNo'])
                        new.save()

                        messages.info(request, "Registration successful.")
                        the_user = new_user.details()

                        return redirect('/view-members')

                messages.info(request, 'Something went wrong')
                return redirect('register-user-page')

            messages.info(request, form.errors)
            return redirect('register-user-page')

    return redirect('login-page')


def goToregister(request):
    return render(request, 'registerUser.html')


def Logout(request):
    # logout()
    logout(request)
    return redirect('login-page')


def LoginPage(request):
    return render(request, 'login.html')


