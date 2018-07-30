from django.shortcuts import render
from django.contrib.auth.views import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from custom_registration.models import GetApp
from django.http import HttpResponseRedirect


def selectuserapp(request):
    # Extract app from table
    # based on the app extracted send html file
    # first create for software manager
    output = list(GetApp.objects.filter(user=request.user).values())
    app = None
    if output :
        app = output[0]['Role']
        print output[0]['Role']
        request.session["User_Role"] = app

    return render(request,'DeltaCompressionWebtool/home.html')