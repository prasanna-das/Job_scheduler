import os
import subprocess

print 
print "FROM UTIL:::::"
fstat = os.stat("../media/jobs/19/xdelta3/19_patch.xdelta3")
print fstat.st_size
