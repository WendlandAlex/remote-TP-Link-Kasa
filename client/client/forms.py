from flask_wtf import FlaskForm
from wtforms import RadioField, SelectMultipleField, StringField, SubmitField, widgets
from wtforms.validators import DataRequired, Regexp

states = ['on','off']

class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class DeviceForm(FlaskForm):
    room = MultiCheckboxField(
        'Room',
        # validators = [DataRequired()],
        choices=[('all','All')]
    )

    # wait why is the constructor after another method? see citation
    def __init__(self, devices, *args, **kwargs):
        """citation: https://stackoverflow.com/a/59586666"""
        super().__init__(*args, **kwargs)
        self.devices = devices
        self.room.choices.extend([
            ( i.get('alias'), i.get('alias') )
            for i in self.devices
        ])

    command = RadioField(
        'Command',
        validators = [DataRequired()],
        choices = [ ( i, i.title() ) for i in states ]
    )
    totp = StringField(
        'TOTP',
        validators = [
            DataRequired(),
            Regexp(r"""\d{6}""")
        ] 
    )
    submit = SubmitField('Submit')
