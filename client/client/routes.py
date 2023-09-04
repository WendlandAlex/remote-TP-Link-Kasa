# import websockets
from flask import Flask, Response, abort
from flask import current_app as app
from flask import redirect, render_template, request, url_for, jsonify
import requests
import os

from flask_wtf import csrf

from forms import DeviceForm
from main import PYOTP, uri
from services import mfa
import json

with app.app_context():
    @app.route('/json', methods=['GET'])
    async def json():
        devices = requests.get(f'{uri}/').json()
        return jsonify(devices)

    @app.route('/', methods=['GET','POST'])
    async def authenticate():
        devices = requests.get(f'{uri}/').json()
        form = DeviceForm(devices)

        if request.method == 'GET':
            return render_template(
                'authenticate.jinja2',
                form=form,
                title=os.getenv('TITLE'),
                template='form-template'
            )
        
        elif request.method == 'POST':
            if not form.validate_on_submit():
                abort(404)

            totp = int(form.totp.data)
            totp_is_valid = mfa.validate_totp(PYOTP, totp)

            if totp_is_valid is False:
                abort(404)

            print(form.hosts.data)
            print(form.command.data)

            res = requests.post(f'{uri}/submit', json={
                'hosts': form.hosts.data,
                'power': form.command.data
            })
            # return redirect(
            #     url_for('authenticate')
            # )
            # return jsonify(res)
            return Response(res, status=200, mimetype='application/json')