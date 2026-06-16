from django.urls import path
from . import views

app_name = 'organisations'

urlpatterns = [
    path('', views.organisation_list, name='list'),
]
