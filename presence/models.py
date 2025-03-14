from datetime import timedelta
from django.db import models
from accueil.models import Utilisateur
from employe.models import Employe, DemandeConges, Notification, Formation, Absence
# Create your models here.


class Presence(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    heure_arrivee = models.TimeField(null=True, blank=True)
    heure_depart = models.TimeField(null=True, blank=True)
    retard = models.BooleanField(default=False)
    heures_travail = models.DurationField(default=timedelta(hours=8))  # Nombre d'heures de travail par jour
    compteur_actif = models.BooleanField(default=False)
    temps_restant = models.DurationField(default=timedelta(hours=8))  # Temps restant
    heure_derniere_action = models.DateTimeField(null=True, blank=True)  # Ajouter ce champ

    def __str__(self):
        return f"{self.employe.nom} {self.employe.prenom} - {self.date}"
    
    
class SettingsHeures(models.Model):
    heure_arrivee_normale = models.TimeField(default="08:00:00")
    heure_depart_normale = models.TimeField(default="16:00:00")
