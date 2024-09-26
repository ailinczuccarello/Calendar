from django.shortcuts import render

# Create your views here.
from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendar_view, name='calendar-view-default'),
    path('<int:year>/<int:month>/', views.calendar_view, name='calendar-view'),
    path('events/', views.events_json, name='events-json'),
    path('add/', views.add_event, name='add-event'),
]