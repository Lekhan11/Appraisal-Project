from django.contrib import admin
from django.urls import path
from .views import *
from django.urls import include




urlpatterns = [
    path('', Login, name='login'),
    path('home/<str:content>/', Home, name='home'),
    path('home/', Home, name='home'),
    path('submit-activity/', submit_activity, name='submit_activity'),
    path('dashboard/', Home, {'content': 'dashboard'}, name='dashboard'),
    path('activity/', Home, {'content': 'activity'}, name='activity'),
    path("__reload__/", include("django_browser_reload.urls")),
    path('home/proofs/<str:filename>/', serve_pdf, name='serve_pdf'),
    path('dashboard/proofs/<str:filename>/', serve_pdf, name='serve_pdf'),
    
]