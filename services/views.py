from django.shortcuts import render

# Create your views here.

from .models import AuthUser


def create_user(request, daata):
    AuthUser.create_user("Daniel", "theSuperPassword")
