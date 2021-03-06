# Generated by Django 2.2.7 on 2019-11-18 18:41

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20191118_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='numberplate',
            name='number',
            field=models.CharField(max_length=6, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_number_plate', message='Plate number should contain first three alphabetical letters followed by three numbers. exmp.: ABC123', regex='[A-Za-z]{3}\\d{3}')]),
        ),
    ]
