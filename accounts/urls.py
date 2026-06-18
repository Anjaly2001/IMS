from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('roles-permissions/', views.roles_permissions, name='roles_permissions'),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_upsert, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_upsert, name='user_edit'),
]


