from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('moderation/', views.moderation_panel, name='moderation'),
    path('api/pending-count/', views.get_pending_count, name='pending_count'),
    path('ajax/login/', views.ajax_login, name='ajax_login'),
    path('ajax/register/', views.ajax_register, name='ajax_register'),
    path('profile/data/', views.profile_data, name='profile_data'),
    path('', views.map_view, name='map'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='incidents/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('add/', views.add_incident, name='add_incident'),
    path('anonymous/', views.anonymous_report, name='anonymous_report'),
]
