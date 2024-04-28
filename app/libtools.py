import pip
import os
import platform
import stat
import time







def installupdate(package):
    print("Checking requirement: ", package)
    
    if hasattr(pip, 'main'):
        pip.main(['install', '--upgrade',package])
    else:
        pip._internal.main(['install','--upgrade', package])
    






def file_age_in_days(pathname):
    return (time.time() - os.stat(pathname)[stat.ST_MTIME])/86400




if(file_age_in_days("requirements.txt")>1):
    requirements = open("requirements.txt",'r')
    libraries = requirements.readlines()

    for lib in libraries:
        installupdate(lib) 