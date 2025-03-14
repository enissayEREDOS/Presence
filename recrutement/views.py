from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta

from accueil.models import Utilisateur, Role
from employe.models import DemandeConges, Employe, Notification, Absence, Formation

from .forms import ConnexionForm, CreationCompteForm, CandidatForm,PosteForm
from .models import Candidat, Poste

# Create your views here.

def connexion_view(request):
    next_url = request.GET.get('next', 'recrutement:afficher_postes')  # Utiliser 'home' ou une URL valide par défaut
    poste_id = request.GET.get('poste_id')  # Récupère l'ID du poste depuis les paramètres GET

    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            mot_de_passe = form.cleaned_data['mot_de_passe']
            try:
                candidat = Candidat.objects.get(email=email)
                if candidat.check_password(mot_de_passe):
                    request.session['candidat_id'] = candidat.id
                    # Rediriger vers la page de candidature si `poste_id` est fourni
                    if poste_id:
                        return redirect('recrutement:postuler', poste_id=poste_id)
                    else:
                        return redirect(next_url)  # Rediriger vers l'URL passée dans 'next'
                else:
                    form.add_error(None, "Identifiants invalides.")
            except Candidat.DoesNotExist:
                form.add_error(None, "Identifiants invalides.")
    else:
        form = ConnexionForm()

    return render(request, 'recrutement/connexion.html', {'form': form})




def creation_compte_view(request):
    if request.method == 'POST':
        form = CreationCompteForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if Candidat.objects.filter(email=email).exists():
                form.add_error('email', "Un compte avec cet e-mail existe déjà.")
            else:
                candidat = form.save(commit=False)
                candidat.set_password(form.cleaned_data['mot_de_passe'])
                candidat.save()
                return redirect('recrutement:connexion')  # Rediriger vers la page de connexion
    else:
        form = CreationCompteForm()

    return render(request, 'recrutement/creation-compte.html', {'form': form})


def postuler_view(request, poste_id):
    if 'candidat_id' not in request.session:
        return redirect('recrutement:connexion', poste_id=poste_id)  # Passer `poste_id` à la page de connexion

    poste = get_object_or_404(Poste, id=poste_id)
    candidat = get_object_or_404(Candidat, id=request.session['candidat_id'])
    
    # Vérifier si le candidat a déjà postulé
    if candidat.poste == poste:
        messages.info(request, "Vous avez déjà postulé à ce poste.")
        return redirect('recrutement:afficher_postes')
    
    if request.method == 'POST':
        form = CandidatForm(request.POST, request.FILES)
        if form.is_valid():
            candidat.cv = form.cleaned_data['cv']
            candidat.lettre_motivation = form.cleaned_data['lettre_motivation']
            candidat.poste = poste
            candidat.date_candidature = timezone.now().date()  # Définir la date de candidature
            candidat.etape_processus = 'Candidature reçue'  # Mettre à jour l'étape du processus
            candidat.save()
            return redirect('recrutement:confirmation')  # Rediriger vers une page de confirmation
    else:
        form = CandidatForm()

    return render(request, 'recrutement/postulation.html', {'form': form, 'poste': poste})






def ajouter_poste_view(request):
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')
    user_id = request.session.get('user_id')
    
    utilisateur = Utilisateur.objects.get(id=user_id)
    profile_image = utilisateur.image.url if utilisateur.image else None
    if request.method == 'POST':
        form = PosteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('recrutement:ajouter_poste')  # Redirige vers la liste des postes après l'ajout
    else:
        form = PosteForm()
    postes = Poste.objects.all()

    return render(request, 'recrutement/ajouter_poste.html', {'form': form,
        'postes': postes,
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom,
        'profile_image': profile_image,
        })




def modifier_poste_view(request, poste_id):
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')
    user_id = request.session.get('user_id')
    
    utilisateur = Utilisateur.objects.get(id=user_id)
    profile_image = utilisateur.image.url if utilisateur.image else None
    poste = get_object_or_404(Poste, id=poste_id)
    if request.method == 'POST':
        form = PosteForm(request.POST, instance=poste)
        if form.is_valid():
            form.save()
            return redirect('recrutement:ajouter_poste')  # Redirige vers la liste des postes après la modification
    else:
        form = PosteForm(instance=poste)

    return render(request, 'recrutement/modifier_poste.html', {'form': form,
        'poste': poste,
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom,
        'profile_image': profile_image,
                                                               })



def afficher_postes_view(request):
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')
    user_id = request.session.get('user_id')
    
    utilisateur = Utilisateur.objects.get(id=user_id)
    profile_image = utilisateur.image.url if utilisateur.image else None
    postes = Poste.objects.all()  # Récupérer tous les postes
    return render(request, 'recrutement/afficher_postes.html', {'postes': postes,
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom,
        'profile_image': profile_image,               
                                                                })




