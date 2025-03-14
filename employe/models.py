import math
import random
import string
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum


from accueil.models import Utilisateur
from paiement.models import AvantageEnNature
######################################################
class Departement(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom
##########################################################
class Fonction(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    salaire = models.DecimalField(max_digits=10, decimal_places=2)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE, related_name='fonctions')

    def __str__(self):
        return self.nom

########################################################





class Employe(Utilisateur):
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('O', 'Autre'),
    ]

    TYPE_CONTRAT_CHOICES = [
        ('CDI', 'CDI'),
        ('CDD', 'CDD'),
    ]

    MODE_PAIEMENT_CHOICES = [
        ('VIREMENT', 'Virement bancaire'),
        ('CHEQUE', 'Chèque'),
        ('ESPECE', 'Espèces'),
    ]
    
    CATEGORIE_CHOICES = [
        ('CADRE', 'Cadre'),
        ('AUTRE_CATEGORIES', 'Autre_categories'),
    ]

    # Champs existants
    date_naissance = models.DateField()
    genre = models.CharField(max_length=1, choices=SEXE_CHOICES)
    nationalite = models.CharField(max_length=100)
    numero_telephone = models.CharField(max_length=20)
    fonction = models.ForeignKey(Fonction, on_delete=models.SET_NULL, null=True)  # Liaison avec le modèle Fonction
    departement = models.ForeignKey(Departement, on_delete=models.SET_NULL, null=True)  # Liaison avec le modèle Département
    date_debut = models.DateField()
    type_contrat = models.CharField(max_length=3, choices=TYPE_CONTRAT_CHOICES)
    date_fin_contrat = models.DateField(null=True, blank=True)
    salaire_base = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Le salaire sera calculé
    heures_travail = models.CharField(max_length=50, blank=True)
    nbr_jours_conges_AN = models.PositiveIntegerField(default=0, blank=True)

    #Nouveaux champs
    categorie = models.CharField(max_length=50, choices=CATEGORIE_CHOICES)
    nombre_enfants = models.PositiveIntegerField(default=0)
    matricule = models.CharField(max_length=10, unique=True, blank=True)  # Alphanumérique
    numero_cnss = models.CharField(max_length=15, unique=True)
    numero_compte = models.CharField(max_length=30)
    mode_paiement = models.CharField(max_length=10, choices=MODE_PAIEMENT_CHOICES)
    sursalaire = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True)
    prime_anciennete = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True)
    avantages_en_nature = models.ManyToManyField(AvantageEnNature, blank=True)

    # Fichiers
    cv = models.FileField(upload_to='documents/cvs/', null=True, blank=True)
    lettre_motivation = models.FileField(upload_to='documents/lettres_motivation/', null=True, blank=True)
    contrat_travail = models.FileField(upload_to='documents/contrats_travail/', null=True, blank=True)
    certificats_diplomes = models.FileField(upload_to='documents/certificats_diplomes/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.fonction:
            self.salaire_base = self.fonction.salaire  # On prend le salaire de base de la fonction
        if self.type_contrat == 'CDD' and not self.date_fin_contrat:
            raise ValueError('La date de fin de contrat est requise pour un CDD.')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.prenom} {self.nom} ({self.fonction})'
    
    
    
        # Méthode pour calculer le SBPD
    def calculer_salaire_brut_permanent_de_base(self):
        # Salaire de base, sursalaire et prime d'ancienneté avec valeur par défaut à 0
        salaire_base = self.salaire_base or 0
        sursalaire = self.sursalaire or 0
        prime_anciennete = self.prime_anciennete or 0

        # Calcul du SBPD
        sbpd = salaire_base + sursalaire + prime_anciennete
        print(f"Salaire de base: {salaire_base}, Sursalaire: {sursalaire}, Prime ancienneté: {prime_anciennete}")
        print(f"SBPD (Salaire Brut Permanent de Base): {sbpd}")
        
        return sbpd

    def calculer_base_cnss(self):
        # Calculer la somme des indemnités
        from paiement.models import EmployeIndemnite
        indemnites = EmployeIndemnite.objects.filter(employe=self)
        somme_indemnites = sum(indemnite.somme_percue for indemnite in indemnites)
        
        # Base CNSS
        base_cnss = self.calculer_salaire_brut_permanent_de_base() + somme_indemnites
        print(f"Somme des indemnités: {somme_indemnites}")
        print(f"Base CNSS: {base_cnss}")
        
        return base_cnss

        


    def calculer_cnss(self):
        base_cnss = self.calculer_base_cnss()
        sbpd = self.calculer_salaire_brut_permanent_de_base()

        # Conversion en Decimal pour assurer la compatibilité
        cnss_base_5_5 = base_cnss * Decimal('5.5') / Decimal('100')
        cnss_sbpd_8 = sbpd * Decimal('8') / Decimal('100')
        plafond_cnss = Decimal('33000')

        # Calcul de la CNSS en prenant le minimum
        calcule_cnss = min(cnss_base_5_5, cnss_sbpd_8, plafond_cnss)
        

        # Afficher les détails pour vérifier le calcul
        print(f"Base CNSS * 5.5%: {cnss_base_5_5}")
        print(f"SBPD * 8%: {cnss_sbpd_8}")
        print(f"Plafond CNSS: {plafond_cnss}")
        print(f"CNSS calculée: {calcule_cnss}")


        return calcule_cnss
    
    
    
    def calculer_cnss2(self):
        base_cnss = self.calculer_base_cnss()

        # Conversion en Decimal pour assurer la compatibilité
        cnss_base_5_5 = base_cnss * Decimal('5.5') / Decimal('100')
        plafond_cnss = Decimal('33000')

    
        
        calcule_cnss2 = min(cnss_base_5_5, plafond_cnss)

        # Afficher les détails pour vérifier le calcul
        print(f"CNSS calculée2: {calcule_cnss2}")
        

        return calcule_cnss2



    ###########################
    def calculer_salaire_brut_imposable(self):
        # Étape 1 : Calculer la base CNSS
        base_cnss = self.calculer_base_cnss()
        
        # Étape 2 : Calculer la CNSS
        cnss = self.calculer_cnss()
        
        # Étape 3 : Calculer la somme des avantages en nature
        avantages_en_nature = self.avantages_en_nature.all()
        somme_avantages_en_nature = sum(avantage.valeur for avantage in avantages_en_nature)

        # Étape 4 : Calculer le salaire brut imposable
        salaire_brut_imposable = base_cnss - cnss + somme_avantages_en_nature

        # Afficher les détails pour vérifier le calcul
        print(f"Base CNSS: {base_cnss}")
        print(f"CNSS: {cnss}")
        print(f"Somme des avantages en nature: {somme_avantages_en_nature}")
        print(f"Salaire brut imposable: {salaire_brut_imposable}")

        return salaire_brut_imposable


        # Méthode pour calculer l'exonération totale des indemnités
    def calculer_exonerations(self):
        from paiement.models import EmployeIndemnite  # Importer pour éviter les boucles d'import
        
        # Récupérer toutes les indemnités de l'employé
        indemnites_employe = EmployeIndemnite.objects.filter(employe=self)
        total_exoneration = 0  # Initialiser la somme des exonérations

        for indemnite_employe in indemnites_employe:
            # Calculer l'exonération pour chaque indemnité
            exonoration = indemnite_employe.calculer_exoneration()
            
            # Ajouter l'exonération au total
            total_exoneration += exonoration
        
        # Afficher les détails pour débogage
        print(f"Exonération totale pour l'employé {self.nom}: {total_exoneration}")
        
        return total_exoneration
    
    
    
    def calculer_abattement_frais_charges(self):
        # Récupérer le SBPD
        sbpd = self.calculer_salaire_brut_permanent_de_base()

        # Calculer l'abattement selon la catégorie de l'employé
        if self.categorie == 'CADRE':
            abattement = sbpd * 20 / 100
        else:  # Autre catégorie
            abattement = sbpd * 25 / 100

        # Afficher pour vérifier le calcul
        print(f"SBPD: {sbpd}")
        print(f"Abattement frais et charges: {abattement}")

        return abattement


    def calculer_salaire_net_imposable(self):
        # Récupérer le salaire brut imposable
        salaire_brut_imposable = self.calculer_salaire_brut_imposable()
        
        # Calculer le total des exonérations
        total_exoneration = self.calculer_exonerations()

        # Calculer l'abattement frais et charges
        abattement_frais_charges = self.calculer_abattement_frais_charges()

        # Calcul du salaire net imposable
        salaire_net_imposable = salaire_brut_imposable - total_exoneration - abattement_frais_charges

        # Afficher pour vérifier le calcul
        print(f"Salaire Brut Imposable: {salaire_brut_imposable}")
        print(f"Total Exonérations: {total_exoneration}")
        print(f"Abattement Frais et Charges: {abattement_frais_charges}")
        print(f"Salaire Net Imposable: {salaire_net_imposable}")

        return salaire_net_imposable



    def calculer_base_uits_arrondie(self):
            # Calculer le salaire net imposable
        salaire_net_imposable = self.calculer_salaire_net_imposable()

        # Arrondir à l'inférieur au multiple de 10
        base_uits_arrondie = math.floor(salaire_net_imposable / 100) * 100

        # Afficher pour vérifier le calcul
        print(f"Base UITS arrondie: {base_uits_arrondie}")

        return base_uits_arrondie


    def calculer_uits_brut(self):
        # Appel de la méthode pour obtenir la base UITS arrondie
        base_uits_arrondie = self.calculer_base_uits_arrondie() 
        uits_brut = 0

        # Appliquer le barème progressif par tranches
        if base_uits_arrondie > 250000:
            uits_brut += (base_uits_arrondie - 250000) * 0.25
            base_uits_arrondie = 250000
        if base_uits_arrondie > 170000:
            uits_brut += (base_uits_arrondie - 170000) * 0.217
            base_uits_arrondie = 170000
        if base_uits_arrondie > 120000:
            uits_brut += (base_uits_arrondie - 120000) * 0.184
            base_uits_arrondie = 120000
        if base_uits_arrondie > 80000:
            uits_brut += (base_uits_arrondie - 80000) * 0.157
            base_uits_arrondie = 80000
        if base_uits_arrondie > 50000:
            uits_brut += (base_uits_arrondie - 50000) * 0.139
            base_uits_arrondie = 50000
        if base_uits_arrondie > 30000:
            uits_brut += (base_uits_arrondie - 30000) * 0.121

        # Les premiers 30 000 FCFA ne sont pas taxés (0%)
        
        print(f"UITS Brut calculé: {uits_brut}")
        return uits_brut


    def calculer_abattement_uits(self):
        uits_brut = self.calculer_uits_brut()
        
        # Déterminer le pourcentage en fonction du nombre d'enfants
        if self.nombre_enfants == 0:
            pourcentage = 0.0
        elif self.nombre_enfants == 1:
            pourcentage = 0.08
        elif self.nombre_enfants == 2:
            pourcentage = 0.10
        elif self.nombre_enfants == 3:
            pourcentage = 0.12
        else:
            pourcentage = 0.14  # Pour 4 enfants ou plus
        
        # Calculer l'abattement UITS
        abattement_uits = uits_brut * pourcentage

        # Afficher pour vérifier le calcul (facultatif)
        print(f"UITS Brut: {uits_brut}, Nombre d'enfants: {self.nombre_enfants}, Pourcentage: {pourcentage * 100}%")
        print(f"Abattement UITS: {abattement_uits}")

        return abattement_uits


    def calculer_uits_net(self):
            # Calculer l'UITS brut et l'abattement UITS
        uits_brut = self.calculer_uits_brut()
        abattement_uits = self.calculer_abattement_uits()

        # Convertir les valeurs en Decimal si elles sont des chaînes
        if isinstance(uits_brut, str):
            uits_brut = Decimal(uits_brut)
        if isinstance(abattement_uits, str):
            abattement_uits = Decimal(abattement_uits)

        # Calculer l'UITS net
        uits_net = uits_brut - abattement_uits

        # Afficher pour vérifier le calcul (facultatif)
        print(f"UITS Brut: {uits_brut}, Abattement UITS: {abattement_uits}")
        print(f"UITS Net: {uits_net}")

        return uits_net




        

    def calculer_salaire_net(self):
        base_cnss = self.calculer_base_cnss()  # Méthode pour calculer la base CNSS
        calcul_cnss2 = self.calculer_cnss2()  # Méthode pour calculer la CNSS
        uits_net = self.calculer_uits_net()  # Méthode pour calculer l'IUTS net

        # Convertir les valeurs en Decimal si ce sont des chaînes
        if isinstance(base_cnss, str):
            base_cnss = Decimal(base_cnss)
        if isinstance(calcul_cnss2, str):
            calcul_cnss2 = Decimal(calcul_cnss2)
        if isinstance(uits_net, str):
            uits_net = Decimal(uits_net)

        # Somme des retenues et revenus
        retenues = self.retenues_revenus.filter(type='RETENUE').aggregate(total=Sum('montant'))['total'] or Decimal(0)
        revenus = self.retenues_revenus.filter(type='REVENUE').aggregate(total=Sum('montant'))['total'] or Decimal(0)

        # Convertir les retenues et revenus en Decimal si nécessaire
        if isinstance(retenues, str):
            retenues = Decimal(retenues)
        if isinstance(revenus, str):
            revenus = Decimal(revenus)

        # Vérifiez les types avant le calcul
        print(f"base_cnss: {base_cnss} (type: {type(base_cnss)})")
        print(f"calcul_cnss: {calcul_cnss2} (type: {type(calcul_cnss2)})")
        print(f"uits_net: {uits_net} (type: {type(uits_net)})")
        print(f"retenues: {retenues} (type: {type(retenues)})")
        print(f"revenus: {revenus} (type: {type(revenus)})")

        # Calcul du salaire net
        salaire_net = base_cnss - calcul_cnss2 - Decimal(uits_net) - retenues + revenus
        
            # Calcul de l'effort de paie = 1% du salaire net
        effort_de_paie = salaire_net * Decimal('0.01')

        print(f"Salaire Net: {salaire_net}, Effort de Paie: {effort_de_paie}")

        return salaire_net, effort_de_paie





    

    # Fonction pour générer un matricule aléatoire
