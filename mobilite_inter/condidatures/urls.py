from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='login/', permanent=False)),
    path('login/', views.candidate_login, name='candidate_login'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('profile/', views.profile_details, name='profile_details'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('changer_statut_ajax/', views.changer_statut_ajax, name='changer_statut_ajax'),
    path('stats/', views.stats, name='stats'),
    path('logout/', views.logout_view, name='logout'),
    path('ajouter-offre/', views.ajouter_offre_stage, name='ajouter_offre'),
    path('liste-offres/', views.liste_offres_stage, name='liste_offres'),
    path('offres/update/<int:id>/', views.update_offre_stage, name='update_offre'),
    path('offres/delete/<int:id>/', views.delete_offre_stage, name='delete_offre'),
    path('postuler/<int:offre_id>/', views.postuler_offre, name='postuler_offre'),
    path('candidatures/export/pdf/', views.export_candidatures_pdf, name='export_candidatures_pdf'),


]