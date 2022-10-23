from flask import current_app as app
from flask import Flask, request, abort, Response, url_for, render_template, redirect
import websockets

from forms import DeviceForm
from main import uri, PYOTP

with app.app_context():
    @app.route('/', methods=['GET','POST'])
    def authenticate():
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

            return redirect(url_for('power_toggle', path=f'{form.command.data}/{form.alias.data}'))


        
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
    async def power_toggle(path):
        async with websockets.connect(uri=uri) as conn:
            try:
                await conn.send(request.path)
                res = await conn.recv()

                return Response(res, status=200, mimetype='application/json')
                    
            except websockets.ConnectionClosed as e:
                print(e)
            finally:
                await conn.close()