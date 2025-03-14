from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib import messages
from .models import Utilisateur
from .forms import UtilisateurCreationForm, UtilisateurEditForm, LoginForm, RoleForm
from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
from datetime import datetime, timedelta
from .models import Role
from django.contrib.auth.decorators import login_required
from .models import Utilisateur
from employe.models import Employe, DemandeConges, SondageSatisfaction
from django.db.models import Avg, F
from recrutement.models import Candidat
from django.contrib.auth import logout


from django.db.models import Count
from django.http import JsonResponse

def tableau_de_bord(request):
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')

    # Récupérer les statistiques générales
    nombre_utilisateurs = Utilisateur.objects.count()
    nombre_demandes_conges = DemandeConges.objects.count()
    nombre_employes = Employe.objects.count()
    nombre_roles = Role.objects.count()  # Total des rôles

    # Calcul des KPI
    scores_satisfaction = SondageSatisfaction.objects.values_list('score', flat=True)
    taux_satisfaction = sum(scores_satisfaction) / len(scores_satisfaction) * 20 if scores_satisfaction else 0
    taux_demande_conge = (nombre_demandes_conges / nombre_employes) * 100 if nombre_employes > 0 else 0

    delai_moyen_traitement = DemandeConges.objects.annotate(
        delai=F('date_approbation_drh') - F('date_demande')
    ).aggregate(moyen=Avg('delai'))['moyen'] or 0

    # Récupérer la répartition des rôles
    repartition_roles = (
        Utilisateur.objects.values('role__nom')
        .annotate(nombre=Count('role'))
        .order_by('-nombre')
    )

    # Préparer les données des rôles pour Chart.js
    labels_roles = [r['role__nom'] for r in repartition_roles]
    data_roles = [r['nombre'] for r in repartition_roles]
    
    # Récupérer la répartition des types de congés
    repartition_types_conges = (
        DemandeConges.objects.values('type_conge__nom')
        .annotate(nombre=Count('type_conge'))
        .order_by('-nombre')
    )
    labels_types_conges = [tc['type_conge__nom'] for tc in repartition_types_conges]
    data_types_conges = [tc['nombre'] for tc in repartition_types_conges]
    
    
    
    

    context = {
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom,
        'nombre_utilisateurs': nombre_utilisateurs,
        'nombre_demandes_conges': nombre_demandes_conges,
        'taux_satisfaction': taux_satisfaction,
        'taux_demande_conge': taux_demande_conge,
        'nombre_roles': nombre_roles,
        'delai_moyen_traitement': delai_moyen_traitement.days if isinstance(delai_moyen_traitement, timedelta) else delai_moyen_traitement,
        'labels_roles': labels_roles,  # Transmettre les noms des rôles
        'data_roles': data_roles,      # Transmettre les données de chaque rôle
        'labels_types_conges': labels_types_conges,  # Transmettre les noms des types de congés
        'data_types_conges': data_types_conges,      # Transmettre les données des types de congés
    }
    
    return render(request, 'accueil/br.html', context)






def index(request):
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')

    context = {
        
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom
    }
    return render(request, 'accueil/index.html', context)





# views.py


def register(request):
    # Récupérer les informations utilisateur depuis la session
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')

    roles = Role.objects.all()  # Tous les rôles doivent être récupérés
    utilisateurs = Utilisateur.objects.all()  # Récupération des utilisateurs
    if request.method == 'POST':
        form = UtilisateurCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Compte créé avec succès !')
            return redirect('accueil:register')
    else:
        form = UtilisateurCreationForm()

    # Récupérer les utilisateurs existants
    utilisateurs = Utilisateur.objects.all()
    
    context = {
        'form': form,
        'utilisateurs': utilisateurs,
        'roles': roles,  # Envoi des rôles au template
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom
    }
    
    return render(request, 'accueil/register.html', context)


    
def edit_user(request, user_id):
    utilisateur = get_object_or_404(Utilisateur, id=user_id)
    roles = Role.objects.all()
    if request.method == 'POST':
        form = UtilisateurEditForm(request.POST, instance=utilisateur)
        if form.is_valid():
            form.save()
            messages.success(request, "L'utilisateur a été modifié avec succès.")
            return redirect('accueil:register')
        else:
            messages.error(request, "Une erreur s'est produite lors de la modification de l'utilisateur.")
    else:
        form = UtilisateurEditForm(instance=utilisateur)
        
    

    return render(request, 'accueil/register.html', {
        'utilisateurs': Utilisateur.objects.all(),
        'roles': roles,
        'form': form,
        'utilisateur': utilisateur
    })







