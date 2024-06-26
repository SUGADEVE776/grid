from django.urls import path

from access.views import home

urlpatterns = [path("home/", home)]
