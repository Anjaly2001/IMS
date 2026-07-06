from django.urls import path
from . import views
from .notification_views import notifications

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:pk>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
    path('activity-log/', views.activity_log, name='activity_log'),
    path('profile/', views.profile_view, name='profile'),
    path('password/change/', views.password_change_view, name='password_change'),
    path('notifications/', notifications, name='notifications'),
    path('email-settings/', views.email_settings_view, name='email_settings'),
]
