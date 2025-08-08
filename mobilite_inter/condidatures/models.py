
from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    identifiant = models.CharField(max_length=20, unique=True)
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