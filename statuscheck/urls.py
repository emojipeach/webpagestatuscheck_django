"""Defines the URL patterns for statuscheck app."""

from django.urls import path

from . import views

app_name = 'statuscheck'
urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    path('result', views.result, name='result')
]