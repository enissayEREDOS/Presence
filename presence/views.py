from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta
from .models import Presence, SettingsHeures

from accueil.models import Utilisateur, Role
from employe.models import DemandeConges, Employe, Notification, Absence, Formation
# Create your views here.





def update_compteur(request):
    user_id = request.session.get('user_id')

    if not user_id:
        print("Utilisateur non authentifié")
        return redirect('login')

    try:
        employe = Utilisateur.objects.get(id=user_id).employe
    except Utilisateur.DoesNotExist:
        print(f"Utilisateur avec l'ID {user_id} non trouvé")
        return redirect('login')

    # Obtenir la date actuelle
    aujourd_hui = timezone.now().date()

    # Vérifier si une présence existe pour aujourd'hui
    presence = Presence.objects.filter(employe=employe, date=aujourd_hui).first()

    # Obtenir l'heure normale de début de travail
    settings_heures = SettingsHeures.objects.first()
    if not settings_heures:
        messages.error(request, "Les heures normales de travail ne sont pas définies. Veuillez contacter un administrateur.")
        print("Les paramètres d'heures de travail ne sont pas définis")
        return redirect('presence:update_compteur')

    heure_normale_arrivee = settings_heures.heure_arrivee_normale

    if not presence:
        # Si aucune présence n'existe pour aujourd'hui, créer une nouvelle entrée avec 8 heures (28800 secondes)
        heure_arrivee_actuelle = timezone.now()

        # Déterminer si l'employé est en retard
        retard = heure_arrivee_actuelle.time() > heure_normale_arrivee

        presence = Presence(
            employe=employe,
            heure_arrivee=heure_arrivee_actuelle.time(),
            retard=retard,
            temps_restant=timedelta(seconds=28800),
            compteur_actif=True,
            heure_derniere_action=timezone.now(),
            date=aujourd_hui
        )
        presence.save()
        
         #Indiquer que la présence a été enregistrée dans la session
        request.session['presence_enregistree'] = True
    else:
        # Mettre à jour le compteur si la présence existe déjà
        if presence.compteur_actif and presence.heure_derniere_action is not None:
            temps_ecoule = (timezone.now() - presence.heure_derniere_action).total_seconds()
            presence.temps_restant = max(timedelta(seconds=0), presence.temps_restant - timedelta(seconds=temps_ecoule))

        presence.heure_derniere_action = timezone.now()

        # Vérifier si l'employé est en retard à nouveau
        if presence.heure_arrivee > heure_normale_arrivee:
            presence.retard = True
        else:
            presence.retard = False

        presence.save()

    if request.method == 'POST':
        try:
            temps_restant = int(float(request.POST.get('temps_restant')))
        except (ValueError, TypeError):
            print("Erreur de conversion du temps restant")
            temps_restant = 0

        compteur_actif = request.POST.get('compteur_actif') == 'true'

        if presence:
            # Calculer le temps écoulé depuis la dernière action
            if presence.compteur_actif and compteur_actif:
                temps_ecoule = (timezone.now() - presence.heure_derniere_action).total_seconds()
                temps_restant -= int(temps_ecoule)

            # Mettre à jour les informations
            presence.temps_restant = timedelta(seconds=temps_restant)
            presence.compteur_actif = compteur_actif
            presence.heure_derniere_action = timezone.now()

            # Vérifier si l'employé est en retard à nouveau
            if presence.heure_arrivee > heure_normale_arrivee:
                presence.retard = True
            else:
                presence.retard = False

            presence.save()

        return redirect('presence:update_compteur')

    # Calculer le temps restant
    if presence.compteur_actif and presence.heure_derniere_action is not None:
        temps_ecoule = (timezone.now() - presence.heure_derniere_action).total_seconds()
        temps_restant = max(0, presence.temps_restant.total_seconds() - temps_ecoule)
    else:
        temps_restant = presence.temps_restant.total_seconds()

    context = {
        'temps_restant': temps_restant,
        'compteur_actif': presence.compteur_actif,
        'retard': presence.retard
    }
    return render(request, 'presence/marquer_presence.html', context)

########################################################################
def liste_presences(request):
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')
    user_id = request.session.get('user_id')
    
    utilisateur = Utilisateur.objects.get(id=user_id)
    profile_image = utilisateur.image.url if utilisateur.image else None
    # Récupérer tous les enregistrements de présences
    presences = Presence.objects.all()

    # Récupérer les filtres depuis la requête GET
    nom = request.GET.get('nom', '')
    date = request.GET.get('date', '')

    # Filtrer par nom
    if nom:
        presences = presences.filter(Q(employe__nom__icontains=nom) | Q(employe__prenom__icontains=nom))

    # Filtrer par date
    if date:
        presences = presences.filter(date=date)

    # Si le bouton "Aujourd'hui" est cliqué, afficher les présences du jour
    if 'aujourd_hui' in request.GET:
        aujourd_hui = timezone.now().date()
        presences = presences.filter(date=aujourd_hui)

    context = {
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom,
        'profile_image': profile_image,
        'presences': presences,
        'nom': nom,
        'date': date,
    }

    return render(request, 'presence/liste_presences.html', context)
##@@@@@@@@@@@@@@@@@@@@@@@@@@@#######################################