from JobManager.models import *
from SoftwareManager.models import *
from util.constants import *
import os
import subprocess
import csv
import platform
global time_cmd

if  platform.uname()[0] == "Linux":
    time_cmd="/usr/bin/time"
else:
    time_cmd="time"

def prepare_fm_for_each_job(job_id):
    directory = JOB_ROOT_PATH + str(job_id)
    if not os.path.exists(directory):
        os.makedirs(directory)

    files_id = ExecuteJob.objects.filter(job_id=job_id).values('file1_id','file2_id')
    file1_id, file2_id = files_id[0]['file1_id'], files_id[0]['file2_id']
    file1_path = (UploadedSoftwareObject.objects.filter(id=file1_id).values('file'))[0]['file']
    file1_name = (UploadedSoftwareObject.objects.filter(id=file1_id).values('filename'))[0]['filename']
    file2_path = (UploadedSoftwareObject.objects.filter(id=file2_id).values('file'))[0]['file']
    file2_name = (UploadedSoftwareObject.objects.filter(id=file2_id).values('filename'))[0]['filename']
    file1_path, file2_path = '' + 'media/' + file1_path, '' + 'media/' + file2_path

    job_dir = MEDIA_PATH + 'jobs/' +str(job_id) + '/'
    copy_file1_command = 'cp '+file1_path+' '+job_dir+file1_name
    print "2222222222222222222222",file1_path, file1_name, copy_file1_command
    subprocess.check_call([copy_file1_command], shell=True)

    copy_file2_command = 'cp '+file2_path+' '+job_dir+file2_name
    subprocess.check_call([copy_file2_command], shell=True)

    return None


def prepare_fm_for_each_tool(job_id, tool):
    directory = JOB_ROOT_PATH + str(job_id) + '/' + tool
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


def create_delta_patch(job_id, tool, tool_directory_path):
    print tool
    job_dir = MEDIA_PATH + 'jobs/' +str(job_id) + '/'
    files_id = ExecuteJob.objects.filter(job_id=job_id).values('file1_id','file2_id')
    file1_id, file2_id = files_id[0]['file1_id'], files_id[0]['file2_id']
    file1_name = (UploadedSoftwareObject.objects.filter(id=file1_id).values('filename'))[0]['filename']
    file2_name = (UploadedSoftwareObject.objects.filter(id=file2_id).values('filename'))[0]['filename']
    file1_path = job_dir+file1_name
    file2_path = job_dir+file2_name

    if tool == 'bsdiff':
        delta_parameters = run_bsdiff(job_id, job_dir, file1_name, file2_name, None)
        return delta_parameters

    if tool == 'xdelta3':
        delta_parameters = run_xdelta3(job_id, job_dir, file1_name, file2_name, None)
        return delta_parameters

    if tool == 'vcdiff':
        delta_parameters = run_vcdiff(job_id, job_dir, file1_name, file2_name, None)
        return delta_parameters


def fetch_delta_times(job_dir, delta_time_path, patch_time_path):
    delta_time_log_path = job_dir + delta_time_path
    patch_time_log_path = job_dir + patch_time_path
    delta_times = [get_time_from_log(delta_time_log_path), get_time_from_log(patch_time_log_path)]
    return delta_times


def create_job_description_file(job_id):

    return None


def get_file_size(job_dir, path):
    path = job_dir + path
    print "PATH", path
    print os.getcwd()
    new_path = os.getcwd()+'/'
    print "\n NEW PATH ", new_path, " 		PATH	",path, "\n"
    os.chdir(new_path)
    delta_file_stat = os.stat(path)
    delta_size = delta_file_stat.st_size
    return delta_size


def get_time_from_log(logPath):
    timeD = {}
    with open(logPath) as timelogfile:
        timereader = csv.reader(timelogfile, delimiter='\t')
        for row in timereader:
            try:
                if row[0] and row[1]:
                    timeD[row[0]] = row[1]
            except IndexError:
                pass
    time = timeD['real']
    return time


def find_delta_parameters(job_id, job_dir, delta_path, delta_time_path, patch_time_path, tool):

    delta_size = get_file_size(job_dir, delta_path)
    delta_times = fetch_delta_times(job_dir, delta_time_path, patch_time_path)
    delta_time, patch_time = delta_times[0], delta_times[1]
    delta_parameters = [delta_size, delta_time, patch_time]
    # delta_parameters = [delta_size, "40 seconds", "30 seconds"]
    return delta_parameters


