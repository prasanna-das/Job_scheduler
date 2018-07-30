from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import *
import json
import time
from SoftwareManager.models import *
from util.runDeltaCompressionJob import *
from policy_manager.models import *
from util.constants import *
from django.db.models import Q
import shutil,threading, Queue
from userprofile.views import session_env

def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj


# Create your views here.
@login_required
def delta_analysis(request):
    current_user = request.user
    #session_env(request)
    output = list(
        ExecuteJob.objects.filter(user_id=current_user.id).values("job_id", "file1", "file2", "date", "xdelta3_status",
                                                                  "vcdiff_status", "bsdiff_status").exclude(
            Q(xdelta3_status__isnull=True) | Q(bsdiff_status__isnull=True) | Q(vcdiff_status__isnull=True)).order_by(
            'job_id').reverse())

    output = json.dumps(output, default=date_handler)
    return render(request, 'JobManager/job_manager.html', {'init_data' : output, 'type': "initial"})

@login_required
def file_list(request):
    current_user = request.user
    output = list(UploadedSoftwareObject.objects.filter(user_id=current_user.id).values_list('title'))
    output = json.dumps(output)
    return HttpResponse(output)


def execution_status(request):
    #
    # import pdb
    # pdb.set_trace()
    main_thread = threading.currentThread()
    jobsalive = []
    for t in threading.enumerate():
        if t is main_thread:
            continue
        jobname = t.getName()
        if  "Delta" in jobname:
            jobsalive.append( jobname)
       # print jobsalive
    output = json.dumps(jobsalive)
    return HttpResponse(output)




@login_required
def execute(request):
    current_user = request.user
    #import pdb
    #pdb.set_trace()
    #tools_checked = request.POST.getlist('tool')
    file1 = request.POST.get('file1')
    file2 = request.POST.get('file2')
    select_policy = request.POST.get('select_policy')
    policy_id = 0
    remrow = 0
    evt = threading.Event()
    my_queue = Queue.Queue()
    lock = threading.Lock()
    counter = 0
    threads = []
    if select_policy:
        policy_id = select_policy.split(',')[0]
    else:
        print "Policy can't left blank ,Please select policy"
        return None

    file1_data = UploadedSoftwareObject.objects.filter(title=file1, user_id=current_user.id).values('file_size', 'id')
    file2_data = UploadedSoftwareObject.objects.filter(title=file2, user_id=current_user.id).values('file_size', 'id')

    file1_size, file1_id = file1_data[0]["file_size"], file1_data[0]["id"]
    file2_size, file2_id = file2_data[0]["file_size"], file2_data[0]["id"]

    #job_id = ExecuteJob.objects.filter(user_id=current_user.id).filter(file1_id = file1_id, file2_id = file2_id).filter(tools_selected = tools_checked).values_list('job_id')
    job_id = ExecuteJob.objects.filter(user_id=current_user.id).filter(file1_id = file1_id, file2_id = file2_id).values_list('job_id')

    if not job_id:

        ExecuteJob(user_id = current_user.id, file1 = file1, file2 = file2, file1_size=file1_size, file2_size=file2_size, file1_id=file1_id, file2_id=file2_id, policy_id=policy_id).save()
        jid = ExecuteJob.objects.filter(user_id=current_user.id).filter(file1_id = file1_id).filter(file2_id = file2_id).values("job_id")
        job_id = jid[0]["job_id"]
        prepare_fm_for_each_job(job_id)

        for tool in [ 'xdelta3','bsdiff','vcdiff' ]:
            # I hardcorded delta_size, delta_time, recreation_time where we need to store Dynamic values
            existing_result = ToolsResult.objects.filter(user_id = current_user.id, job_id=job_id, delta_tool=tool).values("delta_size", "delta_time", "recreation_time" )
            if not existing_result:
                tool_directory_path = prepare_fm_for_each_tool(job_id, tool)
              #  status_msg = perform_delta_compression( current_user, job_id, tool, current_user.id, tool_directory_path)
                jobname = "Delta tool " + tool + " running for " + file1 + " and " + file2 + " \n"
                t = threading.Thread(name=jobname, target=perform_delta_compression, args=(current_user, job_id, tool, current_user.id, tool_directory_path, my_queue, lock))
                t.start()
                threads.append(t)

        while not evt.is_set():
            if my_queue.qsize() == 3:
                evt.set()
                for t in threads:
                    t.join()

        while not my_queue.empty():
            (tool,status_msg) =  my_queue.get()
            print tool,status_msg
            if tool == "xdelta3" :
                if status_msg :
                    ExecuteJob.objects.filter(user_id=current_user.id,job_id = job_id).update(xdelta3_status = "Passed")
                else :
                    ExecuteJob.objects.filter(user_id=current_user.id, job_id=job_id).update(xdelta3_status="Failed")
            if tool == "bsdiff":
                if status_msg:
                    ExecuteJob.objects.filter(user_id=current_user.id, job_id=job_id).update(bsdiff_status="Passed")
                else:
                    ExecuteJob.objects.filter(user_id=current_user.id, job_id=job_id).update(bsdiff_status="Failed")
            if tool == "vcdiff":
                if status_msg:
                    ExecuteJob.objects.filter(user_id=current_user.id, job_id=job_id).update(vcdiff_status="Passed")
                else:
                    ExecuteJob.objects.filter(user_id=current_user.id, job_id=job_id).update(vcdiff_status="Failed")


    output = list(ExecuteJob.objects.filter(user_id=current_user.id).values("job_id", "file1", "file2","date","xdelta3_status","vcdiff_status","bsdiff_status" ).exclude(
        Q(xdelta3_status__isnull=True) | Q(bsdiff_status__isnull=True) | Q(vcdiff_status__isnull=True)).order_by('job_id').reverse())
    #import pdb
    #pdb.set_trace()

    output = json.dumps(output, default=date_handler)


    delta_details = iDeltaSummary.objects.filter(user_id=current_user.id).values()

    return HttpResponse(output)

                