def delete_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        utilisateur = get_object_or_404(Utilisateur, id=user_id)
        utilisateur.delete()
        messages.success(request, 'L\'utilisateur a été supprimé avec succès.')
        return redirect('accueil:register')  # Replace with your actual URL name
    
    


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            mot_de_passe = form.cleaned_data['mot_de_passe']
            utilisateur = Utilisateur.objects.filter(email=email).first()
            if utilisateur and utilisateur.check_password(mot_de_passe):
                # Authentification réussie
                auth_login(request, utilisateur)
                
                # Stocker des informations utilisateur dans la session
                request.session['user_id'] = utilisateur.id
                request.session['user_role'] = utilisateur.role.nom
                request.session['user_nom'] = utilisateur.nom
                request.session['user_prenom'] = utilisateur.prenom
                request.session['user_permissions'] = list(utilisateur.role.permissions.values_list('code', flat=True))

                # Dictionnaire de permissions et redirections
                permission_redirects = {
                    'Tableau de bord': 'accueil:tableau_de_bord',
                    'Portail DRH': 'employe:portail_drh',
                    'Portail CD': 'employe:portail_chef_de_departement',
                    'Portail employé': 'employe:portail_employe',
                    'utilisateur': 'accueil:add_role',
                    'Calendrier': 'accueil:calendar',
                    'employe': 'employe:employe_list',
                    'Présence': 'presence:liste_presences',
                    'Absences': 'employe:liste_absences',
                    'Congés': 'employe:liste_demandes_confirmees',
                    'Formation': 'employe:formations_planifiees',
                    'Recrutement': 'recrutement:ajouter_poste',
                    'Paie': 'paie:index',
                    'Données': 'entreprise:donnees_entreprise',
                }

                # Récupérer la première permission valide
                user_permissions = request.session['user_permissions']
                for permission in user_permissions:
                    if permission in permission_redirects:
                        return redirect(permission_redirects[permission])

                # Si aucune permission correspondante n'est trouvée, rediriger vers une page par défaut
                return redirect('accueil:index')
            else:
                messages.error(request, 'Identifiants invalides')
    else:
        form = LoginForm()

    return render(request, 'accueil/login.html', {'form': form})


def user_logout(request):
    # Déconnecter l'utilisateur et vider la session
    logout(request)
    request.session.flush()  # Supprime toutes les données de session
    return redirect('accueil:user_login')  # Redirige vers la page de connexion





#return HttpResponse("Bonjour tous le monde. Ceci est un index de sondage.")
# Create your views here.


def add_role(request):
    # Récupérer les informations utilisateur depuis la session
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Le rôle a été ajouté avec succès.')
            return redirect('accueil:add_role')  # Assurez-vous que 'add_role' est le nom correct de l'URL
    else:
        form = RoleForm()

    # Récupérer les rôles existants
    roles = Role.objects.all()
    context = {
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom,
        'form': form,
        'roles': roles
    }
    
    return render(request, 'accueil/add_role.html', context)



def edit_role(request):
    if request.method == 'POST':
        role_id = request.POST.get('role_id')
        role = get_object_or_404(Role, id=role_id)
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, 'Le rôle a été modifié avec succès.')
        else:
            messages.error(request, 'Une erreur s\'est produite lors de la modification du rôle.')
        return redirect('accueil:add_role')  # Replace with your actual URL name


def delete_role(request):
    if request.method == 'POST':
        role_id = request.POST.get('role_id')
        role = get_object_or_404(Role, id=role_id)
        role.delete()
        messages.success(request, 'Le rôle a été supprimé avec succès.')
        return redirect('accueil:add_role')  # Replace with your actual URL name




############################################




def calendar_view(request):
    utilisateur_nom = request.session.get('user_nom', 'Nom non disponible')
    utilisateur_prenom = request.session.get('user_prenom', 'Prénom non disponible')
    role = request.session.get('user_role', 'Role non disponible')
    user_id = request.session.get('user_id')
    
    utilisateur = Utilisateur.objects.get(id=user_id)
    profile_image = utilisateur.image.url if utilisateur.image else None
    employes = Employe.objects.all()
    
    events = []
    current_year = datetime.now().year

    # Ajouter les anniversaires et fins de contrat des employés
    for employe in employes:
        anniversaire = employe.date_naissance.replace(year=current_year)
        events.append({
            'title': f"Anniversaire: {employe.prenom} {employe.nom}",
            'start': anniversaire.isoformat(),
            'color': 'blue'
        })
        
        if employe.date_fin_contrat:
            events.append({
                'title': f"Fin de contrat: {employe.prenom} {employe.nom}",
                'start': employe.date_fin_contrat.isoformat(),
                'color': 'red'
            })

    # Récupérer les congés confirmés
    conges_confirmes = DemandeConges.objects.filter(statut='confirmée')

    for conge in conges_confirmes:
        event = {
            'title': f"Congé {conge.type_conge}: {conge.employe.prenom} {conge.employe.nom}",
            'start': conge.date_debut.isoformat(),
            'color': 'green'
        }
        if conge.date_fin:
            event['end'] = conge.date_fin.isoformat()
        events.append(event)

    # Récupérer les entretiens planifiés
    candidats_entretien = Candidat.objects.filter(entretien_date__isnull=False)

    for candidat in candidats_entretien:
        events.append({
            'title': f"Entretien: {candidat.prenom} {candidat.nom} pour {candidat.poste.titre}",
            'start': candidat.entretien_date.isoformat(),
            'color': 'orange'  # Couleur pour les entretiens
        })

    context = {
        'events': events,
        'role': role,
        'utilisateur_nom': utilisateur_nom,
        'utilisateur_prenom': utilisateur_prenom,
        'profile_image': profile_image,
    }
    
    return render(request, 'accueil/calendar.html', context)



def configuration(request):
    return render(request, 'accueil/home.html')




