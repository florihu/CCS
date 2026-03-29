from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('',                         views.dashboard,       name='dashboard'),
    path('login/',                   views.login_view,      name='login'),
    path('logout/',                  views.logout_view,     name='logout'),
    path('invite/',                  views.invite_send,     name='invite_send'),
    path('invite/<uuid:token>/',     views.invite_register, name='invite_register'),
    path('profile/',                 views.profile,         name='profile'),
]
