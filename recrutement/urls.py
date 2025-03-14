
from django.urls import path
from . import views
from accueil.views import index
from django.conf import settings
from django.conf.urls.static import static

app_name = 'recrutement'

urlpatterns = [
    path('connexion/', views.connexion_view, name='connexion'),
    path('creation-compte/', views.creation_compte_view, name='creation_compte'),
    path('postuler/<int:poste_id>/', views.postuler_view, name='postuler'),
    path('ajouter_poste/', views.ajouter_poste_view, name='ajouter_poste'),
    path('modifier_poste/<int:poste_id>/', views.modifier_poste_view, name='modifier_poste'),
    path('postes/', views.afficher_postes_view, name='afficher_postes'),
    path('confirmation/', views.confirmation_view, name='confirmation'),
    path('poste/<int:poste_id>/candidats/', views.liste_candidats_poste, name='liste_candidats_poste'),
    # URL pour rejeter un candidat
    path('candidat/<int:candidat_id>/rejeter/', views.rejeter_candidat, name='rejeter_candidat'),
    # URL pour planifier un entretien
    path('candidat/<int:candidat_id>/planifier_entretien/', views.planifier_entretien, name='planifier_entretien'),
    
    path('offrir_emploi/<int:candidat_id>/', views.offrir_emploi, name='offrir_emploi'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
