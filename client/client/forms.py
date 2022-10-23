from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField
from wtforms.validators import DataRequired, Regexp

devices = ['all','entrance','kitchen','office','bathroom']
states = ['on','off']

class DeviceForm(FlaskForm):
    alias = RadioField(
        'Alias',
        validators = [DataRequired()],
        choices = [ ( i, i.title() ) for i in devices ]
    )
    command = RadioField(
        'Command',
        validators = [DataRequired()],
        choices = [ ( i, i.title() ) for i in states ]
    )
    totp = StringField(
        'MFA Code',
        validators = [
            DataRequired(),
            Regexp(r"""\d{6}""")
        ] 
    )
    submit = SubmitField('Submit')
