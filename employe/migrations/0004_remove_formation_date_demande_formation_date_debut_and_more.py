# Generated by Django 5.1 on 2024-09-09 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employe', '0003_demandeconges_date_demande'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='formation',
            name='date_demande',
        ),
        migrations.AddField(
            model_name='formation',
            name='date_debut',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='formation',
            name='date_fin',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='formation',
            name='formateur',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='formation',
            name='heure_debut',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='formation',
            name='heure_fin',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='formation',
            name='statut',
            field=models.CharField(choices=[('en attente', 'En attente'), ('planifiée', 'Planifiée'), ('rejetée', 'Rejetée')], max_length=50),
        ),
        migrations.AlterField(
            model_name='formation',
            name='titre',
            field=models.CharField(max_length=255),
        ),
    ]
