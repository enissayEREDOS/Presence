from django.urls import path
from . import views

app_name='accueil'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='user_login'),
    path('ajouter-role/', views.add_role, name='add_role'),
    path('edit-role/', views.edit_role, name='edit_role'),
    path('delete-role/', views.delete_role, name='delete_role'),
    path('edit-user/', views.edit_user, name='edit_user'),
    path('delete-user/', views.delete_user, name='delete_user'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('tableau_de_bord/', views.tableau_de_bord, name='tableau_de_bord'),
    path('configuration/', views.configuration, name='configuration'),
    path('deconnexion/', views.user_logout, name='user_dec'),
]

