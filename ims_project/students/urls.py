from django.urls import path
from . import views
urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('create/', views.student_create, name='student_create'),
    path('import/', views.student_import, name='student_import'),
    path('<int:pk>/', views.student_detail, name='student_detail'),
    path('<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('<int:student_pk>/break/add/', views.break_create, name='break_create'),
    path('programmes/', views.programme_list, name='programme_list'),
    path('programmes/create/', views.programme_create, name='programme_create'),
    path('batches/', views.batch_list, name='batch_list'),
    path('batches/create/', views.batch_create, name='batch_create'),
]
