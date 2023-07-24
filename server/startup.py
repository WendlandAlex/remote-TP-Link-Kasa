import subprocess
import json

def bootstrap_devices():
    with open('../server/db/stateFile.json', 'r') as infile:
        Devices = json.load(infile)
        for device in Devices:
            subprocess.check_call(
                ['kasa', '--host', device]
            )

if __name__ == '__main__':
    bootstrap_devices()