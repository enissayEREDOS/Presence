from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from .models import DemandeConges, Employe, Notification, Absence, Formation, SondageSatisfaction, Fonction, Departement
from .forms import DemandeCongesForm, FormationForm, AbsenceForm, PlanificationFormationForm, SondageSatisfactionForm
from .forms import EmployeForm, FonctionForm, DepartementForm
from accueil.models import Utilisateur, Role
from presence.models import Presence
from paiement.models import EmployeIndemnite
from presence.views import update_compteur

#######################################################################################


# Vue pour ajouter un département
def ajouter_departement(request):
    if request.method == 'POST':
        form = DepartementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employe:ajouter_departement')  # Redirige vers la liste des départements
    else:
        form = DepartementForm()

    return render(request, 'employe/ajouter_departement.html', {'form': form})

# Vue pour ajouter une fonction
def ajouter_fonction(request):
    if request.method == 'POST':
        form = FonctionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employe:ajouter_fonction')  # Redirige vers la liste des fonctions
    else:
        form = FonctionForm()

    return render(request, 'employe/ajouter_fonction.html', {'form': form})

#############################################################################################










# Vue pour ajouter un employé
def add_employe(request):
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')
    user_id = request.session.get('user_id')
    utilisateur = Utilisateur.objects.get(id=user_id)
    profile_image = utilisateur.image.url if utilisateur.image else None

    if request.method == 'POST':
        form = EmployeForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                mot_de_passe = get_random_string(length=8)
                employe = form.save(commit=False)
                employe.set_password(mot_de_passe)
                employe.role = Role.objects.get(nom='Employe')
                employe.save()

                send_mail(
                    'Votre compte a été créé',
                    f'Bonjour {employe.prenom},\n\nVotre compte a été créé avec succès. Voici vos informations de connexion :\n\nEmail : {employe.email}\nMot de passe : {mot_de_passe}\n\nVeuillez vous connecter desormais avec ses informations, ne partagez surtout pas votre mot de passe.',
                    'no-reply@votre-domaine.com',
                    [employe.email],
                    fail_silently=False,
                )
                return redirect('employe:employe_list')
            except Exception as e:
                form.add_error(None, f'Une erreur est survenue lors de l\'ajout de l\'employé : {str(e)}')
    else:
        form = EmployeForm()

    context = {
        'form': form,
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom,
        'profile_image': profile_image,
    }

    return render(request, 'employe/add_employe.html', context)







# Vue pour la liste des employés
def employe_list(request):
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')
    employes = Employe.objects.all()
    user_id = request.session.get('user_id')
    utilisateur = Utilisateur.objects.get(id=user_id)
    profile_image = utilisateur.image.url if utilisateur.image else None
    
    context = {
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom,
        'employes': employes,
        'profile_image': profile_image,
    }
    return render(request, 'employe/employe_list.html', context)

# Vue pour modifier un employé
def modifier_employe(request, employe_id):
    employe = get_object_or_404(Employe, pk=employe_id)
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')
    user_id = request.session.get('user_id')
    utilisateur = Utilisateur.objects.get(id=user_id)
    profile_image = utilisateur.image.url if utilisateur.image else None

    if request.method == 'POST':
        form = EmployeForm(request.POST, request.FILES, instance=employe)
        if form.is_valid():
            form.save()
            return redirect('employe:employe_list')  # Redirige vers la liste des employés après la modification
    else:
        form = EmployeForm(instance=employe)

    context = {
        'form': form,
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom,
        'profile_image': profile_image,
    }
    
    return render(request, 'employe/modifier_employe.html', context)

# Vue pour supprimer un employé
def supprimer_employe(request, employe_id):
    employe = get_object_or_404(Employe, pk=employe_id)

    if request.method == 'POST':
        employe.delete()
        return redirect('employe:employe_list')  # Redirige vers la liste des employés après la suppression

    context = {
        'employe': employe,
    }
    
    return render(request, 'employe/supprimer_employe.html', context)

from django.contrib import messages
from .models import SondageSatisfaction
from .forms import SondageSatisfactionForm

