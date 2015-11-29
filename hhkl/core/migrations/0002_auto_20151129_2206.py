# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='table',
            name='type',
            field=models.CharField(max_length=50, choices=[(b'brief', b'Brief'), (b'yellow', b'Yellow'), (b'red', b'Red')]),
        ),
    ]
