from django.urls import path
from . import views

app_name = 'wiki'

urlpatterns = [
    path('',                    views.wiki_list,         name='list'),
    path('<int:pk>/delete/',    views.wiki_entry_delete, name='delete'),
]
