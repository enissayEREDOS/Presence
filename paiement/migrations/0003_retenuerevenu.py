# Generated by Django 5.1 on 2024-09-30 09:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employe', '0008_employe_avantages_en_nature'),
        ('paiement', '0002_avantageennature'),
    ]

    operations = [
        migrations.CreateModel(
            name='RetenueRevenu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('REVENUE', 'Revenue'), ('RETENUE', 'Retenue')], max_length=10)),
                ('description', models.CharField(max_length=255)),
                ('montant', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateField()),
                ('employe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='retenues_revenus', to='employe.employe')),
            ],
        ),
    ]
