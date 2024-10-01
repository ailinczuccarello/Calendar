from django.shortcuts import render

# Create your views here.
from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('<int:year>/<int:month>/', views.calendar_view, name='calendar-view'),
    path('events/', views.events_json, name='events-json'),
    path('add/', views.add_event, name='add-event'),
    path('edit-event/<int:event_id>/', views.edit_event_view, name='edit-event'),
]