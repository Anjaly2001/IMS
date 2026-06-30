from django.urls import path
from . import views
from .notification_views import notifications
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('activity-log/', views.activity_log, name='activity_log'),
    path('profile/', views.profile_view, name='profile'),
    path('notifications/', notifications, name='notifications'),
]