def portail_employe(request):
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')
    employes = Employe.objects.all()

    # Récupérer l'utilisateur actuellement connecté
    user_id = request.session.get('user_id')
    presence_enregistree = False  # Par défaut, la présence n'est pas enregistrée

    if user_id:
        try:
            utilisateur = Utilisateur.objects.get(id=user_id)
            employe = utilisateur.employe
            
            # Vérifier si une présence a été enregistrée pour aujourd'hui
            aujourd_hui = timezone.now().date()
            presence = Presence.objects.filter(employe=employe, date=aujourd_hui).exists()
            presence_enregistree = presence  # Mettre à jour l'état en fonction de la présence
            
            
            jours_conge_restant = employe.nbr_jours_conges_AN
            nom = employe.nom
            prenom = employe.prenom
            poste = employe.fonction
            departement = employe.departement
            
            # Récupérer l'URL de l'image de profil de l'utilisateur
            profile_image = utilisateur.image.url if utilisateur.image else None
            
            # Récupérer les notifications non lues pour cet utilisateur
            notifications = Notification.objects.filter(utilisateur_id=user_id, vue=False)
        except Utilisateur.DoesNotExist:
            jours_conge_restant = 0
            profile_image = None
            notifications = []
    else:
        jours_conge_restant = 0
        profile_image = None
        notifications = []

    # Formulaire de demande de congés
    form_conge = DemandeCongesForm()

    # Formulaire de sondage de satisfaction
    if request.method == 'POST':
        form_sondage = SondageSatisfactionForm(request.POST)
        if form_sondage.is_valid():
            satisfaction = form_sondage.save(commit=False)
            satisfaction.employe = employe  # Lier l'employé connecté au sondage
            satisfaction.save()
            messages.success(request, "Merci pour votre évaluation !")
            return redirect('employe:portail_employe')  # Rediriger après soumission
    else:
        form_sondage = SondageSatisfactionForm()  # Initialiser le formulaire de sondage

    context = {
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom,
        'employes': employes,
        'form_conge': form_conge,
        'form_sondage': form_sondage,  # Ajouter le formulaire de sondage au contexte
        'jours_conge_restant': jours_conge_restant,
        'nom': nom,
        'prenom': prenom,
        'poste': poste,
        'departement': departement,
        'profile_image': profile_image,
        'notifications': notifications,
        'presence_enregistree': presence_enregistree,
    }

    return render(request, 'employe/portail_employe.html', context)





def upload_photo(request):
    # Récupérer l'ID de l'utilisateur à partir de la session
    user_id = request.session.get('user_id')
    
    if not user_id:
        return HttpResponse("Utilisateur non authentifié", status=403)
    
    # Récupérer l'utilisateur en fonction de l'ID stocké dans la session
    utilisateur = get_object_or_404(Utilisateur, id=user_id)
    
    if request.method == 'POST':
        if 'image' in request.FILES:
            # Mettre à jour l'image de l'utilisateur
            utilisateur.image = request.FILES['image']
            utilisateur.save()
            return redirect('employe:portail_employe')
        else:
            return HttpResponse("Aucun fichier image reçu")
    
    return render(request, 'employe/portail_employe.html', {'utilisateur': utilisateur})


###############################

def upload_chef(request):
    # Récupérer l'ID de l'utilisateur à partir de la session
    user_id = request.session.get('user_id')
    
    if not user_id:
        return HttpResponse("Utilisateur non authentifié", status=403)
    
    # Récupérer l'utilisateur en fonction de l'ID stocké dans la session
    utilisateur = get_object_or_404(Utilisateur, id=user_id)
    
    if request.method == 'POST':
        if 'image' in request.FILES:
            # Mettre à jour l'image de l'utilisateur
            utilisateur.image = request.FILES['image']
            utilisateur.save()
            return redirect('employe:portail_chef_de_departement')
        else:
            return HttpResponse("Aucun fichier image reçu")
    
    return render(request, 'employe/portail_chef_de_departement.html', {'utilisateur': utilisateur})

########################################

