# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-03-10 01:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0441_auto_20200303_1010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sanctionoutcomeduedate',
            name='due_date_term_currently_applied',
            field=models.CharField(default=b'1st', max_length=10),
        ),
    ]
