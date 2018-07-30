# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import userprofile.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('photo', models.ImageField(default=b'userprofile/userphoto/no-image-icon-hi.png', help_text=b'Profile photo', upload_to=userprofile.models.upload_location)),
                ('firstname', models.CharField(max_length=140, null=True, blank=True)),
                ('lastname', models.CharField(max_length=140, null=True, blank=True)),
                ('user', models.OneToOneField(related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
