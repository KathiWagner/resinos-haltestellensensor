#! /usr/bin/python3

import sys
import subprocess as sp
import os
import time

params = {}
params['Name'] = 'hss-app-2018-09-21.7z'
updatedir = '/home/pi/updates'
updatefilepath = os.path.join(updatedir, params['Name'])

# Run update process
sys.stderr.write('Update file received. Starting update...\n')
output = ''
imgtarname = params['Name'][:params['Name'].rfind('.')] + '.tar'
imgtarpath = os.path.join(updatedir, imgtarname)
sp.call(['p7zip', '-d', '-k', '-f', params['Name']], cwd=updatedir, stdout=sys.stderr)
sp.call(['balena', 'load', '-i', imgtarname], cwd=updatedir, stdout=sys.stderr)
sp.call(['balena', 'stop', 'hss-app-container'], cwd=updatedir, stdout=sys.stderr)
sys.stderr.write("Waiting for container to start up again...")
time.sleep(15)
output = sp.check_output(['balena', 'container', 'ls'], cwd=updatedir).decode('ascii')
sys.stderr.write('Running containers: ' + output)
if output.find('hss-app-container') > 0:
    sys.stderr.write('Update successful! Cleaning up...\n')
    try:
        if os.path.exists(updatefilepath):
            os.remove(updatefilepath)
        if os.path.exists(imgtarpath):
            os.remove(imgtarpath)
        status = sp.call(['balena', 'image', 'prune', '-f'])
        if status == 0:
            sys.stderr.write('Cleanup finished! Exiting...\n')
            sys.exit(0)
    except:
        pass
    sys.stderr.write('Cleanup could not be finished. Please clean up manually! Exiting...\n')
    sys.exit(0)

else:
    sys.stderr.write('Update unsuccessful. Checking status of old container...')
    output = sp.check_output(['balena', 'container', 'ls'], cwd=updatedir).decode('ascii')
    if output.find('hss-app-container') > 0:
        sys.stderr.write('Old container still up and running! Exiting...')
        sys.exit(1)
    sys.stderr.write('Old container not up and running! Please revert manually! Exiting...\n')
    sys.exit(1)
