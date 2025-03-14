from datetime import timedelta
from django.db import models
from accueil.models import Utilisateur


# Create your models here.

class Indemnite(models.Model):
    nom = models.CharField(max_length=100)
    plafond = models.DecimalField(max_digits=10, decimal_places=2)
    pourcentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.nom
        
        
        

class EmployeIndemnite(models.Model):
    employe = models.ForeignKey('employe.Employe', on_delete=models.CASCADE)
    indemnite = models.ForeignKey(Indemnite, on_delete=models.CASCADE)
    somme_percue = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.employe.nom} - {self.indemnite.nom} : {self.somme_percue}"
        
    def calculer_exoneration(self):
        # Obtenir le salaire brut imposable de l'employé
        salaire_brut_imposable = self.employe.calculer_salaire_brut_imposable()

        # Calculer l'exonération basée sur le pourcentage de l'indemnité
        exonoration_calculee = (self.indemnite.pourcentage / 100) * salaire_brut_imposable

        # Obtenir la valeur minimum entre la somme perçue, le plafond et l'exonération calculée
        exonoration_finale = min(self.somme_percue, self.indemnite.plafond, exonoration_calculee)

        # Afficher les détails pour débogage
        print(f"Indemnité: {self.indemnite.nom}")
        print(f"Somme perçue: {self.somme_percue}")
        print(f"Plafond: {self.indemnite.plafond}")
        print(f"Exonération calculée: {exonoration_calculee}")
        print(f"Exonération finale: {exonoration_finale}")

        return exonoration_finale
        


class AvantageEnNature(models.Model):
    nom = models.CharField(max_length=100)
    valeur = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nom
    
    
    
class RetenueRevenu(models.Model):
    TYPE_CHOICES = [
        ('REVENUE', 'Revenue'),
        ('RETENUE', 'Retenue'),
    ]

    employe = models.ForeignKey('employe.Employe', on_delete=models.CASCADE, related_name='retenues_revenus')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.CharField(max_length=255)  # A description of the revenue or withholding
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.employe.nom} - {self.type} : {self.montant} FCFA"
    