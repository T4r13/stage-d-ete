from django.shortcuts import render, redirect
from django.contrib.auth import login , authenticate , logout
from django.contrib.auth.models import User
from .models import Profile, Score , Classement
from django.utils import timezone
import logging

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
    if request.user.is_authenticated:
        profile = request.user.profile
        return render(request, 'condidatures/profile_details.html', {'profile': profile})
    return redirect('login')


#---------------------------------------------------------------------------------------------------------


def admin_dashboard(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login')
    
    # Récupérer tous les profils
    profiles = Profile.objects.all()
    students_data = []

    # Définir l'année scolaire
    annee_scolaire = 2025  # Ajustez si vous voulez l'année en cours avec timezone.now().year

    # Calculer les données pour chaque profil
    for profile in profiles:
        # Vérifier et récupérer activites
        activites = profile.activites if profile.activites else "Aucune activité"

        # Calculer le score pour ce profil
        langues_list = [lang.strip() for lang in profile.langues.split(',') if lang.strip()]
        num_langues = len(langues_list)
        score_final = (profile.moyenne * 10) + (num_langues * 5) if profile.moyenne is not None else 0

        # Date de calcul : utiliser la date de création du profil sans le temps
        date_calcul = profile.user.date_joined.date() if hasattr(profile.user, 'date_joined') else timezone.now().date()

        # Ajouter les données au tableau
        students_data.append({
            'username': profile.user.username,
            'identifiant': profile.identifiant,
            'moyenne': profile.moyenne,
            'langues': profile.langues,
            'activites': activites,
            'score_final': score_final,
            'date_calcul': date_calcul,
            'rang': None,  # À calculer après
            'annee': annee_scolaire
        })

    # Trier par score_final pour déterminer le rang
    students_data.sort(key=lambda x: x['score_final'] or 0, reverse=True)
    for rank, student in enumerate(students_data, 1):
        student['rang'] = rank

    return render(request, 'condidatures/admin_dashboard.html', {'students_data': students_data, 'annee_scolaire': annee_scolaire})

#-------------------------------------------------------------------------------------------------------------------------------------------

def logout_view(request):
    logout(request)
    return redirect('candidate_login')



#----------------------------------------------------------------------------------------------------------------------------
def stats(request):
    if request.user.is_authenticated:
        # Récupérer le profil de l'utilisateur connecté
        profile = request.user.profile

        # Vérifier et récupérer activites depuis la base de données
        activites = profile.activites if profile.activites else "Aucune activité"

        # Calculer le score pour ce profil
        langues_list = [lang.strip() for lang in profile.langues.split(',') if lang.strip()]
        num_langues = len(langues_list)
        score_final = (profile.moyenne * 10) + (num_langues * 5)

        # Récupérer tous les profils pour calculer le rang
        all_profiles = Profile.objects.all()
        all_students_data = []
        for p in all_profiles:
            langues = [lang.strip() for lang in p.langues.split(',') if lang.strip()]
            num_langues = len(langues)
            score = (p.moyenne * 10) + (num_langues * 5)
            all_students_data.append({
                'username': p.user.username,
                'score_final': score
            })

        # Trier par score_final pour déterminer le rang
        all_students_data.sort(key=lambda x: x['score_final'], reverse=True)
        rang = next((i + 1 for i, student in enumerate(all_students_data) if student['username'] == profile.user.username), None)

        # Date de calcul : utiliser la date de création du profil sans le temps
        date_calcul = profile.date_joined.date() if hasattr(profile, 'date_joined') else timezone.now().date()

        # Préparer les données pour cet utilisateur
        students_data = [{
            'username': profile.user.username,
            'identifiant': profile.identifiant,
            'moyenne': profile.moyenne,
            'langues': profile.langues,
            'activites': activites,  # Utilise la valeur récupérée
            'score_final': score_final,
            'date_calcul': date_calcul,
            'rang': rang,
            'annee': 2025
        }]

        return render(request, 'condidatures/stats.html', {'students_data': students_data})
    return redirect('login')