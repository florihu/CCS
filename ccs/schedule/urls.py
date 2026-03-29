from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
    path('',            views.timeslot_list,   name='list'),
    path('new/',        views.timeslot_create, name='create'),
    path('<int:pk>/',   views.timeslot_detail, name='detail'),
]
