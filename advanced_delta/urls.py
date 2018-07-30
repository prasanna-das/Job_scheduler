"""DeltaCompressionWebtool URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from SoftwareManager.views import (
    UploadView, UploadCompleteView
)
from django.conf.urls.static import static

urlpatterns = [

    # Admin URLs
    url(r'^admin/', include(admin.site.urls)),

    # Registration and Sing In URLs
    url(r'^accounts/', include('custom_registration.backends.default.urls')),

    url(r'^password/change/$',
                    auth_views.password_change,
                    name='password_change'),
    url(r'^password/change/done/$',
                    auth_views.password_change_done,
                    name='password_change_done'),
    url(r'^password/reset/$',
                    auth_views.password_reset,
                    name='password_reset'),
    url(r'^accounts/password/reset/done/$',
                    auth_views.password_reset_done,
                    name='password_reset_done'),
    url(r'^password/reset/complete/$',
                    auth_views.password_reset_complete,
                    name='password_reset_complete'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
                    auth_views.password_reset_confirm,
                    name='password_reset_confirm'),
    url(r'^about/$', 'userprofile.views.about', name='about'),


    # Dashboard URLs - Landing software application
    url(r'^$', 'policy_manager.views.home', name='home'),
    url(r'^home/$', 'policy_manager.views.home', name='home'),
    url(r'^profile/$', 'userprofile.views.profile', name='profile'),
    url(r'^selectuserapp/$', 'userprofile.views.selectuserapp', name='selectuserapp'),
    url(r'^DeleteImage/$','userprofile.views.delete', name='delete'),

    # URLs for SoftwareObject upload and list of files
    url(r'^upload/$', 'SoftwareManager.views.upload', name='upload'),
    #url(r'^upload/init_data/$', 'softwareObject.views.init_data', name='init_data'),
    url(r'^upload/api/chunked_upload/?$',
        UploadView.as_view(), name='api_chunked_upload'),
    url(r'^upload/api/chunked_upload_complete/?$',
        UploadCompleteView.as_view(),name='api_chunked_upload_complete'),
    url(r'^delete_file/$', 'SoftwareManager.views.delete_file', name='delete_file'),
    url(r'^profile/$', 'userprofile.views.profile', name='profile'),
    # URLs for Performing Delta Compression Jobs
    url(r'^job_manager/$', 'JobManager.views.delta_analysis', name='jobs'),
    url(r'^job_manager/file_list/$', 'JobManager.views.file_list', name='file_list'),
    url(r'^upload/verify_duplicate_file/$', 'SoftwareManager.views.verify_duplicate_file', name='verify_duplicate_file'),
    url(r'^execute_algos/$', 'JobManager.views.execute', name='execute'),
    url(r'^delete_job/$', 'JobManager.views.delete_job', name='delete_job'),
    url(r'^job_manager/get_policy_list/$', 'JobManager.views.get_policy_list', name='get_policy_list'),
    url(r'^execution_status/$', 'JobManager.views.execution_status', name='execution_status'),
    url(r'^policy_manager/$', 'policy_manager.views.policy_manager', name='policy_manager'),
    url(r'^create_policy/$', 'policy_manager.views.create_policy', name='create_policy'),
    url(r'^delete_policy/$', 'policy_manager.views.delete_policy', name='delete_policy'),
     url(r'^policy_manager/is_policy_exist/$', 'policy_manager.views.is_policy_exist', name='is_policy_exist'),

                  # URLs for Viewing results of Delta Compression tasks
    url(r'^report/$', 'report.views.report', name='report'),
    url(r'^report/generate_report/$', 'report.views.generate_report', name='generate_report'),
    url(r'^report/delete_report/$', 'report.views.delete_report', name='delete_report'),
    url(r'^downloadfile/$', 'report.views.downlolad_attachment', name='downlolad_attachment'),


    # URLs for static files
    url(r'^static/(.*)$',
        'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT, 'show_indexes': False}),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