def generate_matricule(genre):
    # Génère un matricule aléatoire de 4 chiffres
    random_number = ''.join(random.choices(string.digits, k=4))
    
    # Ajoute un suffixe selon le genre
    if genre == 'M':  # Masculin
        suffix = 'X'
    elif genre == 'F':  # Féminin
        suffix = 'Y'
    else:
        suffix = ''  # Par défaut si le genre n'est pas défini ou autre

    return 'EMP' + random_number + suffix

# Signal pour générer automatiquement le matricule avant de sauvegarder un employé
@receiver(pre_save, sender=Employe)
def set_matricule(sender, instance, **kwargs):
    if not instance.matricule:  # Vérifie si le matricule n'est pas déjà défini
        instance.matricule = generate_matricule(instance.genre)  # Passe le genre pour générer le matricule
        


    
################################################################
class TypeConge(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    nombre_jours = models.PositiveIntegerField()

    def __str__(self):
        return self.nom

################################################################


################################################################


################################################################
class DemandeConges(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
    type_conge = models.ForeignKey(TypeConge, on_delete=models.CASCADE)  # Relation avec TypeConge
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    motif = models.TextField(null=True, blank=True)
    statut = models.CharField(max_length=20, default='En attente')
    date_approbation_chef = models.DateField(null=True, blank=True)
    date_approbation_drh = models.DateField(null=True, blank=True)
    date_demande = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Demande de congés de {self.employe} ({self.type_conge}) du {self.date_debut} au {self.date_fin}'


############################################################################



class Notification(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    message = models.TextField()
    vue = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.utilisateur.username} - {self.message[:20]}"
    
    
    ######################################################################

class Formation(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
    titre = models.CharField(max_length=255)
    description = models.TextField()
    statut = models.CharField(max_length=50, choices=[('en attente', 'En attente'), ('planifiée', 'Planifiée'), ('rejetée', 'Rejetée')])
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    heure_debut = models.TimeField(null=True, blank=True)
    heure_fin = models.TimeField(null=True, blank=True)
    formateur = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.titre} - {self.employe.nom} {self.employe.prenom}"
    
    
    ########################################################################
    

class Absence(models.Model):
    employe = models.ForeignKey('Employe', on_delete=models.CASCADE)
    date_debut = models.DateField()
    date_fin = models.DateField()
    motif = models.TextField()
    statut = models.CharField(max_length=20, choices=[('en attente', 'En attente'), ('approuvée', 'Approuvée'), ('refusée', 'Refusée')])

    def __str__(self):
        return f"Absence de {self.employe.nom} {self.employe.prenom} du {self.date_debut} au {self.date_fin}"

############################################################

class SondageSatisfaction(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
    score = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Note de 1 à 5
    commentaire = models.TextField(null=True, blank=True)  # Optionnel, commentaire de l'employé
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Satisfaction de {self.employe} - Score: {self.score}"