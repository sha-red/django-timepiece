# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0003_auto_20151217_1350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='activity',
            field=models.ForeignKey(related_name='entries', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='entries.Activity', null=True),
        ),
    ]