def confirmation_view(request):
    return render(request, 'recrutement/confirmation.html')



def liste_candidats_poste(request, poste_id):
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')
    user_id = request.session.get('user_id')

    utilisateur = Utilisateur.objects.get(id=user_id)
    profile_image = utilisateur.image.url if utilisateur.image else None
    
    # Récupérer le poste correspondant à l'ID
    poste = get_object_or_404(Poste, id=poste_id)
    
    # Récupérer les candidats avec 'Candidature reçue'
    candidats_recus = Candidat.objects.filter(poste=poste, etape_processus='Candidature reçue')
    
    # Récupérer les candidats avec 'Entretien'
    candidats_entretien = Candidat.objects.filter(poste=poste, etape_processus='Entretien')

    # Rendre le template avec la liste des deux groupes de candidats
    return render(request, 'recrutement/liste_candidats.html', {
        'poste': poste,
        'candidats_recus': candidats_recus,
        'candidats_entretien': candidats_entretien,
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom,
        'profile_image': profile_image,
    })


    
    
    
    
    
###########################################################################
def rejeter_candidat(request, candidat_id):
    candidat = get_object_or_404(Candidat, id=candidat_id)
    candidat.etape_processus = 'Rejeté'
    candidat.save()

    # Envoyer un email au candidat
    subject = "Votre candidature a été rejetée"
    message = f"Bonjour {candidat.prenom} {candidat.nom},\n\nNous regrettons de vous informer que votre candidature pour le poste de {candidat.poste.titre} a été rejetée.\n\nMerci de votre intérêt."
    send_mail(subject, message, 'no-reply@B2BRH.com', [candidat.email], fail_silently=False)

    messages.success(request, f"Le candidat {candidat.prenom} {candidat.nom} a été rejeté.")
    return redirect('recrutement:liste_candidats_poste', poste_id=candidat.poste.id)

############################################################################

def planifier_entretien(request, candidat_id):
    candidat = get_object_or_404(Candidat, id=candidat_id)
    
    if request.method == 'POST':
        entretien_date = request.POST.get('entretien_date')
        entretien_heure = request.POST.get('entretien_heure')
        
        # Combiner la date et l'heure en un seul champ DateTime
        if entretien_date and entretien_heure:
            entretien_datetime = f"{entretien_date} {entretien_heure}"
            candidat.entretien_date = entretien_datetime
            candidat.entretien_heure = entretien_heure
            candidat.etape_processus = 'Entretien'
            candidat.save()

            # Envoyer un email au candidat pour l'informer de l'entretien
            subject = "Entretien planifié"
            message = f"Bonjour {candidat.prenom} {candidat.nom},\n\nVotre entretien pour le poste de {candidat.poste.titre} a été planifié pour le {entretien_date} à {entretien_heure}.\n\nMerci de confirmer votre disponibilité."
            send_mail(subject, message, 'no-reply@B2BRH.com', [candidat.email], fail_silently=False)

            messages.success(request, f"Entretien planifié pour {candidat.prenom} {candidat.nom}.")
            return redirect('recrutement:liste_candidats_poste', poste_id=candidat.poste.id)
    
    return render(request, 'recrutement/planifier_entretien.html', {'candidat': candidat})




def offrir_emploi(request, candidat_id):
    candidat = get_object_or_404(Candidat, id=candidat_id)

    # Vérifier que le candidat est à l'étape d'entretien
    if candidat.etape_processus == 'Entretien':
        # Mettre à jour l'étape du processus pour passer à "Offre d'emploi"
        candidat.etape_processus = 'Offre d\'emploi'
        candidat.save()

        # Envoyer un email au candidat pour l'informer de l'offre d'emploi
        subject = "Offre d'emploi de B2BRH"
        message = (
            f"Bonjour {candidat.prenom} {candidat.nom},\n\n"
            f"Félicitations ! Vous avez reçu une offre d'emploi pour le poste de {candidat.poste.titre}.\n\n"
            "Nous vous invitons à vous présenter à l'entreprise pour finaliser votre dossier.\n"
            "Merci de préparer les documents suivants :\n"
            "- Votre CV\n"
            "- Lettre de motivation\n"
            "- Copies de vos diplômes\n"
            "- Toute autre documentation pertinente\n\n"
            "Nous sommes impatients de vous accueillir dans notre équipe.\n\n"
            "Cordialement,\n"
            "L'équipe de B2BRH"
        )
        
        send_mail(subject, message, 'no-reply@B2BRH.com', [candidat.email], fail_silently=False)

        messages.success(request, 'L\'offre d\'emploi a été faite avec succès, et un email a été envoyé au candidat.')
    
    return redirect('recrutement:liste_candidats_poste', poste_id=candidat.poste.id)

