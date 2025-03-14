from django import forms
from .models import Employe
from .models import DemandeConges, TypeConge, SondageSatisfaction
from .models import Fonction, Departement

#################################################
class DepartementForm(forms.ModelForm):
    class Meta:
        model = Departement
        fields = ['nom', 'description']

class FonctionForm(forms.ModelForm):
    class Meta:
        model = Fonction
        fields = ['nom', 'salaire', 'departement']

###############################################




class EmployeForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = [
            'prenom', 'nom', 'email', 'date_naissance', 'genre', 'nationalite',
            'numero_telephone', 'fonction', 'departement', 'categorie',
            'date_debut', 'type_contrat', 'date_fin_contrat', 'heures_travail',
            'nbr_jours_conges_AN', 'cv', 'lettre_motivation',
            'contrat_travail', 'certificats_diplomes', 'nombre_enfants',
            'matricule', 'numero_cnss', 'numero_compte', 'mode_paiement'
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'date_debut': forms.DateInput(attrs={'type': 'date'}),
            'date_fin_contrat': forms.DateInput(attrs={'type': 'date'}),
            'type_contrat': forms.Select(choices=Employe.TYPE_CONTRAT_CHOICES),
            'genre': forms.Select(choices=Employe.SEXE_CHOICES),
            'categorie': forms.Select(choices=Employe.CATEGORIE_CHOICES),  # Widget pour le champ catégorie
            'mode_paiement': forms.Select(choices=Employe.MODE_PAIEMENT_CHOICES),  # Widget pour mode de paiement
        }

    fonction = forms.ModelChoiceField(queryset=Fonction.objects.all(), label='Fonction', required=True)
    departement = forms.ModelChoiceField(queryset=Departement.objects.all(), label='Département', required=True)

    def clean(self):
        cleaned_data = super().clean()
        type_contrat = cleaned_data.get("type_contrat")
        date_fin_contrat = cleaned_data.get("date_fin_contrat")

        # Vérification pour le contrat CDD
        if type_contrat == 'CDD' and not date_fin_contrat:
            self.add_error('date_fin_contrat', 'La date de fin de contrat est requise pour un CDD.')

        return cleaned_data










class TypeCongeForm(forms.ModelForm):
    class Meta:
        model = TypeConge
        fields = ['nom', 'nombre_jours']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du type de congé'}),
            'nombre_jours': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de jours autorisés'}),
        }
        labels = {
            'nom': 'Type de Congé',
            'nombre_jours': 'Nombre de Jours',
        }
        help_texts = {
            'nom': 'Indiquez le type de congé (ex: Annuel, Maladie, etc.).',
            'nombre_jours': 'Nombre de jours autorisés pour ce type de congé.',
        }

    def __init__(self, *args, **kwargs):
        super(TypeCongeForm, self).__init__(*args, **kwargs)
        # Personnalisation des champs
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': self.fields[field].label
            })



class DemandeCongesForm(forms.ModelForm):
    # Utiliser ModelChoiceField pour obtenir les types de congés depuis la table TypeConge
    type_conge = forms.ModelChoiceField(
        queryset=TypeConge.objects.all(),
        empty_label="Choisissez un type de congé",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = DemandeConges
        fields = ['type_conge', 'date_debut', 'motif']  # Garder seulement les champs nécessaires
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'motif': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'type_conge': 'Type de Congé',
            'date_debut': 'Date de Début',
            'motif': 'Motif de la Demande',
        }
        help_texts = {
            'date_debut': 'Sélectionnez la date de début du congé.',
            'motif': 'Décrivez brièvement la raison de votre demande.',
        }

    def __init__(self, *args, **kwargs):
        super(DemandeCongesForm, self).__init__(*args, **kwargs)
        
        # Champs spécifiques
        self.fields['motif'].widget.attrs.update({
            'placeholder': 'Expliquez la raison de votre demande...'
        })
        self.fields['date_debut'].widget.attrs.update({
            'min': '2023-01-01',  # Exemple d'ajout d'une contrainte
        })

    # Validation personnalisée pour s'assurer que la date de début est correcte
    def clean(self):
        cleaned_data = super(DemandeCongesForm, self).clean()
        date_debut = cleaned_data.get("date_debut")
        date_fin = cleaned_data.get("date_fin")

        if date_debut and date_fin:
            if date_debut > date_fin:
                self.add_error('date_debut', "La date de début ne peut pas être après la date de fin.")
                self.add_error('date_fin', "La date de fin doit être après la date de début.")
        return cleaned_data



##################################################################


from .models import Formation

class FormationForm(forms.ModelForm):
    class Meta:
        model = Formation
        fields = ['titre', 'description']
        labels = {
            'titre': 'Titre de la formation',
            'description': 'Description de la formation',
        }
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le titre de la formation'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez la description détaillée de la formation',
                'rows': 5,
            }),
        }

###############################################
from .models import Absence

class AbsenceForm(forms.ModelForm):
    class Meta:
        model = Absence
        fields = ['date_debut', 'date_fin', 'motif']
        labels = {
            'date_debut': 'Date de début de l\'absence',
            'date_fin': 'Date de fin de l\'absence',
            'motif': 'Motif de l\'absence',
        }
        widgets = {
            'date_debut': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'date_fin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'motif': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Expliquez le motif de l\'absence',
                'rows': 4,
            }),
        }
##################################################################

class PlanificationFormationForm(forms.ModelForm):
    class Meta:
        model = Formation
        fields = ['date_debut', 'date_fin', 'heure_debut', 'heure_fin', 'formateur']
        
        # Labels personnalisés et widgets avec placeholders et classes CSS
        labels = {
            'date_debut': 'Date de début',
            'date_fin': 'Date de fin',
            'heure_debut': 'Heure de début',
            'heure_fin': 'Heure de fin',
            'formateur': 'Formateur'
        }
        
        widgets = {
            'date_debut': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control', 
                'placeholder': 'Sélectionnez la date de début'
            }),
            'date_fin': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control', 
                'placeholder': 'Sélectionnez la date de fin'
            }),
            'heure_debut': forms.TimeInput(attrs={
                'type': 'time', 
                'class': 'form-control', 
                'placeholder': 'Sélectionnez l\'heure de début'
            }),
            'heure_fin': forms.TimeInput(attrs={
                'type': 'time', 
                'class': 'form-control', 
                'placeholder': 'Sélectionnez l\'heure de fin'
            }),
            'formateur': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nom du formateur'
            }),
        }
        
        
        ####################################################
        

class SondageSatisfactionForm(forms.ModelForm):
    class Meta:
        model = SondageSatisfaction
        fields = ['score', 'commentaire']
        widgets = {
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Laissez un commentaire (facultatif)'}),
        }
        labels = {
            'commentaire': 'Commentaire',
        }