def upload_drh(request):
    # Récupérer l'ID de l'utilisateur à partir de la session
    user_id = request.session.get('user_id')
    
    if not user_id:
        return HttpResponse("Utilisateur non authentifié", status=403)
    
    # Récupérer l'utilisateur en fonction de l'ID stocké dans la session
    utilisateur = get_object_or_404(Utilisateur, id=user_id)
    
    if request.method == 'POST':
        if 'image' in request.FILES:
            # Mettre à jour l'image de l'utilisateur
            utilisateur.image = request.FILES['image']
            utilisateur.save()
            return redirect('employe:portail_drh')
        else:
            return HttpResponse("Aucun fichier image reçu")
    
    return render(request, 'employe/portail_DRH.html', {'utilisateur': utilisateur})

####################################################

# Dans la vue
def faire_demande_conges(request):
    if request.method == 'POST':
        form = DemandeCongesForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            user_id = request.session.get('user_id')  # Récupérer l'ID de l'utilisateur depuis la session
            
            if user_id:
                try:
                    utilisateur = Utilisateur.objects.get(id=user_id)
                    employe = utilisateur.employe  # Récupérer l'employé lié à l'utilisateur

                    # Récupérer le type de congé sélectionné
                    type_conge = form.cleaned_data['type_conge']
                    
                    # Calcul de la date de fin en fonction du type de congé et de la date de début
                    date_debut = form.cleaned_data['date_debut']
                    nombre_jours = type_conge.nombre_jours
                    
                    # Calculer la date de fin (en excluant les week-ends si nécessaire)
                    demande.date_fin = date_debut + timedelta(days=nombre_jours - 1)

                    # Attribuer l'employé à la demande
                    demande.employe = employe
                    demande.save()

                    # Envoyer une notification au chef de département
                    chef = Utilisateur.objects.filter(role__nom='Chef de departement').first()
                    if chef:
                        Notification.objects.create(
                            utilisateur=chef,
                            message=f"Vous avez une nouvelle demande de congés de {employe.nom} {employe.prenom}."
                        )
                    
                    return redirect('employe:portail_employe')
                except Utilisateur.DoesNotExist:
                    messages.error(request, "Utilisateur non trouvé.")
            else:
                messages.error(request, "Utilisateur non authentifié.")
        else:
            messages.error(request, "Il y a eu une erreur dans la soumission du formulaire.")
    else:
        form = DemandeCongesForm()
        jours_conge_restant = 0  # Valeur par défaut au chargement du formulaire
        if request.session.get('user_id'):
            try:
                utilisateur = Utilisateur.objects.get(id=request.session.get('user_id'))
                jours_conge_restant = utilisateur.employe.nbr_jours_conges_AN
            except Utilisateur.DoesNotExist:
                pass
    
    context = {
        'form': form,
        'jours_conge_restant': jours_conge_restant,
    }
    
    return render(request, 'employe/portail_employe.html', context)






def portail_chef_de_departement(request):
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')
    employes = Employe.objects.all()
    demandes_en_attentes = DemandeConges.objects.filter(statut='En attente')
    
    
    user_id = request.session.get('user_id')
    
    if user_id:
        try:
            utilisateur = Utilisateur.objects.get(id=user_id)
            
            # Récupérer l'URL de l'image de profil de l'utilisateur
            profile_image = utilisateur.image.url if utilisateur.image else None
            
            # Récupérer les notifications non lues pour cet utilisateur
            notifications = Notification.objects.filter(utilisateur_id=user_id, vue=False)
        except Utilisateur.DoesNotExist:
            
            profile_image = None
            notifications = []
    else:
        profile_image = None
        notifications = []
    
    context = {
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom,
        'employes': employes,
        'demandes': demandes_en_attentes,
         'profile_image': profile_image,
    }
    
    return render(request, 'employe/portail_chef_de_departement.html', context)

############################################################
from .forms import TypeCongeForm

def creer_type_conge(request):
    if request.method == 'POST':
        form = TypeCongeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employe:creer_type_conge')  # Redirection après enregistrement
    else:
        form = TypeCongeForm()
    return render(request, 'employe/creer_type_conge.html', {'form': form})
