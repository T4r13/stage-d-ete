from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import login , authenticate , logout
from django.contrib.auth.models import User
from .models import Profile, Score , Classement ,OffreStage , Candidature
from django.utils import timezone
import logging
from django import forms
from django.contrib import messages



# Configurer un logger pour débogage
logger = logging.getLogger(__name__)


def candidate_login(request):
    if request.method == 'POST':
        logger.debug(f"Données POST reçues pour candidat : {request.POST}")
        if 'identifiant' in request.POST and 'username' in request.POST:
            identifiant = request.POST['identifiant']
            username = request.POST['username']
            logger.debug(f"Tentative de connexion candidat - Identifiant: {identifiant}, Username: {username}")
            try:
                profile = Profile.objects.get(identifiant=identifiant, user__username=username)
                user = profile.user
                if user and user.is_active:
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                    logger.debug(f"Connexion candidat réussie pour {username}")
                    return redirect('profile_details')
                else:
                    logger.debug(f"Utilisateur inactif ou non trouvé pour {username}")
                    return render(request, 'condidatures/login.html', {'error': 'Utilisateur inactif ou non trouvé.', 'form_type': 'candidate'})
            except Profile.DoesNotExist:
                logger.debug(f"Profil non trouvé pour Identifiant: {identifiant}, Username: {username}")
                return render(request, 'condidatures/login.html', {'error': 'Identifiant ou nom d\'utilisateur incorrect.', 'form_type': 'candidate'})
        else:
            logger.debug(f"Formulaire candidat invalide - POST: {request.POST}")
            return render(request, 'condidatures/login.html', {'error': 'Formulaire candidat invalide.', 'form_type': 'candidate'})
    return render(request, 'condidatures/login.html', {'form_type': 'candidate'})

def admin_login(request):
    if request.method == 'POST':
        logger.debug(f"Données POST reçues pour admin : {request.POST}")
        if 'admin_username' in request.POST and 'admin_password' in request.POST:
            admin_username = request.POST['admin_username']
            admin_password = request.POST['admin_password']
            logger.debug(f"Tentative de connexion admin - Username: {admin_username}")
            user = authenticate(request, username=admin_username, password=admin_password)
            if user is not None:
                logger.debug(f"Utilisateur authentifié : {user}")
                if user.is_superuser:
                    login(request, user)
                    logger.debug(f"Connexion admin réussie pour {admin_username}")
                    return redirect('admin_dashboard')
                else:
                    logger.debug(f"Utilisateur {admin_username} n'est pas un superuser")
                    return render(request, 'condidatures/login.html', {'error': 'Cet utilisateur n\'est pas un administrateur.', 'form_type': 'admin'})
            else:
                logger.debug(f"Authentification échouée pour {admin_username}")
                return render(request, 'condidatures/login.html', {'error': 'Nom d\'utilisateur ou mot de passe admin incorrect.', 'form_type': 'admin'})
        else:
            logger.debug(f"Formulaire admin invalide - POST: {request.POST}")
            return render(request, 'condidatures/login.html', {'error': 'Formulaire admin invalide.', 'form_type': 'admin'})
    return render(request, 'condidatures/login.html', {'form_type': 'admin'})

#------------------------------------------------------------------------------------------------------------------------
def profile_details(request):
    if not request.user.is_authenticated:
        return redirect('login')

    profile = request.user.profile
    offres = OffreStage.objects.all().order_by('-date_debut')

    return render(request, 'condidatures/profile_details.html', {
        'profile': profile,
        'offres': offres
    })


#---------------------------------------------------------------------------------------------------------


