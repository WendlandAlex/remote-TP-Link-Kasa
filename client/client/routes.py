import websockets
from flask import Flask, Response, abort
from flask import current_app as app
from flask import redirect, render_template, request, url_for

from forms import DeviceForm
from main import PYOTP, uri
from services import commands

with app.app_context():
    @app.route('/', methods=['GET','POST'])
    async def authenticate():


        form = DeviceForm()

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
            totp_is_valid = PYOTP.verify(totp)
            print(
                PYOTP.now(), totp, totp_is_valid
            )

            if not totp_is_valid:
                abort(404)

            res = await commands.send_command(path=f'/power/{form.command.data}/{form.alias.data}')

            return Response(res, status=200, mimetype='application/json')



    @app.route('/devices/<path:path>', methods=['GET'])
    async def devices_list_all(path):
            res = await commands.send_command(path=f'/devices/list/all')

            return Response(res, status=200, mimetype='application/json')