##################################################

##########################fonction pour accepter et refuser une demande chef de departement##################
def accepter_demande(request, demande_id):
    demande = get_object_or_404(DemandeConges, id=demande_id)
    demande.statut = 'Validée'
    demande.date_approbation_chef = timezone.now()
    demande.save()

    # Envoyer une notification au DRH
    drh = Utilisateur.objects.filter(role__nom='DRH').first()
    if drh:
        Notification.objects.create(
            utilisateur=drh,
            message=f"La demande de congé de {demande.employe.prenom} {demande.employe.nom} a été validée par le Chef de département."
        )
    
    messages.success(request, "Demande acceptée et notification envoyée au DRH.")
    return redirect('employe:portail_chef_de_departement')

def rejeter_demande(request, demande_id):
    demande = get_object_or_404(DemandeConges, id=demande_id)
    demande.statut = 'Rejetée'
    demande.save()

    # Envoyer une notification à l'employé
    Notification.objects.create(
        utilisateur=demande.employe,
        message=f"Votre demande de congé a été rejetée par le Chef de département."
    )
    
    messages.success(request, "Demande rejetée et notification envoyée à l'employé.")
    return redirect('employe:portail_chef_de_departement')









################################fonction pour les notifications##################################3

def envoyer_notification(utilisateur, message):
    Notification.objects.create(utilisateur=utilisateur, message=message, vue=False)
    


def notifications_page(request):
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')
    user_id = request.session.get('user_id')
    
    if user_id:
        utilisateur = Utilisateur.objects.get(id=user_id)
        profile_image = utilisateur.image.url if utilisateur.image else None
        
        # Récupérer les notifications triées par ordre décroissant de date (plus récentes en haut)
        notifications = Notification.objects.filter(utilisateur_id=user_id).order_by('-date_creation')
        
        if request.method == 'POST':
            notification_id = request.POST.get('notification_id')
            notification = Notification.objects.get(id=notification_id, utilisateur_id=user_id)
            if notification:
                notification.vue = True
                notification.save()
        
        context = {
            'formations_planifiees': formations_planifiees,
            'role': role,
            'utilisateur_nom': utilisateur_nom,
            'utilisateur_prenom': utilisateur_prenom,
            'profile_image': profile_image,
            'notifications': notifications,
        }

        return render(request, 'employe/notifications.html', context)
    else:
        return redirect('accueil:login')



#################################fonction pour accepter et refuser une demande DRH#################################
def portail_drh(request):
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')
    formations = Formation.objects.filter(statut='en attente')  # Récupérer  les absences en attente
    
    
    user_id = request.session.get('user_id')
    
    if user_id:
        try:
            utilisateur = Utilisateur.objects.get(id=user_id)
            
            # Récupérer l'URL de l'image de profil de l'utilisateur
            profile_image = utilisateur.image.url if utilisateur.image else None
            
            # Récupérer les notifications non lues pour cet utilisateur
            notifications = Notification.objects.filter(utilisateur_id=user_id, vue=False)
        except Utilisateur.DoesNotExist:
            
            profile_image = None
            notifications = []
    else:
        profile_image = None
        notifications = []
    
    if request.method == 'POST':
        form = PlanificationFormationForm(request.POST)
        if form.is_valid():
            form.save()  # Enregistrer la formation dans la base de données
            return redirect('employe:portail_drh')  # Redirection après la soumission
    else:
        form = PlanificationFormationForm()  # Formulaire vide pour un GET
    
    # Récupération des demandes validées
    demandes_validees = DemandeConges.objects.filter(statut='Validée')
    
    # Vérifiez le contenu de demandes_validees
    print("Demandes validées : ", demandes_validees)
    
    context = {
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom,
        'demandes': demandes_validees,
        'profile_image': profile_image,
        'formations': formations,
        'form': form
    }
    
    return render(request, 'employe/portail_drh.html', context)




