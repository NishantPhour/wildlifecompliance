# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-11-01 10:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0326_auto_20191101_0949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='legalcaserunningsheetentry',
            name='legal_case',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='running_sheet_entries', to='wildlifecompliance.LegalCase'),
        ),
    ]