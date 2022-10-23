import websockets
from main import uri


async def send_command(path):
    async with websockets.connect(uri=uri) as conn:
        try:
            await conn.send(path)
            res = await conn.recv()

            return res

        except websockets.ConnectionClosed as e:
            print(e)
        finally:
            await conn.close()
