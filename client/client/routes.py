import websockets
from flask import Flask, Response, abort
from flask import current_app as app
from flask import redirect, render_template, request, url_for

from forms import DeviceForm
from main import PYOTP
from services import commands, mfa
import json

with app.app_context():
    @app.route('/', methods=['GET','POST'])
    async def authenticate():

        devices = json.loads(
            await commands.send_command('/devices/list/all')
        )
        form = DeviceForm(devices)

        if request.method == 'GET':
            return render_template(
                'authenticate.jinja2',
                form=form,
                title='vpnKasa',
                template='form-template'
            )
        
        elif request.method == 'POST':
            if not form.validate_on_submit():
                abort(404)

            totp = int(form.totp.data)
            totp_is_valid = mfa.validate_totp(PYOTP, totp)

            if totp_is_valid is False:
                abort(404)

            _cmd = '/' + '/'.join([
                'power',
                form.command.data,
                form.room.data,
            ])

            res = await commands.send_command(_cmd)

            return Response(res, status=200, mimetype='application/json')


    @app.route('/power/<path:path>', methods=['POST'])
    async def power_toggle(path):
        body = request.get_json()
        print(body)
        totp = body.get('totp')
        if mfa.validate_totp(PYOTP, totp) is False:
            abort(404)

        _cmd = '/' + '/'.join([
            body.get('noun'),
            body.get('verb'),
            body.get('target')
        ])

        res = await commands.send_command(_cmd)

        return Response(res, status=200, mimetype='application/json')


    @app.route('/devices/<path:path>', methods=['GET'])
    async def devices_list_all(path):
            res = await commands.send_command(path=f'/devices/list/all')

            return Response(res, status=200, mimetype='application/json')
