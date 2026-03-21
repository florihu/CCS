from django.urls import path
from . import views

# here all the urls to the different views are stored
urlpatterns = [ path('', views.home, name='home'),
]   