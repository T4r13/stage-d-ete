from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='login/', permanent=False)),
    path('login/', views.candidate_login, name='candidate_login'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('profile/', views.profile_details, name='profile_details'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('stats/', views.stats, name='stats'),
    path('logout/', views.logout_view, name='logout'),
]