def run_bsdiff(job_id, job_dir, file1_name, file2_name, options):
    exe_flag = 1
    p_remove = subprocess.Popen(['rm', './bsdiff/'+str(job_id) + '_patch.bsdiff'],cwd=job_dir,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out_remove, err_remove = p_remove.communicate()

    delta_path = 'bsdiff/' + str(job_id) + '_patch.bsdiff'
    delta_time_path = 'bsdiff/' + str(job_id) + '_bsdiff_delta_time.csv'
    patch_time_path = 'bsdiff/' + str(job_id) + '_bsdiff_patch_time.csv'

    command_delta = time_cmd + ' -f ' + ' "real\t%e \n user\t%U\n sys\t%S\" ' + ' /usr/bin/bsdiff ' + ' ' + file1_name + ' ' + file2_name + ' ' + delta_path + ' 2> '+ delta_time_path
    delta = subprocess.Popen(command_delta, shell=True, cwd=job_dir)
    status_code = delta.wait()
    if  status_code:
        exe_flag = 0
        return exe_flag

    file2_recons_path = './bsdiff/recon_'+file2_name

    command_patch = time_cmd + ' -f ' + ' "real\t%e \n user\t%U\n sys\t%S" ' + ' /usr/bin/bspatch ' + ' ' + file1_name + ' '  + file2_recons_path + ' ' + delta_path  +  ' 2> ' + patch_time_path

    delta = subprocess.Popen(command_patch , shell=True, cwd=job_dir)
    status_code = delta.wait()
    if  status_code:
        exe_flag = 0
        return exe_flag

    delta_parameters = find_delta_parameters(job_id, job_dir, delta_path, delta_time_path, patch_time_path, 'bsdiff')
    return delta_parameters


def run_xdelta3(job_id, job_dir, file1_name, file2_name, options):
    exe_flag = 1
    p_remove = subprocess.Popen(['rm', './xdelta3/'+str(job_id) + '_patch.xdelta3'],cwd=job_dir,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out_remove, err_remove = p_remove.communicate()
    delta_path = 'xdelta3/' + str(job_id) + '_patch.xdelta3'
    delta_time_path = 'xdelta3/' + str(job_id) + '_xdelta3_delta_time.csv'
    patch_time_path = 'xdelta3/' + str(job_id) + '_xdelta3_patch_time.csv'

    command_delta = time_cmd + ' -f ' + ' "real\t%e \n user\t%U\n sys\t%S\" ' + ' /usr/bin/xdelta3 -s ' + ' ' + file1_name + ' ' + file2_name + ' ' + delta_path + ' 2> '+ delta_time_path
    delta = subprocess.Popen(command_delta, shell=True, cwd=job_dir)
    status_code = delta.wait()
    if  status_code:
        exe_flag = 0
        return exe_flag

    file2_recons_path = './xdelta3/recon_'+file2_name
    command_patch = time_cmd + ' -f ' + ' "real\t%e \n user\t%U\n sys\t%S" ' + ' /usr/bin/xdelta3 -d -s ' + ' ' + file1_name + ' ' + delta_path +  ' ' + file2_recons_path  + ' 2> ' + patch_time_path
    print "**************"
    print command_patch, "\n", job_dir
    print "**************"
    patch = subprocess.Popen(command_patch, shell=True, cwd=job_dir)
    status_code = patch.wait()
    if  status_code:
        exe_flag = 0
        return exe_flag
    delta_parameters = find_delta_parameters(job_id, job_dir, delta_path, delta_time_path, patch_time_path, 'xdelta3')
    return  delta_parameters


def run_vcdiff(job_id, job_dir, file1_name, file2_name, options):

    exe_flag = 1
    p_remove = subprocess.Popen(['rm', './vcdiff/'+str(job_id) + '_patch.vcdiff'],cwd=job_dir,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out_remove, err_remove = p_remove.communicate()
    delta_path = 'vcdiff/' + str(job_id) + '_patch.vcdiff'
    delta_time_path = 'vcdiff/' + str(job_id) + '_vcdiff_delta_time.csv'
    patch_time_path = 'vcdiff/' + str(job_id) + '_vcdiff_patch_time.csv'

    command_delta = time_cmd + ' -f ' + ' "real\t%e \n user\t%U\n sys\t%S\" ' + ' /usr/local/bin/vcdiff encode -dictionary ' + file1_name + ' < ' + file2_name + ' > ' + delta_path + ' 2> '+ delta_time_path
    delta = subprocess.Popen(command_delta, shell=True, cwd=job_dir)
    status_code = delta.wait()
    if  status_code:
        exe_flag = 0
        return exe_flag
    file2_recons_path = './vcdiff/recon_'+file2_name


    command_patch = time_cmd + ' -f ' + ' "real\t%e \n user\t%U\n sys\t%S" ' + ' /usr/local/bin/vcdiff decode -dictionary' + ' ' + file1_name + ' < ' + delta_path + ' > ' \
                    + file2_recons_path + ' 2>  '+ patch_time_path
    patch = subprocess.Popen(command_patch, shell=True, cwd=job_dir)
    status_code = patch.wait()
    if  status_code:
        exe_flag = 0
        return exe_flag
    delta_parameters = find_delta_parameters(job_id, job_dir, delta_path, delta_time_path, patch_time_path, 'vcdiff')

    return delta_parameters