def accepter_demande_DRH(request, demande_id):
    demande = get_object_or_404(DemandeConges, id=demande_id)
    demande.date_approbation_drh = timezone.now()
    demande.statut = 'confirmée'
    demande.save()

        # Créer une notification pour l'employé
    Notification.objects.create(
        utilisateur=demande.employe,
        message=f"Votre demande de congé du {demande.date_debut} au {demande.date_fin} a été acceptée.",
        vue=False
    )

    messages.success(request, "La demande de congé a été acceptée.")
    return redirect('employe:portail_drh')


def rejeter_demande_DRH(request, demande_id):
    demande = get_object_or_404(DemandeConges, id=demande_id)
    demande.date_approbation_drh = timezone.now()
    demande.statut = 'refusée'
    demande.save()

    # Créer une notification pour l'employé
    Notification.objects.create(
        utilisateur=demande.employe,
        message=f"Votre demande de congé du {demande.date_debut} au {demande.date_fin} a été refusée.",
        vue=False
    )

    messages.error(request, "La demande de congé a été refusée.")
    return redirect('employe:portail_drh')
#########################################################################################################
def liste_demandes_confirmees(request):
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')
    user_id = request.session.get('user_id')
    utilisateur = Utilisateur.objects.get(id=user_id)
    
    profile_image = utilisateur.image.url if utilisateur.image else None
    # Récupérer toutes les demandes ayant le statut 'confirmée'
    demandes_confirmees = DemandeConges.objects.filter(statut='confirmée')
    
    context = {
        'demandes_confirmees': demandes_confirmees,
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom,
        'profile_image': profile_image,
    }
    return render(request, 'employe/liste_demandes_confirmees.html', context)
#########################################################################################################

#########################################################################################################

def demander_formation(request):
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')
    if request.method == 'POST':
        form = FormationForm(request.POST)
        if form.is_valid():
            formation = form.save(commit=False)
            user_id = request.session.get('user_id')
            if user_id:
                try:
                    utilisateur = Utilisateur.objects.get(id=user_id)
                    employe = utilisateur.employe  # Récupérer l'employé lié à l'utilisateur
                    
                    # Attribuer l'employé à la demande
                    formation.employe = employe
                    formation.statut = 'en attente'
                    formation.save()
                    # Envoyer une notification au chef de département
                    drh = Utilisateur.objects.filter(role__nom='DRH').first()
                    if drh:
                        Notification.objects.create(
                            utilisateur=drh,
                            message=f"Vous avez une nouvelle demande de Formation provenant de l'employé {employe.nom} {employe.prenom}."
                        )
                    
                    return redirect('employe:portail_employe')  # Rediriger vers une page de succès ou tableau de bord
                except Utilisateur.DoesNotExist:
                    messages.error(request, "Utilisateur non trouvé.")
            else:
                messages.error(request, "Utilisateur non authentifié.")
        else:
            messages.error(request, "Il y a eu une erreur dans la soumission du formulaire.")
    else:
                form = FormationForm()
                
    context={
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom,
        'form': form,
    }

    return render(request, 'employe/demander_formation.html', context)



def signaler_absence(request):
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')
    if request.method == 'POST':
        form = AbsenceForm(request.POST)
        if form.is_valid():
            absence = form.save(commit=False)
            user_id = request.session.get('user_id')
            if user_id:
                try:
                    utilisateur = Utilisateur.objects.get(id=user_id)
                    employe = utilisateur.employe  # Récupérer l'employé lié à l'utilisateur
                    
                    # Attribuer l'employé à la demande
                    absence.employe = employe
                    absence.statut = 'envoyé'
                    absence.save()
                    # Envoyer une notification au chef de département
                    chef = Utilisateur.objects.filter(role__nom='Chef de departement').first()
                    if chef:
                        Notification.objects.create(
                            utilisateur=chef,
                            message=f"{employe.nom} {employe.prenom} vous signal son absence du {absence.date_debut} au {absence.date_fin} ."
                        )
                    
                    return redirect('employe:portail_employe')  # Rediriger vers une page de succès ou tableau de bord
                except Utilisateur.DoesNotExist:
                    messages.error(request, "Utilisateur non trouvé.")
            else:
                messages.error(request, "Utilisateur non authentifié.")
        else:
            messages.error(request, "Il y a eu une erreur dans la soumission du formulaire.")
    else:
        form = AbsenceForm()
        
    context={
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom,
        'form': form,
    }

    return render(request, 'employe/signaler_absence.html', context)

