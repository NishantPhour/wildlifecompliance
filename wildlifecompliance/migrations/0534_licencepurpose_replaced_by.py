# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-04-21 04:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0533_auto_20210421_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='licencepurpose',
            name='replaced_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='wildlifecompliance.LicencePurpose'),
        ),
    ]
