import asyncio
import socket
import subprocess
import re
import os
import kasa 
import websockets
import json
import io
import pprint
import dotenv

dotenv.load_dotenv()
WS_HOST = os.getenv('WS_HOST')
WS_PORT = os.getenv('WS_PORT')

# identify eligible smart devices by the manufacturer prefix
TPLink_MACaddr_re = r'54:af:97:a0:\w{2}:\w{2}'


async def serve():
    async with websockets.serve(handler, WS_HOST, WS_PORT):
        await asyncio.Future()


async def handler(webscocket):
    async for message in webscocket:
        print(message)
        if message[0] != '/': continue

        (noun,verb,target,*args) = message.lstrip('/').split('/')

        if noun.lower() == 'power':
            if verb.lower() == 'on': on = True
            if verb.lower() == 'off': on = False
            
            if target.lower() == 'all':
                res, err = await toggleAllDevices(on=on)
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


async def toggleAllDevices(on:bool) -> tuple[str,Exception]:
    Devices = get_TPLink_devices()
    update_coros = [ i.update() for i in Devices ]
    await asyncio.gather(*update_coros)

    if on is True:
        power_coros = [ i.turn_on() for i in Devices ]
    else:
        power_coros = [ i.turn_off() for i in Devices ]

    await asyncio.gather(*power_coros)

    update_coros = [ i.update() for i in Devices ]

    await asyncio.gather(*update_coros)

    allDevices = SmartPlug_fmt(Devices)

    return (
        json.dumps(allDevices), None
        )


async def listAllDevices() -> tuple[str,Exception]:
    Devices = get_TPLink_devices()
    update_coros = [ i.update() for i in Devices ]
    await asyncio.gather(*update_coros)

    allDevices = SmartPlug_fmt(Devices)

    return (
        json.dumps(allDevices), None
        )


def SmartPlug_fmt(Devices):
    _fmt = [
        {
            "alias":        i._sys_info.get("alias"),
            "host":         i.host,
            "dev_name":     i._sys_info.get("dev_name"),
            "is_on":        i.is_on
        }
        for i in Devices
    ]

    try:
        snapshot_device_state(_fmt)
    except Exception as e:
        print(e)

    return _fmt


def snapshot_device_state(Devices:list[dict]) -> None:
    with open('db/stateFile.json', 'w') as stateFile:
        json.dump(Devices, stateFile, indent=4)


def get_TPLink_devices():
    # if your server has multiple interfaces on the same network (e.g., wireless and eth0)
    # the same devices will appear twice as a neighbor -- dedupe by host IP
    results = set()

    for i in subprocess.getoutput('ip neigh show').splitlines():
        host = i.split(' ')
        host.remove('')
        
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
    asyncio.run(serve())