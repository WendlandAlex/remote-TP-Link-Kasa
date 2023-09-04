require('dotenv').config();
const path = require("path");
const express = require("express");
const morgan = require('morgan');
const {startup} = require('./startup')
const {parseAlias, getDevicePowerStates} = require('./utils')

const wg_host = process.env.WG_HOST || 'localhost'
const wg_port = process.env.WG_PORT || '8989'

const app = express();
app.use(express.json());
app.use(express.urlencoded({extended: false}))
app.use(morgan('combined'))

const startServer = async () => {
    const {deviceInfo, devices} = await startup()

    app.get('/healthcheck', async (req, res) => {
        res.json({health: 'y'})
    })

    app.get('/', async (req, res) => {
        res.send(await getDevicePowerStates(devices))
    })

    app.post('/submit', async (req, res) => {
        let hosts
        let zones

        const data = req.body || {
            hosts: 'all', power: 'off'
        }

        if (data.hosts) {
            hosts = data.hosts[0] === 'all' ? devices : devices.filter(i => data.hosts.includes(i.host))
        }
        if (data.zones) {
            zones = data.zones === 'all' ? devices : devices.filter(i => data.zones.includes(i.aliasMetadata.zone))
        }
        const powerState = (data.power.toLowerCase() === 'on')

        await Promise.all(hosts.map(async i => {
            await i.setPowerState(powerState)
            return i
        }))

        res.json(await getDevicePowerStates(devices))
    })

    app.listen(wg_port, wg_host, () => {
        console.log(`app listening on ${wg_host}:${wg_port}`)
    })
}

startServer()
