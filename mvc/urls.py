from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^signup/$', views.signup),
    url(r'^signin/$', views.signin),
]