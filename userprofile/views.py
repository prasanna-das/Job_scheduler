from django.shortcuts import render, redirect
from django.contrib.auth.views import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from custom_registration.models import GetApp
from .form import UserProfileForm
from advanced_delta import settings
from django.shortcuts import render_to_response
from .models import UserProfile
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
import os

defaultimage = 'userprofile/userphoto/no-image-icon-hi.png'

def about(request):
    return render(request,'DeltaCompressionWebtool/about.html')

def selectuserapp(request):
    # Extract app from table
    # based on the app extracted send html file
    # first create for software manager
   # session_env(request)
    return render(request,'DeltaCompressionWebtool/home.html')

def session_env(request):
    output = list(GetApp.objects.filter(user=request.user).values())
    app = None
    if output:
        app = output[0]['Role']
        print output[0]['Role']
        request.session["User_Role"] = app

    userid = request.user.id
    userprof = UserProfile.objects.filter(user=userid)[0]
    firstname = userprof.firstname
    if  firstname is None:
        request.session["firstname"] = request.user.first_name
    lastname = userprof.lastname
    if lastname is None:
        request.session["lastname"] = request.user.last_name
    request.session["profilephoto"] = userprof.photo.url
    return None

@login_required
#@csrf_exempt
def profile(request):
    '''
    Simple   view method for uploading an image

    '''
    global defaultimage
   # import pdb
   # pdb.set_trace()
    print "profile entered"
    userid = request.user.id
    usrname = request.user.username
    userprofobj = UserProfile.objects.filter(user=userid)[0]
    id = userprofobj.id
    form = UserProfileForm(request.POST or None , request.FILES or None, instance=userprofobj)
    if request.method == 'POST':
        print "form entered"

        if form.is_valid() and form.is_multipart():

            instance = form.save(commit=False)
            print request.FILES['photoname']
            if ( request.FILES['photoname']):
                imagefile = save_file(request.FILES['photoname'], id)

            firstname = request.POST.get("firstname")
            lastname = request.POST.get("lastname")

            instance.firstname = firstname
            instance.lastname = lastname
            instance.photo = imagefile
            instance.save()
           # print "url" + instance.photo.url + "path " + instance.photo.path

           # uploaded_path =  save_file(request.FILES['photo'], usrname)
           # profileobj = UserProfile.objects.filter(user=userid)[0]

        else:
            return HttpResponse('Invalid image')
    userprof = getprofilephoto(request)
    firstname = userprof.firstname
    lastname = userprof.lastname
    if firstname is None:
        userprof.firstname = request.user.first_name
    if lastname is None:
        userprof.lastname = request.user.last_name
    userprof.save()
    print firstname,lastname
    userprof = getprofilephoto(request)
    profiledetail = {'form': form }
    profiledetail["profileinst"] = userprof
    request.session["firstname"] = userprof.firstname
    request.session["lastname"] = userprof.lastname
    request.session["profilephoto"] = userprof.photo.url
    print userprof.photo.url
    if userprof.photo.url != '/media/'+defaultimage:
        profiledetail['deletebt'] = 1
    else :
        profiledetail['deletebt'] = 0


    return render_to_response('DeltaCompressionWebtool/profile.html', profiledetail, context_instance=RequestContext(request))

def  getprofilephoto(request):
    #import pdb
    #pdb.set_trace()
    userid = request.user.id
    userprof = UserProfile.objects.filter(user=userid)[0]
    return  userprof

def save_file(file, id):
    ''' Little helper to save a file
    '''
    #import pdb
    #pdb.set_trace()
    filename = file._get_name()
    photodir = "/userprofile/userphoto/" + str(id) + "/"
    uploaddir = settings.MEDIA_ROOT + photodir
    if not os.path.exists(uploaddir):
         os.makedirs(uploaddir)
    #filepath = photodir + str(filename)
    uploaded_path = uploaddir  + str(filename)
    fd = open(uploaded_path, 'wb')
    for chunk in file.chunks():
        fd.write(chunk)
    fd.close()
    # print uploaded_path
    file.path = uploaded_path
    return file


def delete(request):
  # import pdb
  # pdb.set_trace()
   global defaultimage
   userid = request.user.id
   uf = UserProfile.objects.get(user= userid)
   imagepath = uf.photo.path
   os.remove(imagepath)
   uf.photo = defaultimage
   uf.save()
   return redirect('/profile')