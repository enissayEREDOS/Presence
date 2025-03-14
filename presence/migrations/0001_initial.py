# Generated by Django 5.1 on 2024-09-12 14:14

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employe', '0004_remove_formation_date_demande_formation_date_debut_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SettingsHeures',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heure_arrivee_normale', models.TimeField(default='08:00:00')),
                ('heure_depart_normale', models.TimeField(default='16:00:00')),
            ],
        ),
        migrations.CreateModel(
            name='Presence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('heure_arrivee', models.TimeField(blank=True, null=True)),
                ('heure_depart', models.TimeField(blank=True, null=True)),
                ('retard', models.BooleanField(default=False)),
                ('heures_travail', models.DurationField(default=datetime.timedelta(seconds=28800))),
                ('compteur_actif', models.BooleanField(default=False)),
                ('temps_restant', models.DurationField(default=datetime.timedelta(seconds=28800))),
                ('employe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employe.employe')),
            ],
        ),
    ]
