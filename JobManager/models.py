from django.db import models
import datetime

today = datetime.date.today()

class ExecuteJob(models.Model):
    user_id = models.IntegerField(db_column="user_id", blank=True, null=True)
    file1 = models.CharField(db_column="File1",max_length=60, blank=True, null=True)
    file2 = models.CharField(db_column="File2",max_length=60, blank=True, null=True)
    file1_size = models.CharField(db_column="file1_size",max_length=60,null=True, blank=True)
    file2_size = models.CharField(db_column="file2_size",max_length=60,null=True, blank=True)
    file1_id = models.IntegerField(db_column="file1_id",null=True, blank=True)
    file2_id = models.IntegerField(db_column="file2_id",null=True, blank=True)
    #tools_selected = models.CharField(db_column="tools_selected",max_length=60, blank=True, null=True)
    #report_type = models.CharField(db_column="report_type",max_length=60, blank=True, null=True)
    date = models.DateField(db_column="date",default=today, null=True, blank=True)
    policy_id = models.IntegerField(db_column="policy_id",null=True, blank=True)
    job_id = models.AutoField(primary_key=True)

    xdelta3_status = models.CharField(db_column="xdelta3_status",max_length=60, default=None,null=True, blank=True)
    bsdiff_status = models.CharField(db_column="bsdiff_status", max_length=60, default=None,null=True, blank=True)
    vcdiff_status = models.CharField(db_column="vcdiff_status", max_length=60, default=None,null=True, blank=True)

    class Meta:
        db_table = 'ExecuteJob'

class ToolsResult(models.Model):
    user_id = models.IntegerField(db_column="user_id", blank=True, null=True)
    job_id = models.IntegerField(db_column="job_id", blank=True, null=True)
    delta_file_name = models.CharField(db_column="delta_file_name",max_length=60, blank=True, null=True)
    delta_tool = models.CharField(db_column="delta_tool",max_length=60, blank=True, null=True)
    delta_size = models.CharField(db_column="delta_size",max_length=60,null=True, blank=True,default=None)
    delta_time = models.CharField(db_column="delta_time",max_length=60, blank=True, null=True,default=None)
    recreation_time = models.CharField(db_column="recreation_time",max_length=60, blank=True, null=True, default=None)

    class Meta:
        managed = True
        db_table = 'ToolsResult'

class iDeltaSummary(models.Model):
    user_id = models.IntegerField(db_column="user_id", blank=True, null=True)
    job_id = models.IntegerField(db_column="job_id", blank=True, null=True)
    orig_file = models.CharField(db_column="orig_file",max_length=60, blank=True, null=True)
    new_file = models.CharField(db_column="new_file",max_length=60, blank=True, null=True)
    orig_file_size = models.CharField(db_column="orig_file_size",max_length=60,null=True, blank=True)
    new_file_size = models.CharField(db_column="new_file_size",max_length=60,null=True, blank=True)
    patch_tool = models.CharField(db_column="patch_tool",max_length=60,null=True, blank=True)
    patch_file = models.CharField(db_column="patch_file",max_length=60,null=True, blank=True)
    patch_size = models.CharField(db_column="patch_size",max_length=60,null=True, blank=True,default=None)
    patch_time = models.CharField(db_column="patch_time",max_length=60,null=True, blank=True, default=None)
    recreation_time = models.CharField(db_column="recreation_time",max_length=60,null=True, blank=True, default=None)

    class Meta:
        managed = True
        db_table = 'iDeltaSummary'
