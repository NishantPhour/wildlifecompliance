# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-01-31 02:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        #('invoice', '0010_invoice_payment_method'),
        ('wildlifecompliance', '0397_remove_sanctionoutcome_payment_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='infringementpenaltyinvoice',
            name='infringement_penalty',
        ),
        migrations.AddField(
            model_name='infringementpenalty',
            name='invoice',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='invoice.Invoice'),
        ),
        migrations.DeleteModel(
            name='InfringementPenaltyInvoice',
        ),
    ]
