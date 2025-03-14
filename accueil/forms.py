# forms.py
from django import forms
from .models import Utilisateur, Role, Permission

class UtilisateurCreationForm(forms.ModelForm):
    mot_de_passe1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}),
        label="Mot de passe"
    )
    mot_de_passe2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'}),
        label="Confirmer le mot de passe"
    )
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        label="Rôle",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Utilisateur
        fields = ['nom', 'prenom', 'email', 'mot_de_passe1', 'role']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        mot_de_passe1 = cleaned_data.get('mot_de_passe1')
        mot_de_passe2 = cleaned_data.get('mot_de_passe2')

        if mot_de_passe1 and mot_de_passe2 and mot_de_passe1 != mot_de_passe2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas")

    def save(self, commit=True):
        utilisateur = super().save(commit=False)
        utilisateur.set_password(self.cleaned_data['mot_de_passe1'])
        if commit:
            utilisateur.save()
        return utilisateur



# forms.py
class LoginForm(forms.Form):
    email = forms.EmailField()
    mot_de_passe = forms.CharField(widget=forms.PasswordInput)
    
    
    
class RoleForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple(
            attrs={
                'class': 'permission-checkboxes',
                'aria-label': 'Permissions',
            }
        ),
        required=False
    )

    class Meta:
        model = Role
        fields = ['nom', 'description', 'permissions']
        widgets = {
            'nom': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nom du rôle',
                    'aria-label': 'Nom du rôle',
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Description',
                    'aria-label': 'Description',
                }
            ),
        }



class UtilisateurEditForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['nom', 'prenom', 'email', 'role']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }




####################################
