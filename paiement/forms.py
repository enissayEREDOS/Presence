from django import forms
from .models import EmployeIndemnite, RetenueRevenu
from datetime import date
from django.core.exceptions import ValidationError
from django import forms
from accueil.models import Utilisateur, Role
from employe.models import DemandeConges, Employe, Notification, Absence, Formation
from .models import Indemnite, EmployeIndemnite

class IndemniteForm(forms.ModelForm):
    class Meta:
        model = Indemnite
        fields = ['nom', 'plafond', 'pourcentage']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l\'indemnité'}),
            'plafond': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Plafond de l\'indemnité'}),
            'pourcentage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Pourcentage de l\'indemnité'}),
        }
        
        

class EmployeIndemnitesForm(forms.Form):
    indemnites = forms.ModelMultipleChoiceField(
        queryset=Indemnite.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Sélectionnez les indemnités"
    )
    # Un champ pour chaque indemnité sélectionnée
    def __init__(self, *args, **kwargs):
        super(EmployeIndemnitesForm, self).__init__(*args, **kwargs)
        for indemnite in Indemnite.objects.all():
            self.fields[f"somme_percue_{indemnite.id}"] = forms.DecimalField(
                label=f"Somme perçue pour {indemnite.nom}",
                max_digits=10,
                decimal_places=2,
                required=False
            )



from .models import AvantageEnNature

class AvantageEnNatureForm(forms.ModelForm):
    class Meta:
        model = AvantageEnNature
        fields = ['nom', 'valeur']
        widgets = {
            'nom': forms.TextInput(attrs={'placeholder': 'Nom de l\'avantage'}),
            'valeur': forms.NumberInput(attrs={'placeholder': 'Valeur de l\'avantage'}),
        }


class EmployeAvantageForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = ['avantages_en_nature']  # Seulement le champ des avantages
        labels = {
            'avantages_en_nature': 'Sélectionnez les avantages en nature',
        }
        help_texts = {
            'avantages_en_nature': 'Cochez les avantages auxquels cet employé est éligible.',
        }
        widgets = {
            'avantages_en_nature': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input',
                'style': 'margin-left: 10px;'
            }),  # Widget pour afficher une liste de cases à cocher avec du style personnalisé
        }

    # Ajout de validation supplémentaire si nécessaire
    def clean_avantages_en_nature(self):
        avantages = self.cleaned_data.get('avantages_en_nature')
        if not avantages:
            raise forms.ValidationError("Vous devez sélectionner au moins un avantage.")
        return avantages
        
        
        
        
class RetenueRevenuForm(forms.ModelForm):
    class Meta:
        model = RetenueRevenu
        fields = ['type', 'description', 'montant', 'date']
        labels = {
            'type': 'Type de Retenue ou Revenu',
            'description': 'Description',
            'montant': 'Montant (en FCFA)',
            'date': 'Date',
        }
        help_texts = {
            'type': 'Sélectionnez si c’est une retenue ou un revenu.',
            'description': 'Décrivez brièvement cette retenue ou ce revenu.',
            'montant': 'Entrez le montant en FCFA.',
            'date': 'Sélectionnez la date de cette retenue ou de ce revenu.',
        }
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Saisissez une description détaillée...'
            }),
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def clean_montant(self):
        montant = self.cleaned_data.get('montant')
        if montant <= 0:
            raise forms.ValidationError("Le montant doit être supérieur à zéro.")
        return montant