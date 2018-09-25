import subprocess as sp
import json

if __name__ == "__main__":
    output = sp.check_output(["balena", "volume", "inspect", "framectrdata"])
    volumeinfo = json.parse(output)
    mountpoint = volumeinfo["Mountpoint"]
    with open(mountpoint, "r") as cmdreader:
        status = -1
        cmd = cmdreader.readline()
        if cmd.startswith("bluetooth:"):
            if cmd[cmd.find(" ")+1:] == "on":
                status = sp.call('echo -e "power on\ndiscoverable on\nquit" | sudo bluetoothctl')
            elif cmd[cmd.find(" ")+1:] == "off":
                status = sp.call('echo -e "discoverable off\npower off\nquit" | sudo bluetoothctl')

        if status == -1:
            print("Invalid command " + cmd + "received!")
        elif status > 0:
            print("Command " + cmd + " failed with exit status " + str(status))
        else:
            print("Command " + cmd + " was executed successfully!")