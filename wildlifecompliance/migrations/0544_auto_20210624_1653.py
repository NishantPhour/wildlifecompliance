# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-06-24 08:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0543_remove_applicationstandardcondition_additional_information'),
    ]

    operations = [
        migrations.AlterField(
            model_name='return',
            name='processing_status',
            field=models.CharField(choices=[('due', 'Due'), ('overdue', 'Overdue'), ('draft', 'Draft'), ('future', 'Future'), ('with_curator', 'With Curator'), ('accepted', 'Accepted'), ('payment', 'Awaiting Payment'), ('discarded', 'Discarded'), ('expired', 'Expired')], default='future', max_length=20),
        ),
    ]
