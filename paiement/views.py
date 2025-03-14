from django.shortcuts import get_object_or_404, render

# Create your views here.
from django.shortcuts import render, redirect
from .forms import EmployeIndemnitesForm, IndemniteForm, EmployeAvantageForm, RetenueRevenuForm
from .models import EmployeIndemnite, Indemnite, RetenueRevenu
from employe.models import Employe

def ajouter_indemnite(request):
    if request.method == 'POST':
        form = IndemniteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('paiement:ajouter_indemnite')  # Redirigez vers une page de votre choix après l'ajout
    else:
        form = IndemniteForm()
    
    return render(request, 'paiement/indemnite.html', {'form': form})



def ajouter_indemnites_employe(request, employe_id):
    employe = Employe.objects.get(id=employe_id)

    if request.method == 'POST':
        form = EmployeIndemnitesForm(request.POST)
        if form.is_valid():
            indemnites_selectionnees = form.cleaned_data['indemnites']
            for indemnite in indemnites_selectionnees:
                somme_percue = form.cleaned_data.get(f"somme_percue_{indemnite.id}")
                if somme_percue:
                    # Crée une instance EmployeIndemnite
                    EmployeIndemnite.objects.create(
                        employe=employe,
                        indemnite=indemnite,
                        somme_percue=somme_percue
                    )
            return redirect('employe:liste_employes')  # Redirige vers la liste des employés ou une autre page

    else:
        form = EmployeIndemnitesForm()

    return render(request, 'paiement/ajouter_indemnites.html', {'form': form, 'employe': employe})



#################################
from .forms import AvantageEnNatureForm

def ajouter_avantage_en_nature(request):
    if request.method == "POST":
        form = AvantageEnNatureForm(request.POST)
        if form.is_valid():
            form.save()  # Enregistrer l'avantage en nature
            return redirect('paiement:ajouter_avantage')  # Rediriger vers une page de liste des avantages (si elle existe)
    else:
        form = AvantageEnNatureForm()
    
    return render(request, 'paiement/ajouter_avantage_en_nature.html', {'form': form})









def ajouter_avantages_employe(request, employe_id):
    employe = Employe.objects.get(id=employe_id)  # Récupérer l'employé par son ID
    if request.method == "POST":
        form = EmployeAvantageForm(request.POST, instance=employe)
        if form.is_valid():
            form.save()  # Sauvegarder les avantages sélectionnés
            return redirect('employe:liste_employes')  # 
    else:
        form = EmployeAvantageForm(instance=employe)
    
    return render(request, 'paiement/ajouter_avantages_employe.html', {'form': form, 'employe': employe})



def add_retenue_revenu(request, employe_id):
    employe = get_object_or_404(Employe, id=employe_id)
    
    if request.method == 'POST':
        form = RetenueRevenuForm(request.POST)
        if form.is_valid():
            retenue_revenu = form.save(commit=False)
            retenue_revenu.employe = employe  # Link the employee
            retenue_revenu.save()
            return redirect('paiement:add_retenue_revenu', employe_id=employe.id)  # Redirect to list view after saving
    else:
        form = RetenueRevenuForm()
    
    return render(request, 'paiement/add_retenue_revenu.html', {'form': form, 'employe': employe})



# View for listing all "Retenue/Revenu"
#def list_retenues_revenus(request):
    #retenues_revenus = RetenueRevenu.objects.all()
    #return render(request, 'retenue_revenu/list_retenues_revenus.html', {'retenues_revenus': retenues_revenus})
