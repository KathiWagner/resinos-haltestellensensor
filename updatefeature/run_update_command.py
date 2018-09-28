import subprocess as sp
import json
import os
import io
import sys


if __name__ == "__main__":
    output = sp.check_output(["balena", "volume", "inspect", "framectrdata"])
    volumeinfo = json.loads(output.decode('ascii'))
    print('Volumeinfo: ' + str(volumeinfo))
    mountpoint = volumeinfo[0]["Mountpoint"]
    with open(os.path.join(mountpoint, 'update.command'), "r") as cmdreader:
        status = -1
        cmd = cmdreader.readline().strip('\r\n \t')
        print('Got command: ' + cmd)
        if cmd.startswith("bluetooth:"):
            arg = cmd[cmd.find(" ")+1:].strip()
            if arg.startswith("on"):
                #print('Running: echo -e "power on\ndiscoverable on\nquit" | sudo bluetoothctl')
                status = sp.call(['echo', '-e', '"power on\ndiscoverable on\nquit"', '|', 'bluetoothctl'])
                if status == 0:
                    # obexp = sp.Popen(['obexpushd', '-B', '-o', '/home/pi/updates', '-s', 'put',
                    #                   '/home/pi/resinos-haltestellensensor/updatefeature/run_update.py',
                    #                   '-p', '/home/pi/updates/obexpushdpid.txt'])
                    # print("Started bluetooth file server!")
                    # print(obexp.stderr)
                    # obexp.wait()
                    # sp.Popen(['obexpushd', '-B', '-d', '-o', '/home/pi/updates', '-s', 'put',
                    #           '/home/pi/resinos-haltestellensensor/updatefeature/run_update.py',
                    #           '-p', '/home/pi/updates/obexpushdpid.txt'], close_fds=True)
                    sp.Popen(['obexpushd', '-B', '-d', '-o', '/home/pi/updates', '-s',
                              '/home/pi/resinos-haltestellensensor/updatefeature/run_update_in_shell.sh',
                              '-p', '/home/pi/updates/obexpushdpid.txt'], close_fds=True)

            elif arg.startswith("off"):
                #print('Running: echo -e "discoverable off\npower off\nquit" | sudo bluetoothctl')
                status = sp.call(['echo', '-e', '"discoverable off\npower off\nquit"', '|', 'bluetoothctl'])
            else:
                print('Invalid argument "' + arg + '" for "bluetooth" command!')

        if status == -1:
            print("Invalid command " + cmd + " received!")
        elif status > 0:
            print("Command " + cmd + " failed with exit status " + str(status))
        else:
            print("Command " + cmd + " was executed successfully!")