def admin_dashboard(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login')
    
    # Récupérer tous les profils
    profiles = Profile.objects.all()
    students_data = []

    # Définir l'année scolaire
    annee_scolaire = 2025

    # Calculer les données pour chaque profil
    for profile in profiles:
        # Vérifier et récupérer activites
        activites = profile.activites if profile.activites else "Aucune activité"

        # Calculer le score pour ce profil avec les nouveaux champs
        langues_list = [lang.strip() for lang in profile.langues.split(',') if lang.strip()]
        num_langues = len(langues_list)
        
        # Score de base (moyenne + langues)
        score_base = (profile.moyenne * 10) + (num_langues * 5)
        
        # Score des nouveaux critères
        score_projets = profile.participation_projets * 2
        score_experience = profile.experience_internationale * 8
        
        # Score niveau anglais
        niveau_anglais_scores = {
            'debutant': 2,
            'intermediaire': 5,
            'avance': 8,
            'bilingue': 10
        }
        score_anglais = niveau_anglais_scores.get(profile.niveau_anglais, 0)
        
        # Score des compétences
        score_competences = (profile.motivation_score + profile.leadership_score + 
                           profile.innovation_score + profile.adaptabilite_score) * 2
        
        # Score engagement
        score_engagement = profile.engagement_communautaire * 0.5
        
        # Bonus stage antérieur
        bonus_stage = 15 if profile.stage_anterieur else 0
        
        # Score recommandations
        score_recommandations = profile.recommandation_prof * 3
        
        # Score portfolio
        score_portfolio = profile.portfolio_qualite * 2
        
        # Score final total
        score_final = (score_base + score_projets + score_experience + score_anglais + 
                      score_competences + score_engagement + bonus_stage + 
                      score_recommandations + score_portfolio)

        # Date de calcul
        date_calcul = profile.user.date_joined.date() if hasattr(profile.user, 'date_joined') else timezone.now().date()

        # Ajouter les données au tableau
        students_data.append({
            'username': profile.user.username,
            'identifiant': profile.identifiant,
            'moyenne': profile.moyenne,
            'langues': profile.langues,
            'activites': activites,
            'score_final': round(score_final, 2),
            'date_calcul': date_calcul,
            'rang': None,  # À calculer après
            'annee': annee_scolaire,
            # Nouveaux champs pour l'admin
            'participation_projets': profile.participation_projets,
            'experience_internationale': profile.experience_internationale,
            'niveau_anglais': profile.get_niveau_anglais_display(),
            'motivation_score': profile.motivation_score,
            'leadership_score': profile.leadership_score,
            'innovation_score': profile.innovation_score,
            'adaptabilite_score': profile.adaptabilite_score,
            'engagement_communautaire': profile.engagement_communautaire,
            'stage_anterieur': profile.stage_anterieur,
            'recommandation_prof': profile.recommandation_prof,
            'portfolio_qualite': profile.portfolio_qualite
        })

    # Trier par score_final pour déterminer le rang
    students_data.sort(key=lambda x: x['score_final'] or 0, reverse=True)
    for rank, student in enumerate(students_data, 1):
        student['rang'] = rank

    candidatures = Candidature.objects.select_related('candidat', 'offre')

    return render(request, 'condidatures/admin_dashboard.html', {
        'students_data': students_data,
        'annee_scolaire': annee_scolaire,
        'candidatures': candidatures
    })

from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt  # à utiliser si fetch ne passe pas le token

@require_POST
@csrf_exempt  # temporaire pour tester si le CSRF bloque
def changer_statut_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Accès refusé'}, status=403)

    candidature_id = request.POST.get('candidature_id')
    nouveau_statut = request.POST.get('statut')

    if not candidature_id or not nouveau_statut:
        return JsonResponse({'success': False, 'error': 'Paramètres manquants'}, status=400)

    try:
        candidature = Candidature.objects.get(id=int(candidature_id))
        candidature.statut = nouveau_statut
        candidature.save()

        # Envoi d'email, mais ne bloque pas si erreur
        try:
            profile = Profile.objects.get(user=candidature.candidat)
            email = profile.email.strip()
            if email:
                sujet = "Résultat de votre candidature"
                if nouveau_statut == "acceptee":
                    message = f"Bonjour {candidature.candidat.username},\n\nFélicitations ! Votre candidature pour l'offre '{candidature.offre.titre}' a été ACCEPTÉE. \n\n Veuillez contactez notre service"
                else:
                    message = f"Bonjour {candidature.candidat.username},\n\nNous vous remercions, votre candidature pour l'offre '{candidature.offre.titre}' a été REFUSÉE."

                send_mail(sujet, message, 'bchirtarak@gmail.com', [email], fail_silently=True)

        except Profile.DoesNotExist:
            pass  # ne bloque pas l'update

        return JsonResponse({'success': True, 'statut': candidature.statut})

    except Candidature.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Candidature introuvable'}, status=404)

#-------------------------------------------------------------------------------------------------------------------------------------------

def logout_view(request):
    logout(request)
    return redirect('candidate_login')



#----------------------------------------------------------------------------------------------------------------------------
def stats(request):
    if request.user.is_authenticated:
        profile = request.user.profile
        activites = profile.activites if profile.activites else "Aucune activité"

        # Calcul du score avec les nouveaux champs
        langues_list = [lang.strip() for lang in profile.langues.split(',') if lang.strip()]
        num_langues = len(langues_list)
        
        # Score de base
        score_base = (profile.moyenne * 10) + (num_langues * 5)
        
        # Score des nouveaux critères
        score_projets = profile.participation_projets * 2
        score_experience = profile.experience_internationale * 8
        
        # Score niveau anglais
        niveau_anglais_scores = {
            'debutant': 2,
            'intermediaire': 5,
            'avance': 8,
            'bilingue': 10
        }
        score_anglais = niveau_anglais_scores.get(profile.niveau_anglais, 0)
        
        # Score des compétences
        score_competences = (profile.motivation_score + profile.leadership_score + 
                           profile.innovation_score + profile.adaptabilite_score) * 2
        
        # Score engagement
        score_engagement = profile.engagement_communautaire * 0.5
        
        # Bonus stage antérieur
        bonus_stage = 15 if profile.stage_anterieur else 0
        
        # Score recommandations
        score_recommandations = profile.recommandation_prof * 3
        
        # Score portfolio
        score_portfolio = profile.portfolio_qualite * 2
        
        # Score final total
        score_final = (score_base + score_projets + score_experience + score_anglais + 
                      score_competences + score_engagement + bonus_stage + 
                      score_recommandations + score_portfolio)

        # Calcul du rang parmi tous les profils
        all_profiles = Profile.objects.all()
        all_students_data = []
        for p in all_profiles:
            langues = [lang.strip() for lang in p.langues.split(',') if lang.strip()]
            num_langues = len(langues)
            
            # Même calcul de score pour tous
            score_base = (p.moyenne * 10) + (num_langues * 5)
            score_projets = p.participation_projets * 2
            score_experience = p.experience_internationale * 8
            score_anglais = niveau_anglais_scores.get(p.niveau_anglais, 0)
            score_competences = (p.motivation_score + p.leadership_score + 
                               p.innovation_score + p.adaptabilite_score) * 2
            score_engagement = p.engagement_communautaire * 0.5
            bonus_stage = 15 if p.stage_anterieur else 0
            score_recommandations = p.recommandation_prof * 3
            score_portfolio = p.portfolio_qualite * 2
            
            score = (score_base + score_projets + score_experience + score_anglais + 
                    score_competences + score_engagement + bonus_stage + 
                    score_recommandations + score_portfolio)
            
            all_students_data.append({
                'username': p.user.username,
                'score_final': score
            })

        all_students_data.sort(key=lambda x: x['score_final'], reverse=True)
        rang = next((i + 1 for i, student in enumerate(all_students_data) if student['username'] == profile.user.username), None)

        date_calcul = profile.user.date_joined.date() if hasattr(profile.user, 'date_joined') else timezone.now().date()

        students_data = [{
            'username': profile.user.username,
            'identifiant': profile.identifiant,
            'moyenne': profile.moyenne,
            'langues': profile.langues,
            'activites': activites,
            'score_final': round(score_final, 2),
            'date_calcul': date_calcul,
            'rang': rang,
            'annee': 2025
        }]

        # Récupération des candidatures envoyées par l'utilisateur avec statut
        candidatures = Candidature.objects.filter(candidat=profile.user).select_related('offre')

        return render(request, 'condidatures/stats.html', {
            'students_data': students_data,
            'candidatures': candidatures
        })

    return redirect('login')


#---------------------------------------------------------------------------------------------------------------
# Formulaire Django pour l'offre
class OffreStageForm(forms.ModelForm):
    class Meta:
        model = OffreStage
        fields = ['titre', 'description', 'entreprise', 'localisation', 'date_debut', 'date_fin']
        widgets = {
            'titre': forms.TextInput(attrs={'placeholder': 'Ex: Stage en développement web', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Décrivez les missions et objectifs...', 'class': 'form-control'}),
            'entreprise': forms.TextInput(attrs={'placeholder': 'Nom de l\'entreprise', 'class': 'form-control'}),
            'localisation': forms.TextInput(attrs={'placeholder': 'Ville, Pays', 'class': 'form-control'}),
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

# -------------------------------------------------------------------------------------------------
# Vue pour ajouter une offre de stage (admin uniquement)
def ajouter_offre_stage(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login')  # Redirige si non connecté ou pas admin

    if request.method == 'POST':
        form = OffreStageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Offre de stage ajoutée avec succès.")
            return redirect('liste_offres')  # Redirige vers la liste des offres
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = OffreStageForm()

    return render(request, 'condidatures/ajouter_offre.html', {'form': form})

# -------------------------------------------------------------------------------------------------
# Vue pour afficher la liste des offres (admin uniquement)
def liste_offres_stage(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login')

    offres = OffreStage.objects.all().order_by('-date_publication')
    return render(request, 'condidatures/liste_offres.html', {'offres': offres})
#--------------------------------------------------------------------------------------------------------
# ✅ Mise à jour d’une offre
def update_offre_stage(request, id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login')

    offre = get_object_or_404(OffreStage, id=id)
    if request.method == 'POST':
        form = OffreStageForm(request.POST, instance=offre)
        if form.is_valid():
            form.save()
            messages.success(request, "Offre mise à jour avec succès.")
            return redirect('liste_offres')
        else:
            messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form = OffreStageForm(instance=offre)  # pré-rempli avec anciennes données

    return render(request, 'condidatures/update_offre.html', {'form': form})

# ✅ Suppression d’une offre
def delete_offre_stage(request, id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login')

    offre = get_object_or_404(OffreStage, id=id)
    if request.method == 'POST':
        offre.delete()
        messages.success(request, "Offre supprimée avec succès.")
        return redirect('liste_offres')

    return render(request, 'condidatures/delete_offre.html', {'offre': offre})


#------------------------------------------------------------------------------------------------------

def postuler_offre(request, offre_id):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        offre = OffreStage.objects.get(id=offre_id)
    except OffreStage.DoesNotExist:
        messages.error(request, "Offre introuvable.")
        return redirect('profile_details')

    # Vérifier si le candidat a déjà postulé
    if Candidature.objects.filter(candidat=request.user, offre=offre).exists():
        messages.warning(request, "Vous avez déjà postulé à cette offre.")
    else:
        Candidature.objects.create(candidat=request.user, offre=offre)
        messages.success(request, f"Votre candidature pour '{offre.titre}' a été envoyée avec succès.")

    return redirect('profile_details')



from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from .models import Candidature

def export_candidatures_pdf(request):
    if not request.user.is_staff:
        return HttpResponse(status=403)

    candidatures = Candidature.objects.select_related('offre', 'candidat').all()
    template = get_template('condidatures/candidatures_pdf.html')
    html = template.render({'candidatures': candidatures})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="candidatures.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF', status=500)
    return response