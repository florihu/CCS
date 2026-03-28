from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('invite/<uuid:token>/', views.invite_register, name='invite_register'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Timeslots
    path('schedule/', views.timeslot_list, name='timeslot_list'),
    path('schedule/new/', views.timeslot_create, name='timeslot_create'),
    path('schedule/<int:pk>/', views.timeslot_detail, name='timeslot_detail'),

    # Announcements
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/new/', views.announcement_create, name='announcement_create'),

    # Wiki
    path('wiki/', views.wiki_list, name='wiki_list'),
    path('wiki/<int:pk>/delete/', views.wiki_entry_delete, name='wiki_entry_delete'),

    # Tasks (Admin + CCT only)
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/new/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/status/', views.task_status_update, name='task_status_update'),

    # Invite
    path('invite/', views.invite_send, name='invite_send'),

    # Profile
    path('profile/', views.profile, name='profile'),
]
