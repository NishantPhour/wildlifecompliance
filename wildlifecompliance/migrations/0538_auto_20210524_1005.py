# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-05-24 02:05
from __future__ import unicode_literals

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0537_auto_20210518_1130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sectionquestion',
            name='tag',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('isRepeatable', 'isRepeatable'), ('isRequired', 'isRequired'), ('PromptInspection', 'isRequired - Inspection')], max_length=400, null=True),
        ),
    ]