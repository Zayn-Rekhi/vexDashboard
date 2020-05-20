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
    path('matches/', views.matches, name='match'),
    path('skills/', views.skills, name='skill'),
    path('calendar/', views.calendarPage, name='calendar'),
    path('rankings/', views.rankings, name='rankings'),
    path('messaging/', views.messages, name='message'),
    path('team_search/', views.team_search, name='teamSearch'),
    re_path(r'team/(?P<slug>[-\w]+)/', views.teams, name='teams'),
    # The home page
    path('', views.index, name='home'),
]

urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
