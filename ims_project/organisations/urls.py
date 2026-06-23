from django.urls import path
from . import views
urlpatterns = [
    path('', views.org_list, name='org_list'),
    path('create/', views.org_create, name='org_create'),
    path('<int:pk>/', views.org_detail, name='org_detail'),
    path('<int:pk>/edit/', views.org_edit, name='org_edit'),
]
