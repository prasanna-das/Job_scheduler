# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('JobManager', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='executejob',
            name='bsdiff_status',
            field=models.CharField(default=None, max_length=60, null=True, db_column=b'bsdiff_status', blank=True),
        ),
        migrations.AddField(
            model_name='executejob',
            name='vcdiff_status',
            field=models.CharField(default=None, max_length=60, null=True, db_column=b'vcdiff_status', blank=True),
        ),
        migrations.AddField(
            model_name='executejob',
            name='xdelta3_status',
            field=models.CharField(default=None, max_length=60, null=True, db_column=b'xdelta3_status', blank=True),
        ),
    ]
