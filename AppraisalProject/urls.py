from django.contrib import admin
from django.urls import path
from .views import *




urlpatterns = [
    path('',Login,name='login'),
    path('home/', Home, name='home'),
    path('submit-activity/', submit_activity, name='submit_activity')
]