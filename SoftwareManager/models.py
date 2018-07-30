from django.db import models
from chunked_upload_custom.models import ChunkedUpload
from JobManager.models import *
import datetime

today = datetime.date.today()

# Create your models here.
class UploadedSoftwareObject(ChunkedUpload):
    title = models.CharField(db_column="Title",max_length=60, blank=True, null=True)
    version = models.FloatField(db_column="version",max_length=30, blank=True, null=True)
    created = models.DateField(db_column="created",default=today, null=True, blank=True)
    file_size = models.CharField(db_column="file_size",max_length=60, blank=True, null=True)