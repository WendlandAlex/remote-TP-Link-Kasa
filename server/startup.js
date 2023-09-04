const {execSync} = require('child_process');
const {writeFileSync} = require('fs');
const {Client} = require('tplink-smarthome-api');
const {parseAlias} = require("./utils");

// call shell command in child process
// example of `ip neigh show` output:
// 192.168.1.132 dev em2 lladdr 1c:61:b4:a7:22:10 REACHABLE
const showNeighbors = () => {
    return execSync('ip neigh show')
        .toString()
        .split('\n')
        .map(i => {
            return {ip: i.split(' ')[0], mac: i.split(' ')[4]}
        })
}

// push a promise of client.getDevice for each neighbor onto the stack
// to be awaited in bulk via promise.allSettled()
const discoverDevicesPromises = (client, candidateDevices = [{ip: '169.254.169.254'}]) => {
    return candidateDevices.reduce((accumulator, neighbor) => {
        accumulator.push(client.getDevice({host: neighbor.ip}))
        return accumulator
    }, []);
}

// return a copy of the array where only fulfilled promises are included
// return the .value attribute [a device]
const getFulfilledPromises = async (promises) => {

    // use .allSettled() instead of .all() because some devices are expected to fail/reject
    // because the search space is anything on the LAN, including non-tplink devices
    const _promises = await Promise.allSettled(promises)

    // filter on promises that resolved
    return _promises.reduce((accumulator, currentValue) => {
        if (currentValue.status === 'fulfilled') {
            accumulator.push(currentValue.value);
        }
        return accumulator;
    }, [])
}


const startup = async () => {
    try {
        // instantiate an aggressively short timeout to short-circuit
        // all the calls to neighbors that are not tplink devices
        // ignore all error logging
        // if you [a device] throw an error that's your problem I don't care about it
        const client = new Client({
            logLevel: 'silent', defaultSendOptions: {
                timeout: parseInt(process.env.STARTUP_TIMEOUT)
            }
        })

        // check every ip address on the LAN
        // if it is a tplink device, create a client for it
        // persist a snapshot of the devices for reference
        const knownGood = {}

        // this was cool but caused timing issues when run on the janky old server -
        // I suspect a cheap NIC dropped packets from concurrent getDevice() calls
        //
        // go sequential instead
        //
        // const devices = await getFulfilledPromises(discoverDevicesPromises(client, showNeighbors()))
        // // for (const device of devices) {
        // await Promise.all(devices.map(async device => {
        //     let alias = device.sysInfo.alias
        //
        //     let host = device.host
        //     let aliasMetadata = parseAlias(alias)
        //
        //     knownGood[alias] = {
        //         host, aliasMetadata, ...device.sysInfo,
        //     }
        // }))
        const devices = []
        for (const neighbor of showNeighbors()) {
            const result = await client.getDevice({host: neighbor.ip})
                .catch((err) => {
                    console.log('skipping:', neighbor.ip)
                })

            if (result) {
                devices.push(result)
            }
        }

        // make it look cool
        for (const device of devices) {
            await device.setPowerState(true)
            setTimeout(() => {
            }, 10)
        }
        for (const device of devices.toReversed()) {
            await device.setPowerState(false)
            setTimeout(() => {
            }, 10)
        }

        console.log(devices.map(i => {
            return {
                alias: i.alias, host: i.host
            }
        }))

        // ok we made it look cool we're done
        return {
            deviceInfo: knownGood, devices
        }
    } catch (err) {
    }
}

module.exports = {
    startup
};

(async () => {
    await startup();
})();