#############################################################################
def liste_absences(request):
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')
    absences = Absence.objects.all()  # Récupérer toutes les absences
    user_id = request.session.get('user_id')
    
    utilisateur = Utilisateur.objects.get(id=user_id)
    profile_image = utilisateur.image.url if utilisateur.image else None
    
    context={
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom,
        'absences': absences,
        'profile_image': profile_image,
    }
    return render(request, 'employe/liste_absences.html', context)

#############################################################################

def planifier_formation(request, formation_id):
    formation = get_object_or_404(Formation, id=formation_id)

    if request.method == 'POST':
        form = PlanificationFormationForm(request.POST, instance=formation)
        if form.is_valid():
            formation.statut = 'planifiée'
            form.save()
            # Ajouter ici la logique de notification si nécessaire
            return redirect('employe:portail_drh')
    else:
        form = PlanificationFormationForm(instance=formation)

    return render(request, 'employe/portail_drh.html', {'form': form, 'formation': formation})


#############################################################################

def rejeter_formation(request, formation_id):
    formation = get_object_or_404(Formation, id=formation_id)
    formation.statut = 'rejetée'
    formation.save()
    # Ajouter ici la logique de notification si nécessaire
    return redirect('employe:portail_drh')

#############################################################################
def formations_planifiees(request):
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')
    # Récupérer les formations avec le statut 'planifiée'
    formations_planifiees = Formation.objects.filter(statut='planifiée')
    user_id = request.session.get('user_id')
    
    utilisateur = Utilisateur.objects.get(id=user_id)
    profile_image = utilisateur.image.url if utilisateur.image else None
    
    context = {
        'formations_planifiees': formations_planifiees,
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom,
        'profile_image': profile_image,
    }
    
    return render(request, 'employe/formations_planifiees.html', context)
#############################################################################
def soumettre_satisfaction(request):
    try:
        utilisateur = request.user  # Utilisateur connecté
        employe = utilisateur.employe  # Assurez-vous que l'utilisateur est lié à un employé
    except AttributeError:
        messages.error(request, "Aucun employé n'est associé à cet utilisateur.")
        return redirect('tableau_de_bord')

    if request.method == 'POST':
        form = SondageSatisfactionForm(request.POST)
        if form.is_valid():
            satisfaction = form.save(commit=False)
            satisfaction.employe = employe  # Associe l'employé à la satisfaction
            satisfaction.save()
            messages.success(request, "Merci pour votre évaluation !")
            return redirect('tableau_de_bord')  # Redirection vers la page du tableau de bord ou autre
    else:
        form = SondageSatisfactionForm()

    return render(request, 'sondage/soumettre_satisfaction.html', {'form': form})
#############################################################################
def liste_employes(request):
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')
    employes = Employe.objects.all()  # Récupère tous les employés
    user_id = request.session.get('user_id')
    
    utilisateur = Utilisateur.objects.get(id=user_id)
    profile_image = utilisateur.image.url if utilisateur.image else None
    
    context = {
        'formations_planifiees': formations_planifiees,
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom,
        'employes': employes,
        'profile_image': profile_image,
    }
    
    return render(request, 'employe/salarier.html', context)



def ajouter_element(request, id):
    employe = get_object_or_404(Employe, id=id)

    if request.method == 'POST':
        sursalaire = request.POST.get('sursalaire', 0)
        prime_anciennete = request.POST.get('prime_anciennete', 0)
        
        employe.sursalaire = sursalaire
        employe.prime_anciennete = prime_anciennete
        employe.save()

        return redirect('employe:liste_employes')  # Redirection après mise à jour

    return render(request, 'employe/salarier.html', {'employe': employe})
