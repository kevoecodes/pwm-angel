from django.db import models
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "first_name", "last_name")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class NewUser(models.Model):
    mobileNo = models.CharField(max_length=100)
    accountNo = models.CharField(max_length=256, default=None)
    first_name = models.CharField(max_length=100, default=None)
    last_name = models.CharField(max_length=100, default=None)
    email = models.CharField(max_length=100, default=None)
    deviceNo = models.CharField(max_length=100, default=None)

    def __str__(self):
        return self.mobileNo

