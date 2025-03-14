
from django.urls import path
from . import views
from accueil.views import index
from presence.views import update_compteur
from django.conf import settings
from django.conf.urls.static import static

app_name = 'employe'

urlpatterns = [
    
    path('add-employe/', views.add_employe, name='add_employe'), # This maps to the add_employe view in the employe app
    path('list/', views.employe_list, name='employe_list'),
    path('portail_employe/', views.portail_employe, name='portail_employe'),
    path('portail_drh/', views.portail_drh, name='portail_drh'),
    path('portail_chef_de_departement/', views.portail_chef_de_departement, name='portail_chef_de_departement'),
    path('<int:employe_id>/edit/', views.modifier_employe, name='modifier_employe'),
    path('<int:employe_id>/delete/', views.supprimer_employe, name='supprimer_employe'), 
    path('upload-photo/', views.upload_photo, name='upload_photo'),
    path('upload-profile-chef/', views.upload_chef, name='upload_chef'),
    path('upload-profile-drf/', views.upload_drh, name='upload_drh'),
    path('creer_type_conge/', views.creer_type_conge, name='creer_type_conge'),
    path('faire_demande_conges/', views.faire_demande_conges, name='faire_demande_conges'),
    path('accepter-demande/<int:demande_id>/', views.accepter_demande, name='accepter_demande'),
    path('rejeter-demande/<int:demande_id>/', views.rejeter_demande, name='rejeter_demande'),
    path('notifications/', views.notifications_page, name='notifications_page'),
    path('accepter-demande_DRH/<int:demande_id>/', views.accepter_demande_DRH, name='accepter_demande_DRH'),
    path('rejeter-demande_DRH/<int:demande_id>/', views.rejeter_demande_DRH, name='rejeter_demande_DRH'),
    path('demander_formation/', views.demander_formation, name='demander_formation'),
    path('signaler_absence/', views.signaler_absence, name='signaler_absence'),
    path('absences/', views.liste_absences, name='liste_absences'),
    path('demandes/confirmees/', views.liste_demandes_confirmees, name='liste_demandes_confirmees'),
    #############################################################################################
    path('formation/<int:formation_id>/rejeter/', views.rejeter_formation, name='rejeter_formation'),
    path('formation/<int:formation_id>/planifier/', views.planifier_formation, name='planifier_formation'),
    path('formations-planifiees/', views.formations_planifiees, name='formations_planifiees'),
    
    ##########################################################
    path('ajouter-departement/', views.ajouter_departement, name='ajouter_departement'),
    path('ajouter-fonction/', views.ajouter_fonction, name='ajouter_fonction'),
    ####################################################################################
    
    path('salarier/', views.liste_employes, name='liste_employes'),
    path('salarier/ajouter-element/<int:id>/', views.ajouter_element, name='ajouter_element'),
    
    path('employe/<int:employe_id>/salaire_brut_imposable/', views.afficher_salaire_brut_imposable, name='salaire_brut_imposable'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
