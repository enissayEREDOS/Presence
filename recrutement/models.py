from datetime import timedelta
from django.db import models
from accueil.models import Utilisateur
from employe.models import Employe, DemandeConges, Notification, Formation, Absence
from django.contrib.auth.hashers import make_password, check_password
# Create your models here.



class Poste(models.Model):
    titre = models.CharField(max_length=100)
    description = models.TextField()
    date_publication = models.DateField(auto_now_add=True)
    date_fin_publication = models.DateField()

    def __str__(self):
        return self.titre

class Candidat(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mot_de_passe = models.CharField(max_length=255)  # Stocker le mot de passe hashé
    telephone = models.CharField(max_length=15)
    cv = models.FileField(upload_to='candidats/cv/')
    lettre_motivation = models.FileField(upload_to='candidats/lettres/')
    date_candidature = models.DateField(null=True, blank=True)  # Plus de auto_now_add
    poste = models.ForeignKey('Poste', on_delete=models.SET_NULL, null=True, blank=True)
    etape_processus = models.CharField(
        max_length=50,
        choices=[
            ('Candidature reçue', 'Candidature reçue'),
            ('Entretien', 'Entretien'),
            ('Test technique', 'Test technique'),
            ('Offre envoyée', 'Offre envoyée'),
            ('Rejeté', 'Rejeté')
        ],
        null=True,  # Permettre que ce champ soit vide initialement
        blank=True
    )
    entretien_date = models.DateTimeField(null=True, blank=True)
    entretien_heure = models.TimeField(null=True, blank=True)  # Heure de l'entretien


    # Méthode pour définir le mot de passe
    def set_password(self, raw_password):
        self.mot_de_passe = make_password(raw_password)
        self.save()

    # Méthode pour vérifier le mot de passe
    def check_password(self, raw_password):
        return check_password(raw_password, self.mot_de_passe)

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.poste.titre if self.poste else 'Aucun poste'}"

