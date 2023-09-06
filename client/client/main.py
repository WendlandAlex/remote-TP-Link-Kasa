import asyncio
import os

import pyotp
import websockets
from dotenv import load_dotenv
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_cors import CORS

app = Flask(
    __name__,
    instance_relative_config=False,
    template_folder='templates',
    static_folder='static'
    )
    
app.config.from_object('config.Config')
Bootstrap(app)
CORS(app)

with app.app_context():
    load_dotenv()
    HTTP_HOST = os.getenv('HTTP_HOST', 'localhost')
    HTTP_PORT = os.getenv('HTTP_PORT', 8765)
    if ':' in HTTP_HOST:
        uri = f'http://[{HTTP_HOST}]:{HTTP_PORT}'
    else:
        uri = f'http://{HTTP_HOST}:{HTTP_PORT}'

    PYOTP = pyotp.TOTP(app.config.get('PYOTP_SECRET'))

    import routes



if __name__ == '__main__':
    app.run(port=8080)
