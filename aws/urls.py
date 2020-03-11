from django.contrib import admin
from django.urls import path
from aws import views
from django.conf.urls import url
from aws.views import GetServices
from rest_framework.urlpatterns import format_suffix_patterns
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name="index"),
    url(r'^aws/getServices', csrf_exempt(GetServices.as_view())),

]
