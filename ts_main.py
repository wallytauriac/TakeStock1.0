from ts_validation import *
from ts_database import *
from flask import Blueprint, Flask, render_template, flash, redirect, url_for, request, session, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField
from wtforms.fields import DateField, DecimalField
from wtforms.validators import InputRequired, DataRequired, NumberRange
from passlib.hash import sha256_crypt
from functools import wraps
from datetime import datetime, date
from app_factory import create_app, mysql
from ts_page import ts_page_bp, render_edit_profile, render_game_settings
from ts_sub1 import ts_sub1_bp

app = create_app()

# Register Blueprints
app.register_blueprint(ts_page_bp)
app.register_blueprint(ts_sub1_bp)

db = DB_Mgr(mysql)


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Nice try, Tricks don\'t work, bud!! Please Login :)', 'danger')
            return redirect(url_for('login'))
    return wrap

def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session['role'] == "Host":
            return f(*args, **kwargs)
        else:
            flash('You are probably not an admin!!, Are you?', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/', methods=['GET', 'POST'])
def index():
    page_name = "Home"
    return render_template('home.html', page_name=page_name)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    page_name = "Login"
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        result, q = db.get_player_record(username)
        if q>0:
            status = db.validate_password(result, password_candidate, username)
            if status == "OK":
                flash('You are logged in', 'success')

                return redirect(url_for('profile', username=username, result=result, page_name=page_name))
            else:
                error = 'Invalid login. Please register.'
                return render_template('login.html', error=error, page_name=page_name)
        else:
            error = 'Please Login. Account not Found'
            return render_template('login.html', error=error, page_name=page_name)

    error = 'Please register if you are not a member.'
    return render_template('login.html', error=error, page_name=page_name)
@app.route('/update_password/<string:username>', methods = ['GET', 'POST'])
def update_password(username):
    page_name = "Update Password"
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        status = db.update_password(username, form)
        if status == "OK":
            flash('New password will be in effect from next login!!', 'info')
            return redirect(url_for('memberDash', username = session['username'], page_name=page_name))
        else:
            flash('Old password you entered is wrong!!, try again', 'warning')
    return render_template('updatePassword.html', form=form, page_name=page_name)

@app.route('/adminDash/<username>')
@is_logged_in
@is_admin
def adminDash():
    page_name = "Host Admin"
    return render_template('adminDash.html', page_name=page_name, username=username)
@app.route('/addMember', methods=['GET', 'POST'])
def addMember():
    choices = []
    page_name = "Register"
    choices.clear()
    status, values = db.get_players()
    if status == "OK":
        form = AddMemberForm(values, request.form)

    roles = ['Select your role', 'Host', 'Player']

    if request.method == 'POST' and form.validate():
        username = form.username.data
        status = db.add_player(form)
        if status == "OK":
            choices.clear()
            flash('You are added as a new game player!!', 'success')
        else:
            return render_template('addMember.html', form=form, page_name=page_name, roles=roles)
        return redirect(url_for('profile', username = username, page_name=page_name, roles=roles))
    return render_template('addMember.html', form=form, page_name=page_name, roles=roles)

class DelMemberForm(Form):
    username = StringField('Username', validators=[validators.DataRequired()])
@app.route('/deleteMember', methods = ['GET', 'POST'])
@is_logged_in
def deleteMember():
    choices = []
    choices.clear()
    cur = mysql.connection.cursor()
    q = cur.execute("SELECT username FROM players")
    b = cur.fetchall()
    for i in range(q):
        tup = (b[i]['username'],b[i]['username'])
        choices.append(tup)
    form = DelMemberForm(Form)
    if request.method == 'POST':
        username = form.username.data
        cur = mysql.connection.cursor()

        cur.execute("DELETE FROM players WHERE username = %s", [username])
        mysql.connection.commit()
        cur.close()
        choices.clear()
        flash('You deleted a player from the Game!!', 'success')
        return redirect(url_for('adminDash'))
    return render_template('deleteRecep.html', form = form)

@app.route('/user_connect')
def user_connect():
    # Retrieve the username from the session
    username = session.get('username')
    if not username:
        # Handle the case where the username is not in the session
        return redirect(url_for('login'))
    # return redirect(url_for('gameConnect', username=username))
    return gameConnect(username)


@app.route('/gameConnect/<username>', methods=['GET', 'POST'])
@is_logged_in
def gameConnect(username):
    page_name = "Game Connect"
    username = session.get('username')
    result, data = db.get_player_record(username)

    form = GameConnectForm(request.form)
    # Pre-fill the form with current user data
    if request.method == 'GET':
        form.game_ID.data = result['game_ID']
        form.status.data = result['status']
        form.salary.data = result['salary']

        return render_template('gameConnect.html', result=result, page_name=page_name,
                               username=username, form=form)

    # if result['player_number'] == " " or result['player_number'] is None:
    #     result['player_number'] = 0
    if request.method == 'POST' and form.validate():
        stat, q = db.update_player(form)
        if stat == "OK":
            app.logger.info(q)
            flash('You successfully updated your profile!!', 'success')
        return redirect(url_for('gameConnect', username=username))

    return render_template('gameConnect.html', result=result, page_name=page_name,
                           username=username, form=form)

@app.route('/game_dash', methods=['GET', 'POST'])
@is_logged_in
def game_dash():
    # Retrieve the username from the session
    username = session.get('username')
    if not username:
        # Handle the case where the username is not in the session
        return redirect(url_for('login'))
    return gameDash(username)

@app.route('/gameDash/<username>', methods=['GET', 'POST'])
@is_logged_in
def gameDash(username):
    page_name = "Game PlayBook"
    if username != session.get('username'):
        flash('You aren\'t authorised to view this page', 'error')
        return redirect(url_for('login', username=session['username'], page_name="Login"))
    if session.get('role') != "Host":
        flash('You aren\'t authorised to access this page', 'error')
        return redirect(url_for('login', username=session['username'], page_name="Login"))

    form = GameLevelForm(request.form)
    # Initiate game settings
    if form.game_ID.data == " " or form.game_ID.data is None:
        status, result = db.get_game_data(username)
        form = render_game_settings(form, result)

    if request.method == 'POST' and form.validate():
        selected_glevel = request.form.get('game_level')
        selected_ggoal = request.form.get('game_goal')

        if status == "OK":
            if result>0:
                q, status = db.update_game(form)
                app.logger.info(q)
            else:
                # Insert game row
                status, q = db.add_game(form)
                if status == "OK":
                    app.logger.info(q)
                    flash("You selected: {selected_glevel}", "success")
                    return redirect(url_for('gameDash', username=username, form=form, page_name=page_name))
                else:
                    return render_template('gameDash.html', form=form, page_name=page_name, username=username)

    # Display the game settings
    return render_template('gameDash.html', username=username, form=form, page_name=page_name)

@app.route('/game_setup', methods=['GET', 'POST'])
@is_logged_in
def game_setup():
    # Retrieve the username from the session
    username = session.get('username')
    if not username:
        # Handle the case where the username is not in the session
        return redirect(url_for('login'))
    return gameSetup(username)

@app.route('/gameSetup', methods=['GET', 'POST'])
@is_logged_in
def gameSetup(username):
    page_name = "Game Setup"

    if username!=session.get('username'):
        flash('You aren\'t authorised to view this page', 'error')
        return redirect(url_for('login', username=session['username'], page_name="Login"))
    if session.get('role') != "Host":
        flash('You aren\'t authorised to access this page', 'error')
        return redirect(url_for('login', username=session['username'], page_name="Login"))

    form = GameSetupForm(request.form)
    # Get Game Settings
    status, result = db.get_game_data(username)

    # Display game settings
    if status == "OK":
        # Populate game variables from result
        form.game_ID.data = result["game_ID"]
        form.player_count.data = result["player_count"]
        form.glevel.data = result["game_level"]
        form.ggoal.data = result["game_goal"]

    status, users = db.get_game_players(result["game_ID"])
    if status == "OK":
        # print("Game Players:", users)
        # Example of updating player numbers
        for i, user in enumerate(users):
            username = user['username']
            gstatus = "Ready"
            update_status = db.update_player_game_card(username, i + 1, gstatus)
            player_count = i + 1
            if update_status == "OK":
                pass
            else:
                # print(f"Failed to update player number for {username}")
                flash("Failed to update {username}", "error")
                return redirect(url_for('gameSetup', username=username, form=form, page_name=page_name))
        # Get detailed player information
        form.player_count.data = player_count
        session['player_count'] = player_count
        status, players = db.get_players_game_card(result["game_ID"])

        if status == "OK":
            # print("Player Details:", players)
            pass
        else:
            flash("Failed to retrieve player details", "error")
            return redirect(url_for('gameSetup', username=username, form=form, page_name=page_name))
    else:
        flash("Failed retrieving game players", "error")
        return redirect(url_for('gameSetup', username=username, form=form, page_name=page_name))
    if request.method == 'POST' and form.validate():
        selected_glevel = request.form.get('game_level')
        selected_ggoal = request.form.get('game_goal')


        # Update game row
        form.player_count.data = player_count
        session['player_count'] = player_count
        q, status = db.update_game(form)
        app.logger.info(q)

        if status == "OK":
            app.logger.info(q)
            flash("Game status update was successful", "success")
            return redirect(url_for('gameSetup', username=username, form=form, players=players, page_name=page_name))
        else:
            return render_template('gameSetup.html', form=form, page_name=page_name, username=username)

    # Display the game settings
    return render_template('gameSetup.html', username=username, form=form, players=players, page_name=page_name)


@app.route('/profile/<string:username>')
@is_logged_in
def profile(username):
    page_name = "Profile"
    if username == session['username']:
        result, q = db.get_player_record(username)
        return render_template('profile.html', result=result, page_name=page_name)
    else:
        flash("Please register and/or login.", "error")
    return redirect(url_for('gameDash', username=username, page_name=page_name))

@app.route('/edit_profile/<string:username>', methods = ['GET', 'POST'])
@is_logged_in
def edit_profile(username):
    page_name = "Edit Profile"
    username = session["username"]

    result, q = db.get_player_record(username)

    form = EditForm(request.form)
    if request.method == 'GET':
        form = render_edit_profile(form, result)
    if request.method == 'POST' and form.validate():
        stat, q = db.update_profile(form, username)

        app.logger.info(request.form['name'])
        app.logger.info(request.form['email'])
        app.logger.info(q)
        flash('You successfully updated your profile!!', 'success')

    return render_template('edit_profile.html', form=form, page_name=page_name)

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.secret_key = '528491@JOKER'
    app.debug = True
    app.run()