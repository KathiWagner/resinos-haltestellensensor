import subprocess as sp
import json
import os


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
            pidpath = '/home/pi/updates/obexpushdpid.txt'
            arg = cmd[cmd.find(" ")+1:].strip()
            if arg.startswith("on"):
                #print('Running: echo -e "power on\ndiscoverable on\nquit" | sudo bluetoothctl')
                status = sp.call(['echo', '-e', '"power on\ndiscoverable on\nquit"', '|', 'bluetoothctl'])
                if status == 0:
                    #Spawn detached obexpushd process for receiving files via bluetooth
                    sp.Popen(['obexpushd', '-B', '-d', '-o', '/home/pi/updates', '-s',
                              '/home/pi/resinos-haltestellensensor/updatefeature/run_update_in_shell.sh',
                              '-p', pidpath], close_fds=True)

            elif arg.startswith("off"):
                if os.path.exists(pidpath):
                    with open(pidpath, 'r') as reader:
                        pid = reader.read().rstrip()
                        sp.call(['kill', '-9', pid])
                os.remove('/home/pi/updates/*')
                status = sp.call(['echo', '-e', '"discoverable off\npower off\nquit"', '|', 'bluetoothctl'])
            else:
                print('Invalid argument "' + arg + '" for "bluetooth" command!')

        if status == -1:
            print("Invalid command " + cmd + " received!")
        elif status > 0:
            print("Command " + cmd + " failed with exit status " + str(status))
        else:
            print("Command " + cmd + " was executed successfully!")
