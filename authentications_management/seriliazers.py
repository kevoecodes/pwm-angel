from dataclasses import fields

from rest_framework import serializers

from authentications_management.models import NewUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewUser
        fields = ('mobileNo', 'first_name', 'last_name', 'accountNo', 'deviceNo')


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('mobileNo', 'password')
