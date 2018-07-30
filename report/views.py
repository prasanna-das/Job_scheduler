from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from JobManager.models import *
from policy_manager.models import *
from django.http import HttpResponse
from userprofile.views import session_env
from pprint import pprint
import json,os, pprint
import mimetypes, urllib
from django.http import StreamingHttpResponse
from django.core.servers.basehttp import FileWrapper
from util.constants import *
from django.utils.encoding import smart_str

def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

# Create your views here.
@login_required
def report(request):
    current_user = request.user
    #session_env(request)
    job_data = list(ExecuteJob.objects.filter(user_id=current_user.id).values_list('date', 'job_id', 'file1', 'file2').order_by('job_id').reverse())
    output = json.dumps(job_data, default=date_handler)
    return render(request, 'report/report.html', {'init_data' : output, 'type': "initial"})

def format_report(current_user, job_id):
    result={}
    job_data = list(ExecuteJob.objects.filter(user_id=current_user.id, job_id=job_id).values().order_by('job_id').reverse())
    for each in job_data:

        f1, f2, tools_sel  = {}, {}, {}

        f1["name"] = each['file1']
        f1["size"] = each['file1_size']
        f2["name"] = each['file2']
        f2["size"] = each['file2_size']

        job_id = each["job_id"]
        policy_id = each["policy_id"]


        output = list(PolicyManager.objects.filter(user_id=current_user.id, policy_id=policy_id).values('policy_id', 'severity','size', 'patch_time', 'reconstruction_time'))
        policy_details = json.dumps(output, default=date_handler)
        result[job_id] = {}
        result[job_id]["job_id"] = job_id
        result[job_id]["date"] = each["date"].strftime("%a %b %d")
        result[job_id]["file1"] = f1
        result[job_id]["file2"] = f2
        result[job_id]["policy_details"] = policy_details
        result[job_id]["xdelta3_status"] = each["xdelta3_status"]
        result[job_id]["bsdiff_status"] = each["bsdiff_status"]
        result[job_id]["vcdiff_status"] = each["vcdiff_status"]



        for tool in ["xdelta3", "vcdiff", "bsdiff"]:
            res = ToolsResult.objects.filter(job_id=job_id, delta_tool = tool).values("delta_size", "delta_time", "recreation_time", "delta_tool")


            if res:
                res = res[0]
                tools_sel[tool] = {}
                tools_sel[tool]["delta_size"] = int( res["delta_size"] ) if res["delta_size"] else res["delta_size"]
                tools_sel[str(tool)]["delta_time"] =  round( float(res["delta_time"]),3)  if res["delta_time"] else res["delta_time"]
                tools_sel[str(tool)]["recreation_time"] = round( float(res["recreation_time"]), 3) if res["recreation_time"] else \
                res["recreation_time"]


                #tools_sel[tool] = {}
            #tools_sel[tool]["delta_size"] = 125678
            #tools_sel[str(tool)]["delta_time"] = 5
            #tools_sel[str(tool)]["recreation_time"] = 3

            #chart_tool.append([tool, res["delta_time"], "#b87333"])
            #chart_size.append([tool, res["delta_size"], "#b87333"])
            #chart_recreation.append([tool, res["recreation_time"], "#b87333"])

        #import pdb
        #pdb.set_trace()
        result[job_id]["Tools"] = tools_sel

        iDelta = list(iDeltaSummary.objects.filter(job_id=job_id).values())

        iDelta_Summary = json.dumps(iDelta)
        result[job_id]["iDelta_Summary"] = iDelta_Summary
        result[job_id]["graph"] = graph(current_user,job_id,result)


    return result




@login_required
def generate_report(request, id_data=None):
    current_user = request.user
    id_data = request.POST.get("dat_val")
    job_id = id_data.split(",")[1]
    result = format_report(current_user, job_id)
    output = json.dumps(result)
    print output
    return HttpResponse(output)

@login_required
def delete_report(request):
    current_user = request.user
    job_id = request.POST.get("job_id")

    # delete record and delta results from ExecuteJob and ToolsResult tables
    ExecuteJob.objects.filter(user_id=current_user.id, job_id=job_id).delete()
    ToolsResult.objects.filter(job_id=job_id, user_id=current_user.id).delete()

    # generate the results to refresh the page
    result = format_report(current_user)
    output = json.dumps(result, default=date_handler)

    return HttpResponse(output)


