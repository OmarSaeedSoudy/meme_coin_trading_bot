
from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('start_trading/', index, name='index'),
    path('', home, name='home'),
]