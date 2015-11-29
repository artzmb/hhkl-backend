# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Day',
            fields=[
                ('number', models.IntegerField(unique=True, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(choices=[(0, b'Idle'), (1, b'Running'), (2, b'Completed'), (3, b'Approved'), (4, b'Postponed')])),
                ('day', models.ForeignKey(to='core.Day')),
            ],
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('yellow', models.IntegerField()),
                ('red', models.IntegerField()),
                ('match', models.ForeignKey(to='core.Match')),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('alias', models.CharField(max_length=3)),
                ('league', models.ForeignKey(to='core.League')),
            ],
        ),
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.IntegerField(choices=[(0, b'Brief'), (1, b'Yellow'), (2, b'Red')])),
                ('league', models.OneToOneField(to='core.League')),
            ],
        ),
        migrations.CreateModel(
            name='TableRow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField()),
                ('played', models.IntegerField()),
                ('wins', models.IntegerField()),
                ('overtimeWins', models.IntegerField()),
                ('overtimeLosses', models.IntegerField()),
                ('losses', models.IntegerField()),
                ('goalsFor', models.IntegerField()),
                ('goalsAgainst', models.IntegerField()),
                ('points', models.IntegerField()),
                ('player', models.ForeignKey(to='core.Player')),
                ('table', models.ForeignKey(to='core.Table')),
            ],
        ),
        migrations.AddField(
            model_name='match',
            name='red',
            field=models.ForeignKey(related_name='red', to='core.Player'),
        ),
        migrations.AddField(
            model_name='match',
            name='yellow',
            field=models.ForeignKey(related_name='yellow', to='core.Player'),
        ),
        migrations.AddField(
            model_name='league',
            name='season',
            field=models.ForeignKey(to='core.Season'),
        ),
        migrations.AddField(
            model_name='day',
            name='league',
            field=models.ForeignKey(to='core.League'),
        ),
    ]
