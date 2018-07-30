from django.db import models
import datetime

today = datetime.date.today()

def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj


class PolicyManager(models.Model):
    user_id = models.IntegerField(db_column="user_id", blank=True, null=True)
    policy_id = models.AutoField(primary_key=True)
    severity = models.CharField(db_column="severity",max_length=60, blank=True, null=True)
    size = models.CharField(db_column="size",max_length=60, blank=True, null=True)
    reconstruction_time = models.CharField(db_column="reconstruction_time",max_length=60,null=True, blank=True)
    patch_time = models.CharField(db_column="patch_time",max_length=60, blank=True, null=True)
    date = models.DateField(db_column="date",default=today, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'PolicyManager'