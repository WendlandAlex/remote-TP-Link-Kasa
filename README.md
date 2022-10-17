# Implementation
`Client` runs on fly.io as a reverse proxy and sends commands to the server running on the same LAN as the TP-Link Kasa devices to control. The server requires a wireguard tunnel to be setup and peered with the user's fly.io `6pn` private mesh network -- this can be done by running `flyctl wireguard create` to generate a wg0.conf file, then by running `wg-quick up ./wg0.conf` to provision a wireguard interface on the server. The address of the interface must be seeded in the client `.env` file as `WS_HOST`. As a one-time step, run `flyctl wireguard websockets enable`

# Server
## requirements
a `.env` file with `WS_HOST` and `WS_PORT` to listen for websocket connections

# Client
## requirements
a `.env` file with 