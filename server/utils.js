const parseAlias = (alias) => {
    let [type, room, macLast4, attachedDevices] = alias.split('.')
    return {
        type, room, macLast4, attachedDevices: attachedDevices.split(',')
    }
}

const getDevicePowerStates = async (devices=[]) => {
    return Promise.all(devices.map(async i => {
        return {
            alias: i.alias,
            ...parseAlias(i.alias),
            powerState: await i.getPowerState()
        }
    }))
}

module.exports = {
    parseAlias,
    getDevicePowerStates
}
