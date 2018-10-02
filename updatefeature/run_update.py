#! /usr/bin/python3

import sys
import subprocess as sp
import os
import time

#Log options - file or stderr
logopt = 'file'
loghandle = None


def get_log_handle():
    global loghandle
    if not loghandle:
        if logopt == 'file':
            loghandle = open('/home/pi/updates/update.log', 'a')
        else:
            loghandle = sys.stderr
    return loghandle


def log(logstr):
    get_log_handle().write(logstr)


def close_and_exit(status):
    log('Exiting with code ' + str(status) + '\n')
    try:
        loghandle.close()
    except:
        pass
    sys.exit(status)

# PUT request
# stderr is used for logging, stdout is used for communication with client
if sys.argv[1] == 'put':
    updatedir = '/home/pi/updates'
    #Get params and values
    params = {}
    while True:
        data = sys.stdin.readline()
        if data == '\n':
            break
        params[data.split(':', 1)[0]] = data.split(':', 1)[1].strip()

    log(str(params) + '\n')

    #If sender is not registred do not accept file
    verified = False
    with open('/home/pi/resinos-haltestellensensor/updatefeature/deviceRegistry', 'r') as reader:
        for line in reader:
            if params['From'].find(line.rstrip()):
                verified = True
                break

    if not verified:
        sys.stderr.write('Socket ' + params['From'] + ' is not registered as a trusted device! Exiting...\n')
        sys.exit(1)

    else:

        #Send OK to start transfer of data
        sys.stdout.write('OK\n')
        sys.stdout.flush()

        #Write the file to disk (first to temporary file, rename after download completed)
        updatefilepath = os.path.join(updatedir, params['Name'])
        tmpupdatefilepath = updatefilepath + '.part'
        #Write block by block (65536 byte)
        with open(tmpupdatefilepath, 'wb') as writer:
            data = sys.stdin.buffer.read(65536)  # 2**16
            while data != b'':
                writer.write(data)
                data = sys.stdin.buffer.read(65536)  # 2**16
            log('File transmission complete...\n')
            os.rename(tmpupdatefilepath, updatefilepath)

        # Run update process
        log('Update file received. Starting update...\n')
        output = ''
        imgtarname = params['Name'][:params['Name'].rfind('.')] + '.tar'
        imgtarpath = os.path.join(updatedir, imgtarname)
        try:
            output = sp.check_output(['p7zip', '-d', '-k', '-f', params['Name']], cwd=updatedir, stderr=sp.STDOUT).decode('ascii')
            log(output)
        except sp.CalledProcessError as ex:
            log(str(ex))
            close_and_exit(1)
        output = sp.check_output(['balena', 'load', '-i', imgtarname], cwd=updatedir, stderr=sp.STDOUT).decode('ascii')
        if output.find('no such file or directory') < 0:
            log("Image loaded successfully! Restarting container...\n")
            try:
                output = sp.check_output(['balena', 'stop', 'hss-app-container'], cwd=updatedir, stderr=sp.STDOUT).decode('ascii')
                log(output)
            except sp.CalledProcessError as ex:
                log(str(ex))
                close_and_exit(1)
            log("Waiting for container to start up again...\n")
            time.sleep(15)
            output = sp.check_output(['balena', 'container', 'ls'], cwd=updatedir, stderr=sp.STDOUT).decode('ascii')
            log('Running containers: ' + output + '\n')
        else:
            output = ''
            log("Loading image failed!\n")
        if output.find('hss-app-container') > 0:
            log('Update successful! Cleaning up...\n')
            try:
                if os.path.exists(updatefilepath):
                    os.remove(updatefilepath)
                if os.path.exists(imgtarpath):
                    os.remove(imgtarpath)
                status = sp.call(['balena', 'image', 'prune', '-f'])
                log('Cleanup finished! Exiting...\n')
                close_and_exit(0)
            except:
                pass
            log('Cleanup could not be finished. Please clean up manually! Exiting...\n')
            close_and_exit(0)

        else:
            log('Update unsuccessful. Checking status of old container...')
            output = sp.check_output(['balena', 'container', 'ls'], cwd=updatedir).decode('ascii')
            if output.find('hss-app-container') > 0:
                log('Old container still up and running! Exiting...')
                sys.exit(1)
            log('Old container not up and running! Please revert manually! Exiting...\n')
            close_and_exit(1)
