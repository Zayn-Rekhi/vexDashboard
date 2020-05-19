# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path, include
from django.conf.urls import url
from django.conf.urls.static import static
from app import views
from django.conf import settings

urlpatterns = [
    # Matches any html file 
    path('settings/', views.settings, name='home'),
    re_path(r'team/(?P<slug>[-\w]+)/', views.teams, name='teams'),
    re_path(r'^.*\.html', views.pages, name='pages'),
    # The home page
    path('', views.index, name='home'),
]

urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
