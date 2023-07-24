import asyncio
import json
import os
import re
import socket
import subprocess

import dotenv
from flask import Flask, request, Response
import kasa

dotenv.load_dotenv()
WS_HOST = os.getenv('WS_HOST')
WS_PORT = os.getenv('WS_PORT')
MAPPINGS_ENABLED = bool(
    os.getenv('MAPPINGS_ENABLED', False)
)
if MAPPINGS_ENABLED is True:
    with open('db/mappings.json', 'r') as infile:
        mappings = json.load(infile)

# identify eligible smart devices by the manufacturer prefix
TPLink_MACaddr_re = [
    r'54:af:97:a0:\w{2}:\w{2}',
    r'1c:61:b4:a7:\w{2}:\w{2}'
]

# Devices
Devices = []


def get_TPLink_devices():
    # if your server has multiple interfaces on the same network (e.g., wireless and eth0)
    # the same devices will appear twice as a neighbor -- dedupe by host IP
    results = set()

    for i in subprocess.getoutput('ip neigh show').splitlines():
        orig = i.split(' ')
        host = [x for x in orig if x != '']

        ip_returns = ['ip_addr', 'host_type', 'interface', 'ip_addr_type', 'mac_addr', 'status']

        # validate ip_address
        try:
            socket.inet_aton(host[0])
        except OSError:
            continue

        # validate MAC address
        try:
            if any([re.fullmatch(i, host[4]) for i in TPLink_MACaddr_re]):
                results.add(host[0])

        except IndexError:
            continue
        except Exception:
            raisef

    return [kasa.SmartPlug(i) for i in results]


async def update_TPLink_devices(Devices=None):
    await asyncio.gather(*[i.update() for i in Devices])


# app
app = Flask(__name__)

@app.route('/health', methods=['GET'])
async def healthCheck():
    return Response(json.dumps({"healthy": True}), status=200, mimetype='application/json')


@app.route('/', methods=['GET'])
async def getAll():
    (res, err) = await listAllDevices()

    if err is None:
        return Response(res, status=200, mimetype='application/json')
    else:
        print(err)
        return Response(err, status=404, mimetype='text/plain')


@app.route('/submit', methods=['POST'])
async def handleFormSubmit():
    data = request.get_json()
    allHosts = False

    targets = [i for i in data.get('target')]
    power = data.get('power', 'off')

    if 'all' in targets:
        allHosts = True
        hosts = []
    else:
        hosts = [
            mappings.get(i, {}).get('host', '') for i in targets
        ]

    if power.lower() == 'on':
        on = True
    else:
        on = False

    (res, err) = await toggleDevices(on=on, allHosts=allHosts, targets=hosts)

    if err is None:
        return Response(res, status=200, mimetype='application/json')
    else:
        print(err)
        return Response(err, status=404, mimetype='text/plain')


async def toggleDevices(on=False, allHosts=False, targets=[]):
    if allHosts is True:
        Devices = get_TPLink_devices()
    else:
        Devices = [i for i in get_TPLink_devices() if i.host in targets]

    await asyncio.gather(*[i.update() for i in Devices])

    if on is True:
        power_coros = [i.turn_on() for i in Devices]
    else:
        power_coros = [i.turn_off() for i in Devices]

    await asyncio.gather(*power_coros)

    await asyncio.gather(*[i.update() for i in Devices])

    return (
        json.dumps(
            SmartPlug_fmt(Devices, mappings_enabled=MAPPINGS_ENABLED)
        ), None
    )


async def listAllDevices():
    Devices = get_TPLink_devices()
    update_coros = [i.update() for i in Devices]
    await asyncio.gather(*update_coros)

    allDevices = SmartPlug_fmt(Devices, mappings_enabled=MAPPINGS_ENABLED)

    return (
        json.dumps(allDevices), None
    )


def SmartPlug_fmt(Devices, mappings_enabled: bool):
    _fmt = []

    for i in Devices:
        dev = {
            "alias": i._sys_info.get("alias"),
            "host": i.host,
            "dev_name": i._sys_info.get("dev_name"),
            "is_on": i.is_on
        }
        if mappings_enabled is True:
            parts = i._sys_info.get("alias").split(".")
            plugAlias = parts[0]
            roomName = parts[1]
            attachedDevice = parts[2]
            MACLast4 = parts[3]
            dev.update({
                "room": roomName,
                "attachedDevice": attachedDevice,
                "MACLast4": MACLast4
            })
        _fmt.append(dev)

    return _fmt


if __name__ == '__main__':
    Devices = get_TPLink_devices()
    app.run(
        host=os.getenv('WS_HOST'),
        port=os.getenv('WS_PORT'),
        debug=False,
        use_reloader=False
    )
