# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-06-09 05:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0540_auto_20210606_0538'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questionoptioncondition',
            name='option',
        ),
        migrations.DeleteModel(
            name='QuestionOptionCondition',
        ),
    ]
