from django.shortcuts import render
from django.contrib.auth.views import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from userprofile.views import session_env
from .models import *
import json

def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

# Create your views here.
def home(request):
    if request.user.is_authenticated():
        return render(request, 'DeltaCompressionWebtool/home.html')
    return login(request, template_name='DeltaCompressionWebtool/home.html')


@login_required
def policy_manager(request):
    #session_env(request)
    current_user = request.user
    output = list(PolicyManager.objects.filter(user_id=current_user.id).values().order_by('policy_id').reverse())
    output = json.dumps(output, default=date_handler)
    return render(request, 'policy_manager/policy_manager.html', {'init_data' : output, 'type': "initial"})

@login_required
def create_policy(request):
    current_user = request.user
    severity = request.POST.get('severity')
    size = request.POST.get('size')
    reconstruction_time = request.POST.get('reconstruction_time')
    patch_time = request.POST.get('patch_time')
    if severity == "Custom":
        custom_params = ["size", "reconstruction_time", "patch_time"]
        nulllist = []
        defaultvaluelist = [ 2,1, 3]
        valuelist = []
        for val in custom_params:
            if  eval(val) is None:
                nulllist.append(val)
                valuelist.append(defaultvaluelist[0])
                del defaultvaluelist[0]

            elif eval(val):
                if (int(eval(val)) not in valuelist):
                    nulllist.append(val)
                    valuelist.append(int(eval(val)))
                    defaultvaluelist.remove( int(eval(val)) )
                else:
                    pol_val = defaultvaluelist[0]
                    valuelist.append( pol_val )
                    nulllist.append(val)
                    del defaultvaluelist[0]


        for variable, value in zip(nulllist, valuelist):
            exec ("%s = %d" % (variable, value))
    if severity == "High":
        size = 0
        patch_time = 0
        reconstruction_time = 0
    if severity == "Low":
        size = 1
        reconstruction_time = 2
        patch_time = 3

    PolicyManager(user_id=current_user.id, severity=severity, size=size, reconstruction_time=reconstruction_time, patch_time=patch_time).save()
    output = list(PolicyManager.objects.filter(user_id=current_user.id).values().order_by('policy_id').reverse())
    #values = "\nseverity :  "+severity+" \nsize: "+ size+" \nreconstruction_time: "+ reconstruction_time+" \npatch_time: "+ patch_time
    #output = "Policy has been created with values %s" %values
    output = json.dumps(output, default=date_handler)
    return HttpResponse(output)


@login_required
def delete_policy(request):
    current_user = request.user
    policy_id =  request.POST.get("policy_id")
    PolicyManager.objects.filter(user_id=current_user.id, policy_id=policy_id).delete()
    output = list(PolicyManager.objects.filter(user_id=current_user.id).values().order_by('policy_id').reverse())
    output = json.dumps(output, default=date_handler)
    return HttpResponse(output)

@login_required
def is_policy_exist(request):

    current_user = request.user
    size = request.POST.get("size")
    reconstruction_time = request.POST.get("reconstruction_time")
    patch_time = request.POST.get("patch_time")
    addpolicy = size + reconstruction_time + patch_time
    print addpolicy
    output = list(PolicyManager.objects.filter(user_id=current_user.id).values().order_by('policy_id').reverse())
    print output
    policydetails = []
    for policyobj in output:
        policyparams = policyobj['size'] + policyobj['reconstruction_time'] + policyobj['patch_time']
        policydetails.append(policyparams)

    print len(policydetails)
    if len(policydetails) == 7:
        result = 2
    elif addpolicy in policydetails:
        result = 1
        print "policy exist"
    # print output.size,output.reconstruction_time,output.patch_time
    else:
        result = 3
    # print result
    return HttpResponse(result)