#############################################################################

from django.shortcuts import get_object_or_404, render

def afficher_salaire_brut_imposable(request, employe_id):
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')
    user_id = request.session.get('user_id')
    utilisateur = Utilisateur.objects.get(id=user_id)
    profile_image = utilisateur.image.url if utilisateur.image else None
    # Récupérer l'employé par son ID
    employe = get_object_or_404(Employe, id=employe_id)

    employe_indemnites = EmployeIndemnite.objects.filter(employe_id=employe_id)
    employe_avantages = employe.avantages_en_nature.all()  # Récupère les avantages en nature
    retenues_revenus = employe.retenues_revenus.all()  # Récupère les retenues et revenus

    # Calcul des totaux
    total_gains = employe.salaire_base + employe.sursalaire + employe.prime_anciennete

    for indemnite in employe_indemnites:
        total_gains += indemnite.somme_percue  # ou la logique appropriée


    # Ajouter uniquement les revenus de type "revenu" au total des gains
    total_revenus = sum(retenue.montant for retenue in retenues_revenus if retenue.type == 'REVENUE')  # Filtrer par type
    total_gains += total_revenus  # Inclure les revenus dans le total des gains

    # Calculer le total des retenues
    total_retenues = sum(retenue.montant for retenue in retenues_revenus if retenue.type == 'RETENUE')  # Somme des montants des retenues de type "retenue"
    
    # Ajouter les autres éléments au total des retenues
    uits_net = Decimal(employe.calculer_uits_net())  # Convertir en Decimal
    effort_de_paie = int(employe.calculer_salaire_net()[1])  # Convertir en Decimal
    calcul_cnss2 = Decimal(employe.calculer_cnss2())  # Convertir en Decimal

    total_retenues += int(uits_net + effort_de_paie + calcul_cnss2)  # Totaliser les retenues

    base_cnss = employe.calculer_base_cnss()
    
    compteur = 1

    # Calculer le salaire brut imposable
    salaire_brut_imposable = employe.calculer_salaire_brut_imposable()

    # Calculer les exonérations totales
    total_exonerations = employe.calculer_exonerations()

    # Abattement frais et charges
    abattement = employe.calculer_abattement_frais_charges()
    # Salaire net imposable
    salaire_net_imposable = employe.calculer_salaire_net_imposable()
    # Base UITS arrondie
    base_uits_arrondie = employe.calculer_base_uits_arrondie()
    # UITS brut
    uits_brut = employe.calculer_uits_brut()
    # Abattement UITS
    abattement_uits = employe.calculer_abattement_uits()
    # UITS net
    uits_net = employe.calculer_uits_net()
    # Salaire net
    salaire_net, _ = employe.calculer_salaire_net()
    
    net_a_payer = int(salaire_net - effort_de_paie)

    # Passer le salaire à la template
    context = {
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom,
        'profile_image': profile_image,
        'employe': employe,
        'total_exonerations': total_exonerations,  # Ajouter les exonérations au contexte
        'salaire_brut_imposable': salaire_brut_imposable,
        'abattement': abattement,
        'salaire_net_imposable': salaire_net_imposable,
        'base_uits_arrondie': base_uits_arrondie,
        'uits_brut': uits_brut,
        'abattement_uits': abattement_uits,
        'uits_net': uits_net,
        'salaire_net': salaire_net,
        'effort_de_paie': effort_de_paie,
        'base_cnss': base_cnss,
        'calcul_cnss2': calcul_cnss2,
        'compteur': compteur,
        'net_a_payer': net_a_payer,
        'employe_indemnites': employe_indemnites,
        'employe_avantages': employe_avantages,  # Passe les avantages en nature dans le contexte
        'retenues_revenus': retenues_revenus,  # Passe les retenues et revenus dans le contexte
        'total_gains': total_gains,  # Ajout des totaux des gains au contexte
        'total_retenues': total_retenues,  # Ajout des totaux des retenues au contexte
        'date_actuelle': datetime.now(), 
    }
    return render(request, 'employe/salaire_brut_imposable.html', context)





################################