
from django.urls import path
from . import views
from accueil.views import index
from django.conf import settings
from django.conf.urls.static import static

app_name = 'paiement'

urlpatterns = [
    
    path('ajouter-indemnite/', views.ajouter_indemnite, name='ajouter_indemnite'),
    path('employes/<int:employe_id>/ajouter-indemnites/', views.ajouter_indemnites_employe, name='ajouter_indemnites_employe'),
    path('ajouter-avantage/', views.ajouter_avantage_en_nature, name='ajouter_avantage'),
    path('employes/ajouter-avantages/<int:employe_id>/', views.ajouter_avantages_employe, name='ajouter_avantages_employe'),
    path('add-rv-rt/<int:employe_id>/', views.add_retenue_revenu, name='add_retenue_revenu'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
