# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.forms.utils import ErrorList
from django.http import HttpResponse
from .forms import LoginForm, SignUpForm
import pymongo

def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None
    if not request.user.is_authenticated:

        if request.method == "POST":

            if form.is_valid():
                username = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password")
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    myclient = pymongo.MongoClient(
                        'mongodb+srv://ZaynRekhi:assimo11!@clustor0-vxk4l.mongodb.net/test?retryWrites=true&w=majority')
                    mydb = myclient["webDB_VEX"]
                    mycolAuthUser = mydb["userInfo"]
                    if mycolAuthUser.find_one({"username":username}):
                        return redirect("/dashboard")
                    else:
                        return redirect("/settings")
                else:    
                    msg = 'Invalid credentials'    
            else:
                msg = 'Error validating the form'    

        return render(request, "accounts/login.html", {"form": form, "msg" : msg})
    else:
        return render(request, 'pages/error-404.html')

def register_user(request):

    msg     = None
    success = False
    if not request.user.is_authenticated:

        if request.method == "POST":
            form = SignUpForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get("username")
                raw_password = form.cleaned_data.get("password1")
                user = authenticate(username=username, password=raw_password)

                msg     = 'User created.'
                success = True
                
                #return redirect("/login/")

            else:
                msg = 'Form is not valid'    
        else:
            form = SignUpForm()

        return render(request, "accounts/register.html", {"form": form, "msg" : msg, "success" : success })
    else:
        return render(request, 'pages/error-404.html')