def perform_delta_compression(current_user, job_id, tool, user_id, tool_directory_path,out_queue,lock):
    job_status = 1
    delta_parameters = create_delta_patch(job_id, tool, tool_directory_path)
    lock.acquire()
    if type(delta_parameters) is list:
        delta_size, delta_time, recreation_time = delta_parameters[0], delta_parameters[1], delta_parameters[2]
        out_queue.put((tool, job_status))
        ToolsResult(user_id = user_id, job_id=job_id, delta_tool=tool, delta_size=delta_size, delta_time=delta_time, recreation_time=recreation_time).save()
    #Save in iDeltaSummary
    elif type(delta_parameters) is int and not delta_parameters:
        job_dir = MEDIA_PATH + 'jobs/' + str(job_id)
        job_status = delta_parameters
        #shutil.rmtree(job_dir)
        #ExecuteJob.objects.filter(user_id=current_user.id).filter(job_id=job_id).delete()
        ToolsResult(user_id=user_id, job_id=job_id, delta_tool=tool).save()
        print tool + " execution failed"
        out_queue.put((tool, job_status))


    patch_file = str(job_id)+"_patch."+tool
    patch_file_path = "./media/jobs/"+str(job_id)+"/"+tool+"/"+patch_file
    file_details = ExecuteJob.objects.filter(job_id=job_id).values("file1", "file2", "file1_size", "file2_size")
    existing_result = ToolsResult.objects.filter(user_id=current_user.id, job_id=job_id,
                                                 delta_tool=tool).values("delta_size", "delta_time", "recreation_time",
                                                                         "delta_tool")

    iDeltaSummary(user_id=current_user.id, job_id=job_id, orig_file=str(file_details[0]["file1"]),
                  orig_file_size=str(file_details[0]["file1_size"]),
                  new_file=str(file_details[0]["file2"]), new_file_size=str(file_details[0]["file2_size"]),
                  patch_tool=str(existing_result[0]["delta_tool"]), patch_file=str(job_id) + "_patch." + tool,
                  patch_size=str(existing_result[0]["delta_size"]),
                  patch_time=str(existing_result[0]["delta_time"]),
                  recreation_time=str(existing_result[0]["recreation_time"])).save()
    lock.release()


@login_required
def delete_job(request):
    current_user = request.user
    job_id =  request.POST.get("job_id")
    ExecuteJob.objects.filter(user_id=current_user.id, job_id=job_id).delete()
    ToolsResult.objects.filter(user_id=current_user.id, job_id=job_id).delete()
    iDeltaSummary.objects.filter(user_id=current_user.id, job_id=job_id).delete()
    job_dir =JOB_ROOT_PATH + str(job_id)
    shutil.rmtree(job_dir)
    output = list(ExecuteJob.objects.filter(user_id=current_user.id).values("job_id", "file1", "file2","date","xdelta3_status","vcdiff_status","bsdiff_status").order_by('job_id').reverse())
    output = json.dumps(output, default=date_handler)
    return HttpResponse(output)

def get_policy_list(request):
    current_user = request.user
    output = list(PolicyManager.objects.filter(user_id=current_user.id).values_list('policy_id', 'severity','size', 'patch_time', 'reconstruction_time').order_by('policy_id').reverse())
    output = json.dumps(output, default=date_handler)
    return HttpResponse(output)




