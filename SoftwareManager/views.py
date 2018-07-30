from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from chunked_upload_custom.views import ChunkedUploadView, ChunkedUploadCompleteView
from .models import UploadedSoftwareObject
from django.http import HttpResponse
import json
import subprocess
from util.constants import *
from userprofile.views import session_env
import os,shutil

def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

# Create your views here.
@login_required
def upload(request):
    current_user = request.user
    #session_env(request)
    UploadedSoftwareObject.objects.filter(file_size__isnull=True).delete()
    output = list(UploadedSoftwareObject.objects.filter(user_id=current_user.id).values().order_by('id').reverse())
    output = json.dumps(output, default=date_handler)
    return render(request, 'SoftwareManager/upload.html', {'init_data' : output, 'type': "initial"})

@login_required
def delete_file(request):
    current_user = request.user
    job_id =  request.POST.get("job_id")
    pathDeleteFile = UploadedSoftwareObject.objects.filter(user_id=current_user.id, id=job_id).values('file')[0]["file"]
    UploadedSoftwareObject.objects.filter(user_id=current_user.id, id=job_id).delete()
    #remove_file_from_disk(pathDeleteFile)
    remove_file_from_disk(pathDeleteFile)
    output = list(UploadedSoftwareObject.objects.filter(user_id=current_user.id).values().order_by('id').reverse())
    output = json.dumps(output, default=date_handler)
    return HttpResponse(output)


def remove_file_from_disk(pathDeleteFile):

    p_remove = subprocess.Popen(['rm', pathDeleteFile],cwd=MEDIA_PATH,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    out_remove, err_remove = p_remove.communicate()

@login_required
def verify_duplicate_file(request):
    current_user = request.user

    output1 = list(UploadedSoftwareObject.objects.filter(user_id=current_user.id).values_list('title'))
    output2 = list(UploadedSoftwareObject.objects.filter(user_id=current_user.id).values_list('filename'))
    # print "title uploadfilename"
    # print title, filename
    # print "print file names"
    # print output2
    # for filenm in output2:
    #     print filenm[0]
    output = [output1, output2]
    output = json.dumps(output)
    return HttpResponse(output)

class UploadView(ChunkedUploadView):

    model = UploadedSoftwareObject
    field_name = 'the_file'
    def check_permissions(self, request):
        # Allow non authenticated users to make uploads
         pass


class UploadCompleteView(ChunkedUploadCompleteView):

    model = UploadedSoftwareObject

    def check_permissions(self, request):
        # Allow non authenticated users to make uploads
        pass

    def on_completion(self, uploaded_file, request):
        model = UploadedSoftwareObject
        queryset = model.objects.all()
        if hasattr(request, 'user') and request.user.is_authenticated():
            queryset = list(queryset.filter(user=request.user).values())
        # print queryset

        title = request.POST.get('name')
        version = request.POST.get('version')
        current_user = request.user
        print str(title)
        file_exist = UploadedSoftwareObject.objects.filter(title = str(title), version = str(version), file_size = request.POST.get('size'), user_id = current_user.id)
        if not file_exist:
            print "saved the file"
            UploadedSoftwareObject(title = str(title), version = str(version), user_id = current_user.id, file_size = request.POST.get('size')).save()



    def get_response_data(self, chunked_upload, request):
        current_user = request.user
        output = list(UploadedSoftwareObject.objects.filter(user_id=current_user.id).values().order_by('id').reverse())
        print output
        return {'message': ("You successfully uploaded '%s' (%s bytes)! " %
                            (chunked_upload.filename, chunked_upload.offset)), 'output_list': output}