def graph(current_user,job_id,result):
    chart_tool, chart_size, chart_recreation = [],[],[]
   # chart_tool.append(["Element", "Seconds", { 'role': "style" } ])
   # chart_size.append(["Element", "KBs", { 'role': "style" } ])
   # chart_recreation.append(["Element", "Seconds", { 'role': "style" } ])

    '''
    count = 1;

    for tool in ["xdelta3", "vcdiff", "bsdiff"]:
        if count == 1:
            chart_tool.append([tool, 5, "#b87333"])
            chart_size.append([tool, 1345, "#b87333"])
            chart_recreation.append([tool, 3, "#b87333"])
        elif count == 2:
            chart_tool.append([tool, 5, "silver"])
            chart_size.append([tool, 1345, "silver"])
            chart_recreation.append([tool, 3, "silver"])
        else:
            chart_tool.append([tool, 5, "gold"])
            chart_size.append([tool, 1345, "gold"])
            chart_recreation.append([tool, 3, "gold"])
        count += 1
    '''

    jobs = ExecuteJob.objects.filter(user_id=current_user.id, job_id=job_id).values("xdelta3_status",  "bsdiff_status", "vcdiff_status")
    job_status = jobs[0]

    chart_tool.append( ["Element", "Secs", {'role': "style"}] )
    chart_size.append( ["Element", "KB", {'role': "style"}] )
    chart_recreation.append( ["Element", "Secs", {'role': "style"}] )
    if job_status["xdelta3_status"] == "Passed":

        chart_tool.append(["XDelta", result[job_id]["Tools"]["xdelta3"]["delta_time"], "#b87333"])
        size = result[job_id]["Tools"]["xdelta3"]["delta_size"]
        chart_size.append(["XDelta", int(size) if size is not None else 'None', "#b87333"])
        chart_recreation.append(["XDelta", result[job_id]["Tools"]["xdelta3"]["recreation_time"], "#b87333"])

    if job_status["bsdiff_status"] == "Passed":

        chart_tool.append(["BSDiff", result[job_id]["Tools"]["bsdiff"]["delta_time"], "gold"])
        size = result[job_id]["Tools"]["bsdiff"]["delta_size"]
        chart_size.append(["BSDiff", int(size) if size is not None else 'None', "gold"])
        chart_recreation.append(["BSDiff", result[job_id]["Tools"]["bsdiff"]["recreation_time"], "gold"])

    if job_status["vcdiff_status"] == "Passed":

        chart_tool.append(["VCDiff", result[job_id]["Tools"]["vcdiff"]["delta_time"], "silver"])
        size = result[job_id]["Tools"]["vcdiff"]["delta_size"]
        chart_size.append(["VCDiff", int(size) if size is not None else 'None' , "silver"])
        chart_recreation.append(["VCDiff", result[job_id]["Tools"]["vcdiff"]["recreation_time"], "silver"])

    graph_data = [chart_tool, chart_size, chart_recreation]
    return graph_data

def milisecs(duration):
    duration = duration.strip()
    secs = duration.split(".")
    milisecs = 0
    cnt = 2
    for value in secs[1]:
        milisecs += int(value)* pow(10,cnt)
        cnt-=1
    milisecs = (int(secs[0]) * 1000 )+ milisecs
    return milisecs


def downlolad_attachment(request  ):
    filedetails = request.GET.get("filedata")
    # print filedetails
    fileinfo = filedetails.split()
    tool = fileinfo[0]
    job_id = fileinfo[1]
    patch_file = fileinfo[2]
    job_dir = JOB_ROOT_PATH + str(job_id) + '/' + tool + '/'
    original_filename = job_dir + patch_file
    # print original_filename
    chunk_size = 8192
    downloadfile = patch_file
    response = StreamingHttpResponse(FileWrapper(open(original_filename), chunk_size))

    type, encoding = mimetypes.guess_type(original_filename)
    # print type
    if type is None:
        type = 'application/octet-stream'
    response['Content-Type'] = type
    response['Content-Length'] = str(os.stat(original_filename).st_size)
    if encoding is not None:
        response['Content-Encoding'] = encoding

    # To inspect details for the below code, see http://greenbytes.de/tech/tc2231/
    if u'WebKit' in request.META['HTTP_USER_AGENT']:
        # Safari 3.0 and Chrome 2.0 accepts UTF-8 encoded string directly.
        filename_header = 'filename=%s' % original_filename.encode('utf-8')
    elif u'MSIE' in request.META['HTTP_USER_AGENT']:
        # IE does not support internationalized filename at all.
        # It can only recognize internationalized URL, so we do the trick via routing rules.
        filename_header = ''
    else:
        # For others like Firefox, we follow RFC2231 (encoding extension in HTTP headers).
        filename_header = 'filename*=UTF-8\'\'%s' % urllib.quote(original_filename.encode('utf-8'))
    # print filename_header
    response['Content-Disposition'] = 'inline; ' + filename_header
    # response['Content-Disposition'] = 'inline; ' + 'filename=' + downloadfile + "/n/n/"
    # response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(downloadfile)
    response['X-Sendfile'] = smart_str( downloadfile)
    # pprint.pprint(response)str(
    print response['Content-Disposition']
    print response['Content-Type']
    print response['Content-Length']
    # print response['Content-Encoding']
    return response