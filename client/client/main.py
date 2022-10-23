from flask import Flask
from flask_bootstrap import Bootstrap
import asyncio
import os
import websockets
from dotenv import load_dotenv
import pyotp

app = Flask(
    __name__,
    instance_relative_config=False,
    template_folder='templates',
    static_folder='static'
    )
    
app.config.from_object('config.Config')
Bootstrap(app)

with app.app_context():
    load_dotenv()
    WS_HOST = os.getenv('WS_HOST', 'localhost')
    WS_PORT = os.getenv('WS_PORT', 8765)
    if ':' in WS_HOST:
        uri = f'ws://[{WS_HOST}]:{WS_PORT}/'
    else:
        uri = f'ws://{WS_HOST}:{WS_PORT}/'

    # exit if there is no server to connect to
    async def healthcheck():
        async with websockets.connect(uri=uri) as conn:
            await conn.ping()
                
            sockinfo = conn.remote_address
            if ':' in WS_HOST:
                print(f'connected to socket: ws://[{sockinfo[0]}]:{sockinfo[1]}')
            else:
                print(f'connected to socket: ws://{sockinfo[0]}:{sockinfo[1]}')

        asyncio.run(healthcheck())

    PYOTP = pyotp.TOTP(app.config.get('PYOTP_SECRET'))

    import routes


if __name__ == '__main__':
    app.run(port=8080)