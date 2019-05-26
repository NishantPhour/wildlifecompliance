# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-01-10 07:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mooring', '0098_admissionsoraclecode_mooring_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingperiodoption',
            name='mooring_group',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='mooring.MooringAreaGroup'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cancelgroup',
            name='mooring_group',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='mooring.MooringAreaGroup'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='changegroup',
            name='mooring_group',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='mooring.MooringAreaGroup'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='promoarea',
            name='zoom_level',
            field=models.IntegerField(choices=[(0, 'default'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '4'), (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10'), (11, '11'), (12, '12'), (13, '13'), (14, '14'), (15, '15'), (16, '16')], default=-1),
        ),
    ]