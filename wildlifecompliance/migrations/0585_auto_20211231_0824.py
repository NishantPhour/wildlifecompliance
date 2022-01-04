# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-12-31 00:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0584_auto_20211222_1057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wildcarespeciestype',
            name='call_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='wildcare_species_types', to='wildlifecompliance.CallType'),
        ),
        migrations.AlterUniqueTogether(
            name='wildcarespeciestype',
            unique_together=set([]),
        ),
    ]
