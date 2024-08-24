from datetime import date
from functools import wraps
from flask import session, flash, redirect, url_for
from wtforms import Form, PasswordField, StringField, validators, IntegerField, SelectField, DecimalField, DateField, FloatField
from passlib.hash import sha256_crypt
from wtforms.validators import InputRequired, NumberRange


class ChangePasswordForm(Form):
    old_password = PasswordField('Existing Password')
    new_password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')])
    confirm = PasswordField('Confirm Password')


class AddMemberForm(Form):
    username = StringField('Username', [
        validators.InputRequired(),
        validators.NoneOf(values=[], message="Username already taken, Please try another")
    ])
    name = StringField('Name', [validators.Length(min=1, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')
    email = StringField('Email', [validators.Length(min=1, max=100)])

    def __init__(self, values, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username.validators[1].values = values

class EditForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.Length(min=1, max=100)])
    role = StringField('Role', [validators.Length(min=1, max=10)])
    player_number = IntegerField('Player Number', [NumberRange(min=0, max=12, message='Number must be between 0 and 12')])
    status = StringField('Status', [validators.Length(min=1, max=10)])

class GameActionForm(Form):
    player_number = IntegerField('PN', [NumberRange(min=0, max=12, message='Number must be between 0 and 12')])
    player_round = IntegerField('PR', [NumberRange(min=0, max=999, message='Number must be between 0 and 999')])
    player_move = IntegerField('PR', [NumberRange(min=0, max=999, message='Number must be between 0 and 999')])
    player_message1 = StringField('Name', [validators.Length(min=1, max=100)])
    player_message2 = StringField('Name', [validators.Length(min=1, max=100)])
    player_message3 = StringField('Name', [validators.Length(min=1, max=300)])


class GameForm(Form):
    action = StringField('Action', [validators.InputRequired()])
    salary = IntegerField('Salary', [NumberRange(min=1000, max=3000, message='Salary must be between 1000 and 3000')])
    game_ID = StringField('Game ID', [validators.Length(min=1, max=20)])
    choices = [('New', 'New Player'), ('Ready', 'Ready'), ('Paused', 'Paused')]
    status = SelectField('Status', choices=choices)


class GameLevelForm(Form):
    level = IntegerField('Level', [validators.InputRequired(), NumberRange(min=1, max=100)])
    choices = [('GP', 'Guru Play'),
               ('CP', 'Challenger Play'),
               ('EP', 'Easy Play')]
    glevel = SelectField('Game Level', choices=choices)

    selected_glevel = None
    choices = [('CA', 'Career Achievement'),
               ('MA', 'Money Achievement'),
               ('IA', 'Investment Achievement'),
               ('AA', 'Acquisitions Achievement')]
    ggoal = SelectField('Game Goal', choices=choices)

    selected_ggoal = None
    player_count = IntegerField('Player Count',
                                [NumberRange(min=1, max=12, message='Number of Players must be between 1 and 12')])
    choices = [('New', 'New Game'), ('Ready', 'Ready'), ('Paused', 'Paused')]
    status = SelectField('Status', choices=choices)
    game_ID = StringField('Game ID', [validators.Length(min=1, max=20)])
    start_date = DateField('Game Start Date', default=date.today)

    population = DecimalField('Town Population',
                              [NumberRange(min=100000, max=2000000, message='Population must be between 100K and 2M')])
    population_chg = FloatField('Population Growth Rate',
                           [NumberRange(min=0.05, max=0.15, message='Population rate must be between 0.05 and 0.15')])

class GameSetupForm(Form):
    level = IntegerField('Level', [validators.InputRequired(), NumberRange(min=1, max=100)])
    choices = [('GP', 'Guru Play'),
               ('CP', 'Challenger Play'),
               ('EP', 'Easy Play')]
    glevel = SelectField('Game Level', choices=choices)

    selected_glevel = None
    choices = [('CA', 'Career Achievement'),
               ('MA', 'Money Achievement'),
               ('IA', 'Investment Achievement'),
               ('AA', 'Acquisitions Achievement')]
    ggoal = SelectField('Game Goal', choices=choices)

    selected_ggoal = None
    player_count = IntegerField('Player Count',
                                [NumberRange(min=1, max=12, message='Number of Players must be between 1 and 12')])
    status = SelectField('Status', choices=choices)
    game_ID = StringField('Game ID', [validators.Length(min=1, max=20)])
    start_date = DateField('Game Start Date', default=date.today)

class GameConnectForm(Form):
    salary = IntegerField('Salary', [NumberRange(min=1000, max=3000, message='Salary must be between 1000 and 3000')])
    game_ID = StringField('Game ID', [validators.Length(min=1, max=20)])
    choices = [('New', 'New Player'), ('Ready', 'Ready'), ('Paused', 'Paused')]
    status = SelectField('Status', choices=choices)
