import subprocess as sp
import json
import os
import time


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
            registrypath = '/home/pi/resinos-haltestellensensor/updatefeature/deviceRegistry'
            arg = cmd[cmd.find(" ")+1:].strip()
            if arg.startswith("on"):
                # Turn bluetooth on
                ps = sp.Popen('bluetoothctl', stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT, bufsize=1)
                ps.stdin.write(b'power on\n')
                ps.stdin.write(b'discoverable on\n')
                out, err = ps.communicate(b'quit\n')
                print(out.decode('utf-8'))
                status = ps.returncode
                if status == 0:
                    #Spawn detached obexpushd process for receiving files via bluetooth
                    sp.Popen(['obexpushd', '-B', '-d', '-o', '/home/pi/updates', '-s',
                              '/home/pi/resinos-haltestellensensor/updatefeature/run_update_in_shell.sh',
                              '-p', pidpath], close_fds=True)

            elif arg.startswith("register"):
                mac = arg[arg.find(" ")+1:].strip()
                registered = False
                print("Registrating device with MAC: " + mac)
                # Add MAC address to registry
                if os.path.exists(registrypath):
                    with open(registrypath, 'r') as reader:
                        for line in reader:
                            if line.rstrip() == mac:
                                registered = True
                                print("Device already registered, nothing to do!")
                                break
                if not registered:
                    with open(registrypath, 'a') as appender:
                        appender.write(mac + '\n')
                        print("Successfully registered device!")
                status = 0

            elif arg.startswith("clearregistry"):
                print("Clearing device registry...")
                with open(registrypath, 'w') as writer:
                    pass
                    print("Success!")
                status = 0

            elif arg.startswith("off"):
                if os.path.exists(pidpath):
                    with open(pidpath, 'r') as reader:
                        pid = reader.read().rstrip()
                        status = sp.call(['kill', '-9', pid])
                        print('Successfully killed obexpushd bluetooth file transfer server!')
                # delete all leftover files except the update log and hidden ones
                files = os.listdir('/home/pi/updates')
                files.remove('update.log')
                for filename in files:
                    if not filename.startswith('.'):
                        path = os.path.join('/home/pi/updates/', filename)
                        print('Removing file: ' + path)
                        os.remove(path)
                # Turn bluetooth off
                ps = sp.Popen('bluetoothctl', stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT, bufsize=1)
                ps.stdin.write(b'discoverable off\n')
                ps.stdin.write(b'power off\n')
                out, err = ps.communicate(b'quit\n')
                print(out.decode('utf-8'))
                status = ps.returncode
            else:
                print('Invalid argument "' + arg + '" for "bluetooth" command!')

        if status == -1:
            print("Invalid command " + cmd + " received!")
        elif status > 0:
            print("Command " + cmd + " failed with exit status " + str(status))
        else:
            print("Command " + cmd + " was executed successfully!")
