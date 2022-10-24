from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, SubmitField
from wtforms.validators import DataRequired, Regexp

states = ['on','off']

class DeviceForm(FlaskForm):
    room = RadioField(
        'Room',
        validators = [DataRequired()],
        choices=[('all','All')]
    )

    # wait why is the constructor after another method? see citation
    def __init__(self, devices, *args, **kwargs):
        """citation: https://stackoverflow.com/a/59586666"""
        super().__init__(*args, **kwargs)
        self.devices = devices
        self.room.choices.extend([
            ( i.get('room'), i.get('room').title() )
            for i in self.devices
        ])

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
