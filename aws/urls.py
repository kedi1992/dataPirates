from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from aws import views
from django.conf.urls import url
from aws.views import GetServices
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import re_path
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    # html page urls
    path('', views.index, name="index"),
    path('ec2/', views.ec2, name="result"),
    path('cartInfo/', views.cart_info, name="result"),
    re_path(r'^category/', views.category, name="category"),
    re_path(r'^result/', views.result, name="result"),
    # api urls
    url(r'^aws/getServices', csrf_exempt(GetServices.as_view())),
    url(r'^aws/getOfferCodes', csrf_exempt(views.GetAllOfferCodes.as_view())),
    url(r'^aws/getEc2Instance', csrf_exempt(views.GetEc2Instance.as_view())),

]
