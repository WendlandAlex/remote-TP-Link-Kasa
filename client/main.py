from flask import Flask, abort, request, Response
import asyncio
import os
import websockets
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
WS_HOST = os.getenv('WS_HOST', 'localhost')
WS_PORT = os.getenv('WS_PORT', 8765)
if ':' in WS_HOST:
    uri = f'ws://[{WS_HOST}]:{WS_PORT}/'
else:
    uri = f'ws://{WS_HOST}:{WS_PORT}/'


with app.app_context():
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
    
    
    @app.route('/devices/<path:path>', methods=['GET'])
    async def devices_list_all(path):
        async with websockets.connect(uri=uri) as conn:
            try:
                await conn.send(request.path)
                res = await conn.recv()

                return Response(res, status=200, mimetype='application/json')
                    
            except websockets.ConnectionClosed as e:
                print(e)
            finally:
                await conn.close()


    @app.route('/power/<path:path>', methods=['GET'])
    async def power_toggle_all(path):
        async with websockets.connect(uri=uri) as conn:
            try:
                await conn.send(request.path)
                res = await conn.recv()

                return Response(res, status=200, mimetype='application/json')
                    
            except websockets.ConnectionClosed as e:
                print(e)
            finally:
                await conn.close()


if __name__ == '__main__':
    app.run(port=8080)