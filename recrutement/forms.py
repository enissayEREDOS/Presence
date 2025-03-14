from django import forms
from .models import Candidat, Poste
from datetime import date
from django.core.exceptions import ValidationError

class CreationCompteForm(forms.ModelForm):
    mot_de_passe = forms.CharField(widget=forms.PasswordInput)
    mot_de_passe_confirmation = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Candidat
        fields = ['nom', 'prenom', 'email', 'telephone']

    def clean(self):
        cleaned_data = super().clean()
        mot_de_passe = cleaned_data.get("mot_de_passe")
        mot_de_passe_confirmation = cleaned_data.get("mot_de_passe_confirmation")

        if mot_de_passe != mot_de_passe_confirmation:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        
        

class ConnexionForm(forms.Form):
    email = forms.EmailField()
    mot_de_passe = forms.CharField(widget=forms.PasswordInput)
    
    
    
class CandidatForm(forms.ModelForm):
    class Meta:
        model = Candidat
        fields = ['cv', 'lettre_motivation']  # Exclure les champs déjà renseignés
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cv'].required = True
        self.fields['lettre_motivation'].required = True







class PosteForm(forms.ModelForm):
    class Meta:
        model = Poste
        fields = ['titre', 'description', 'date_fin_publication']
        widgets = {
            'date_fin_publication': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajout de classes CSS et placeholders
        self.fields['titre'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Entrez le titre du poste'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Entrez la description'})

        # Ajout de messages d'aide
        self.fields['titre'].help_text = "Le titre du poste à pourvoir"
        self.fields['date_fin_publication'].help_text = "Sélectionnez une date de fin future"

    # Validation personnalisée pour la date
    def clean_date_fin_publication(self):
        date_fin = self.cleaned_data.get('date_fin_publication')
        if date_fin and date_fin < date.today():
            raise ValidationError("La date de fin de publication ne peut pas être dans le passé.")
        return date_fin
        
