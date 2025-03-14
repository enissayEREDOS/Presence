
from django.urls import path
from . import views
from accueil.views import index
from django.conf import settings
from django.conf.urls.static import static

app_name = 'presence'

urlpatterns = [
    path('update-compteur/', views.update_compteur, name='update_compteur'),
    path('liste_presences/', views.liste_presences, name='liste_presences'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
