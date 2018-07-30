# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExecuteJob',
            fields=[
                ('user_id', models.IntegerField(null=True, db_column=b'user_id', blank=True)),
                ('file1', models.CharField(max_length=60, null=True, db_column=b'File1', blank=True)),
                ('file2', models.CharField(max_length=60, null=True, db_column=b'File2', blank=True)),
                ('file1_size', models.CharField(max_length=60, null=True, db_column=b'file1_size', blank=True)),
                ('file2_size', models.CharField(max_length=60, null=True, db_column=b'file2_size', blank=True)),
                ('file1_id', models.IntegerField(null=True, db_column=b'file1_id', blank=True)),
                ('file2_id', models.IntegerField(null=True, db_column=b'file2_id', blank=True)),
                ('date', models.DateField(default=datetime.date(2016, 9, 26), null=True, db_column=b'date', blank=True)),
                ('policy_id', models.IntegerField(null=True, db_column=b'policy_id', blank=True)),
                ('job_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'ExecuteJob',
            },
        ),
        migrations.CreateModel(
            name='iDeltaSummary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField(null=True, db_column=b'user_id', blank=True)),
                ('job_id', models.IntegerField(null=True, db_column=b'job_id', blank=True)),
                ('orig_file', models.CharField(max_length=60, null=True, db_column=b'orig_file', blank=True)),
                ('new_file', models.CharField(max_length=60, null=True, db_column=b'new_file', blank=True)),
                ('orig_file_size', models.CharField(max_length=60, null=True, db_column=b'orig_file_size', blank=True)),
                ('new_file_size', models.CharField(max_length=60, null=True, db_column=b'new_file_size', blank=True)),
                ('patch_tool', models.CharField(max_length=60, null=True, db_column=b'patch_tool', blank=True)),
                ('patch_file', models.CharField(max_length=60, null=True, db_column=b'patch_file', blank=True)),
                ('patch_size', models.CharField(default=None, max_length=60, null=True, db_column=b'patch_size', blank=True)),
                ('patch_time', models.CharField(default=None, max_length=60, null=True, db_column=b'patch_time', blank=True)),
                ('recreation_time', models.CharField(default=None, max_length=60, null=True, db_column=b'recreation_time', blank=True)),
            ],
            options={
                'db_table': 'iDeltaSummary',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ToolsResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField(null=True, db_column=b'user_id', blank=True)),
                ('job_id', models.IntegerField(null=True, db_column=b'job_id', blank=True)),
                ('delta_file_name', models.CharField(max_length=60, null=True, db_column=b'delta_file_name', blank=True)),
                ('delta_tool', models.CharField(max_length=60, null=True, db_column=b'delta_tool', blank=True)),
                ('delta_size', models.CharField(default=None, max_length=60, null=True, db_column=b'delta_size', blank=True)),
                ('delta_time', models.CharField(default=None, max_length=60, null=True, db_column=b'delta_time', blank=True)),
                ('recreation_time', models.CharField(default=None, max_length=60, null=True, db_column=b'recreation_time', blank=True)),
            ],
            options={
                'db_table': 'ToolsResult',
                'managed': True,
            },
        ),
    ]
