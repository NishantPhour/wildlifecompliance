# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-05-02 06:48
from __future__ import unicode_literals

import commercialoperator.components.compliances.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commercialoperator', '0082_auto_20190501_1555'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChecklistQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('list_type', models.CharField(choices=[('assessor_list', 'Assessor Checklist'), ('referral_list', 'Referral Checklist')], default='assessor_list', max_length=30, verbose_name='Checklist type')),
                ('correct_answer', models.BooleanField(default=False)),
                ('obsolete', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='compliancedocument',
            name='_file',
            field=models.FileField(upload_to=commercialoperator.components.compliances.models.update_proposal_complaince_filename),
        ),
    ]
