from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

class Permission(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=50, unique=True)  # Code unique pour identifier la permission

    def __str__(self):
        return self.nom


class Role(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True)  
    permissions = models.ManyToManyField(Permission, related_name='roles', blank=True)  # Relation avec Permission

    def __str__(self):
        return self.nom
    
    
    
class Utilisateur(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    mot_de_passe = models.CharField(max_length=128)  # Stockage des mots de passe hachés
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    last_login = models.DateTimeField(blank=True, null=True)  # Ajout du champ last_login
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)  # New image field
   
    
    def set_password(self, raw_password):
        self.mot_de_passe = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.mot_de_passe)
    
    def update_last_login(self):
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])

    def __str__(self):
        return f'{self.nom} {self.prenom} ({self.email})'
    
    
    
# Create your models here.

