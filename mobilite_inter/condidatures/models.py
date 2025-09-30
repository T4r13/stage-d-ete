
from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    identifiant = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True,null=True, blank=True)  
    moyenne = models.FloatField()
    langues = models.CharField(max_length=100)
    activites = models.TextField(blank=True)
    certificats = models.TextField(blank=True)

    def __str__(self):
        return f"Profil de {self.user.username}"

class Score(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score_final = models.FloatField()
    date_calcul = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Score de {self.user.username} : {self.score_final}"

class Classement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rang = models.IntegerField()
    annee = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - Rang {self.rang} ({self.annee})"
    

    # 🔹 Nouveau modèle pour les offres de stage
class OffreStage(models.Model):
    titre = models.CharField(max_length=200)
    description = models.TextField()
    entreprise = models.CharField(max_length=150)
    localisation = models.CharField(max_length=150)
    date_debut = models.DateField()
    date_fin = models.DateField()
    date_publication = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titre} - {self.entreprise}"
    


# candidature

class Candidature(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
    ]

    candidat = models.ForeignKey(User, on_delete=models.CASCADE)
    offre = models.ForeignKey(OffreStage, on_delete=models.CASCADE)
    date_candidature = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')

    def __str__(self):
        return f"{self.candidat.username} - {self.offre.titre} ({self.statut})"
    
    


