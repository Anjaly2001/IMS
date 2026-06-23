from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('students/', include('students.urls')),
    path('organisations/', include('organisations.urls')),
    path('internships/', include('internships.urls')),
    path('assessments/', include('assessments.urls')),
    path('reports/', include('reports.urls')),
    path('dashboard/', include('accounts.dashboard_urls')),
    path('', lambda request: redirect('dashboard'), name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
