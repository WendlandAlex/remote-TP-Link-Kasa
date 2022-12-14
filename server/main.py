import asyncio
import socket
import subprocess
import re
import os
import kasa 
import websockets
import json
import dotenv

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
TPLink_MACaddr_re = r'54:af:97:a0:\w{2}:\w{2}'


async def serve():
    async with websockets.serve(handler, WS_HOST, WS_PORT) as conn:
        sockinfo = conn.sockets[0].getsockname()
        print(f'listening on socket: ws://[{sockinfo[0]}]:{sockinfo[1]}')
        
        await asyncio.Future()


async def handler(webscocket):
    async for message in webscocket:
        print(message)
        if message[0] != '/': continue

        (noun,verb,target,*args) = message.lstrip('/').split('/')

        if target.lower() == 'all':
            host = 'all'
        else:
            host = db_lookup({'room': target.lower()}, 'host')

        if noun.lower() == 'power':
            if verb.lower() == 'on': on = True
            if verb.lower() == 'off': on = False

            res, err = await toggleDevices(on=on, target=host)
            if err is None:
                await webscocket.send(res)
            else:
                print(err)
                await webscocket.send(err.status)

        if noun.lower() == 'devices':
            if verb.lower() == 'list':
                if target.lower() == 'all' and args == []:
                    res, err = await listAllDevices()
                    if err is None:
                        await webscocket.send(res)
                    else:
                        print(err)
                        await webscocket.send(err.status)


async def toggleDevices(on:bool,target):
    if target == 'all':
        Devices = get_TPLink_devices()
    else:
        Devices = [ i for i in get_TPLink_devices() if i.host == target ]

    update_coros = [ i.update() for i in Devices ]
    await asyncio.gather(*update_coros)

    if on is True:
        power_coros = [ i.turn_on() for i in Devices ]
    else:
        power_coros = [ i.turn_off() for i in Devices ]

    await asyncio.gather(*power_coros)

    update_coros = [ i.update() for i in Devices ]

    await asyncio.gather(*update_coros)

    allDevices = SmartPlug_fmt(Devices, mappings_enabled=MAPPINGS_ENABLED)

    return (
        json.dumps(allDevices), None
        )


async def listAllDevices():
    Devices = get_TPLink_devices()
    update_coros = [ i.update() for i in Devices ]
    await asyncio.gather(*update_coros)

    allDevices = SmartPlug_fmt(Devices, mappings_enabled=MAPPINGS_ENABLED)

    return (
        json.dumps(allDevices), None
        )


def SmartPlug_fmt(Devices, mappings_enabled:bool):
    _fmt = []

    for i in Devices:
        dev = {
            "alias":        i._sys_info.get("alias"),
            "host":         i.host,
            "dev_name":     i._sys_info.get("dev_name"),
            "is_on":        i.is_on
        }
        if mappings_enabled is True:
            dev.update({
                "room": mappings.get(i.host).get("room")
                })
        _fmt.append(dev)
    
    try:
        snapshot_device_state(_fmt)
    except Exception as e:
        print(e)

    return _fmt


def snapshot_device_state(Devices):
    # if no devices are discovered, don't destroy the snapshot of the last known devices
    if Devices != []:
        with open('db/stateFile.json', 'w') as backup:
            json.dump(Devices, backup, indent=4)

def db_lookup(search_key_value, result_key):
    with open('db/stateFile.json', 'r') as infile:
        stateFile = json.load(infile)

        for key,value in search_key_value.items():
            result = []
            for device in stateFile:
                for k,v in device.items():
                    k = k.lower()
                    v = str(v).lower()

                    if k == key and v == value:
                        result.append(device)
            
            if len(result) > 0:
                return result[0][result_key]

def get_TPLink_devices():
    # if your server has multiple interfaces on the same network (e.g., wireless and eth0)
    # the same devices will appear twice as a neighbor -- dedupe by host IP
    results = set()

    for i in subprocess.getoutput('ip neigh show').splitlines():
        orig = i.split(' ')
        host = [ x for x in orig if x != '' ]
        
        ip_returns = ['ip_addr', 'host_type', 'interface', 'ip_addr_type', 'mac_addr', 'status']

        # validate ip_address
        try:
            socket.inet_aton(host[0])
        except OSError:
            continue

        # validate MAC address
        try:
            if re.fullmatch(TPLink_MACaddr_re, host[4]):
                results.add(host[0])
        
        except IndexError:
            continue
        except Exception:
            raise

    return [ kasa.SmartPlug(i) for i in results ]
    

if __name__ == '__main__':
    import startup
    startup.bootstrap_devices()
    asyncio.run(serve())
