from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField
from wtforms.fields import DateField
from wtforms.validators import InputRequired
from passlib.hash import sha256_crypt
#from flask_script import Manager
from functools import wraps
from datetime import datetime

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Evenodd!512'
app.config['MYSQL_DB'] = 'takestock1.0'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Nice try, Tricks don\'t work, bud!! Please Login :)', 'danger')
			return redirect(url_for('login'))
	return wrap

def is_trainor(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if session['prof'] == 3:
			return f(*args, **kwargs)
		else:
			flash('You are probably not a trainor!!, Are you?', 'danger')
			return redirect(url_for('login'))
	return wrap

def is_admin(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if session['prof'] == 1:
			return f(*args, **kwargs)
		else:
			flash('You are probably not an admin!!, Are you?', 'danger')
			return redirect(url_for('login'))
	return wrap

def is_recep_level(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if session['prof'] <= 2:
			return f(*args, **kwargs)
		else:
			flash('You are probably not an authorised to view that page!!', 'danger')
			return redirect(url_for('login'))
	return wrap


@app.route('/', methods = ['GET', 'POST'])
def index():
	page_name = "Home"
	return render_template('home.html', page_name=page_name)

@app.route('/login', methods = ['GET', 'POST'])
def login():
	page_name = "Login"
	if request.method == 'POST':
		username = request.form['username']
		password_candidate = request.form['password']

		cur = mysql.connection.cursor()

		result = cur.execute('SELECT * FROM info WHERE username = %s', [username])
		#print(result)
		if result>0:
			data = cur.fetchone()
			password = data['password']

			if sha256_crypt.verify(password_candidate, password):
				session['logged_in'] = True
				session['username'] = username
				session['prof'] = data['prof']
				#session['hash'] = sha256_crypt.encrypt(username)
				flash('You are logged in', 'success')
				if session['prof'] == 1:
					return redirect(url_for('adminDash'))
				if session['prof'] == 3:
					return redirect(url_for('trainorDash'))
				if session['prof'] == 2:
					return redirect(url_for('recepDash'))
				#s = 'memberDash/%s', (username)
				return redirect(url_for('memberDash', username = username, page_name=page_name))
			else:
				error = 'Invalid login. Please register.'
				return render_template('login.html', error = error, page_name=page_name)

			cur.close();
		else:
			error = 'Please Login. Account not Found'
			return render_template('login.html', error = error, page_name=page_name)

	error = 'Please register if you are not a member.'
	return render_template('login.html', error = error, page_name=page_name)


class ChangePasswordForm(Form):
	old_password = PasswordField('Existing Password')
	new_password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message = 'Passwords aren\'t matching pal!, check \'em')
	])
	confirm = PasswordField('Confirm Password')


@app.route('/update_password/<string:username>', methods = ['GET', 'POST'])
def update_password(username):
	page_name = "Update Password"
	form = ChangePasswordForm(request.form)
	if request.method == 'POST' and form.validate():
		new = form.new_password.data
		entered = form.old_password.data
		cur = mysql.connection.cursor()
		cur.execute("SELECT password FROM info WHERE username = %s", [username])
		old = (cur.fetchone())['password']
		if sha256_crypt.verify(entered, old):
			cur.execute("UPDATE info SET password = %s WHERE username = %s", (sha256_crypt.encrypt(new), username))
			mysql.connection.commit()
			cur.close()
			flash('New password will be in effect from next login!!', 'info')
			return redirect(url_for('memberDash', username = session['username'], page_name=page_name))
		cur.close()
		flash('Old password you entered is wrong!!, try again', 'warning')
	return render_template('updatePassword.html', form = form, page_name=page_name)

@app.route('/adminDash')
@is_logged_in
@is_admin
def adminDash():
	return render_template('adminDash.html')

values = []
choices = []

class AddTrainorForm(Form):
	name = StringField('Name', [validators.Length(min = 1, max = 100)])
	username = StringField('Username', [validators.InputRequired(), validators.NoneOf(values = values, message = "Username already taken, Please try another")])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message = 'Passwords aren\'t matching pal!, check \'em')
	])
	confirm = PasswordField('Confirm Password')
	street = StringField('Street', [validators.Length(min = 1, max = 100)])
	city = StringField('City', [validators.Length(min = 1, max = 100)])
	prof = 3
	phone = StringField('Phone', [validators.Length(min = 1, max = 100)])


@app.route('/addTrainor', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def addTrainor():
	values.clear()
	cur = mysql.connection.cursor()
	q = cur.execute("SELECT username FROM info")
	b = cur.fetchall()
	for i in range(q):
		values.append(b[i]['username'])
	#app.logger.info(b[0]['username'])
	#res = values.fetchall()
	#app.logger.info(res)
	cur.close()
	form = AddTrainorForm(request.form)
	if request.method == 'POST' and form.validate():
		#app.logger.info("setzdgxfhcgjvkhbjlkn")
		name = form.name.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))
		street = form.street.data
		city = form.city.data
		prof = 2
		phone = form.phone.data

		cur = mysql.connection.cursor()

		cur.execute("INSERT INTO info(name, username, password, street, city, prof, phone) VALUES(%s, %s, %s, %s, %s, %s, %s)", (name, username, password, street, city, 3,phone))
		cur.execute("INSERT INTO trainors(username) VALUES(%s)", [username])
		mysql.connection.commit()
		cur.close()
		flash('You recruited a new Trainor!!', 'success')
		return redirect(url_for('adminDash'))
	return render_template('addTrainor.html', form=form)



class DeleteRecepForm(Form):
	username = SelectField(u'Choose which one you wanted to delete', choices=choices)



@app.route('/deleteTrainor', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def deleteTrainor():
	choices.clear()
	cur = mysql.connection.cursor()
	q = cur.execute("SELECT username FROM trainors")
	b = cur.fetchall()
	for i in range(q):
		tup = (b[i]['username'],b[i]['username'])
		choices.append(tup)
	form = DeleteRecepForm(request.form)
	if len(choices)==1:
		flash('You cannot remove your only Trainor!!', 'danger')
		return redirect(url_for('adminDash'))
	if request.method == 'POST':
		#app.logger.info(form.username.data)
		username = form.username.data
		q = cur.execute("SELECT username FROM trainors WHERE username != %s", [username])
		b = cur.fetchall()
		new = b[0]['username']
		cur.execute("UPDATE members SET trainor = %s WHERE trainor = %s", (new, username))
		cur.execute("DELETE FROM trainors WHERE username = %s", [username])
		cur.execute("DELETE FROM info WHERE username = %s", [username])
		mysql.connection.commit()
		cur.close()
		choices.clear()
		flash('You removed your Trainor!!', 'success')
		return redirect(url_for('adminDash'))
	return render_template('deleteRecep.html', form = form)


@app.route('/addRecep', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def addRecep():
	values.clear()
	cur = mysql.connection.cursor()
	q = cur.execute("SELECT username FROM info")
	b = cur.fetchall()
	for i in range(q):
		values.append(b[i]['username'])
	#app.logger.info(b[0]['username'])
	#res = values.fetchall()
	#app.logger.info(res)
	cur.close()
	form = AddTrainorForm(request.form)
	if request.method == 'POST' and form.validate():
		#app.logger.info("setzdgxfhcgjvkhbjlkn")
		name = form.name.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))
		street = form.street.data
		city = form.city.data
		phone = form.phone.data

		cur = mysql.connection.cursor()

		cur.execute("INSERT INTO info(name, username, password, street, city, prof, phone) VALUES(%s, %s, %s, %s, %s, %s, %s)", (name, username, password, street, city, 2,phone))
		cur.execute("INSERT INTO receps(username) VALUES(%s)", [username])
		mysql.connection.commit()
		cur.close()
		flash('You recruited a new Receptionist!!', 'success')
		return redirect(url_for('adminDash'))
	return render_template('addRecep.html', form=form)

class DeleteRecepForm(Form):
	username = SelectField(u'Choose which one you wanted to delete', choices=choices)



@app.route('/deleteRecep', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def deleteRecep():
	choices.clear()
	cur = mysql.connection.cursor()
	q = cur.execute("SELECT username FROM receps")
	b = cur.fetchall()
	for i in range(q):
		tup = (b[i]['username'],b[i]['username'])
		choices.append(tup)
	if len(choices)==1:
		flash('You cannot remove your only receptionist!!', 'danger')
		return redirect(url_for('adminDash'))
	form = DeleteRecepForm(request.form)
	if request.method == 'POST':
		#app.logger.info(form.username.data)
		username = form.username.data
		cur.execute("DELETE FROM receps WHERE username = %s", [username])
		cur.execute("DELETE FROM info WHERE username = %s", [username])
		mysql.connection.commit()
		cur.close()
		choices.clear()
		flash('You removed your receptionist!!', 'success')
		return redirect(url_for('adminDash'))
	return render_template('deleteRecep.html', form = form)


class AddEquipForm(Form):
	name = StringField('Name', [validators.Length(min = 1, max = 100)])
	count = IntegerField('Count', [validators.NumberRange(min = 1, max = 25)])


@app.route('/addEquip', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def addEquip():
	form = AddEquipForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		count = form.count.data
		cur = mysql.connection.cursor()
		q = cur.execute("SELECT name FROM equip")
		equips = []
		b = cur.fetchall()
		for i in range(q):
			equips.append(b[i]['name'])
		if name in equips:
			cur.execute("UPDATE equip SET count = count+%s WHERE name = %s", (count, name))
		else:
			cur.execute("INSERT INTO equip(name, count) VALUES(%s, %s)", (name, count))
		mysql.connection.commit()
		cur.close()
		flash('You added a new Equipment!!', 'success')
		return redirect(url_for('adminDash'))
	return render_template('addEquip.html', form = form)

class RemoveEquipForm(Form):
	name = RadioField('Name', choices = choices)
	count = IntegerField('Count', [validators.InputRequired()])


@app.route('/removeEquip', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def removeEquip():
	choices.clear()
	cur = mysql.connection.cursor()
	q = cur.execute("SELECT name FROM equip")
	b = cur.fetchall()
	for i in range(q):
		tup = (b[i]['name'],b[i]['name'])
		choices.append(tup)
	form = RemoveEquipForm(request.form)
	#num = data['count']
	if request.method == 'POST' and form.validate():
		cur.execute("SELECT * FROM equip WHERE name = %s", [form.name.data])
		data = cur.fetchone()
		app.logger.info(data['count'])
		num = data['count']
		if num >= form.count.data and form.count.data>0:
			name = form.name.data
			count = form.count.data
			cur = mysql.connection.cursor()
			cur.execute("UPDATE equip SET count = count-%s WHERE name = %s", (count, name))
			mysql.connection.commit()
			cur.close()
			choices.clear()
			flash('You successfully removed some of your equipment!!', 'success')
			return redirect(url_for('adminDash'))
		else:
			flash('you must enter valid number', 'danger')
	return render_template('removeEquip.html', form = form)

choices2 = []

class AddMemberForm(Form):

	name = StringField('Name', [validators.Length(min=1, max=50)])
	username = StringField('Username', [validators.InputRequired(), validators.NoneOf
	(values = values, message = "Username already taken, Please try another")])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Passwords do not match')
	])
	confirm = PasswordField('Confirm Password')
	role = StringField('role', [validators.Length(min=1, max=20)])
	email = StringField('email', [validators.Length(min = 1, max = 100)])
	# city = StringField('City', [validators.Length(min = 1, max = 100)])
	# phone = StringField('Phone', [validators.Length(min = 1, max = 100)])


@app.route('/addMember', methods = ['GET', 'POST'])

def addMember():
	page_name = "Register"
	choices.clear()
	choices2.clear()
	cur = mysql.connection.cursor()

	q = cur.execute("SELECT username FROM players")
	b = cur.fetchall()
	for i in range(q):
		values.append(b[i]['username'])

	cur.close()

	form = AddMemberForm(request.form)
	if request.method == 'POST' and form.validate():
		#app.logger.info("setzdgxfhcgjvkhbjlkn")
		name = form.name.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))
		email = form.email.data
		role = form.role.data

		cur = mysql.connection.cursor()
		try:
			cur.execute("INSERT INTO players(name, username, password, role, email) VALUES(%s, %s, %s, %s, %s)",
					(name, username, password, role, email))
		except:
			flash('DB Insert failed.', 'error')
			cur.close()
			return render_template('addMember.html', form=form, page_name=page_name)

		mysql.connection.commit()
		cur.close()
		choices2.clear()
		choices.clear()
		session['logged_in'] = True
		session['username'] = username
		session['role'] = role
		flash('You are added as a new game player!!', 'success')

		return redirect(url_for('profile', username = username, page_name=page_name))
	return render_template('addMember.html', form=form, page_name=page_name)


@app.route('/deleteMember', methods = ['GET', 'POST'])
@is_logged_in
@is_recep_level
def deleteMember():
	choices.clear()
	cur = mysql.connection.cursor()
	q = cur.execute("SELECT username FROM members")
	b = cur.fetchall()
	for i in range(q):
		tup = (b[i]['username'],b[i]['username'])
		choices.append(tup)
	form = DeleteRecepForm(request.form)
	if request.method == 'POST':
		username = form.username.data
		cur = mysql.connection.cursor()
		cur.execute("DELETE FROM members WHERE username = %s", [username])
		cur.execute("DELETE FROM info WHERE username = %s", [username])
		mysql.connection.commit()
		cur.close()
		choices.clear()
		flash('You deleted a member from the GYM!!', 'success')
		if(session['prof']==1):
			return redirect(url_for('adminDash'))
		return redirect(url_for('recepDash'))
	return render_template('deleteRecep.html', form = form)

@app.route('/viewDetails')
def viewDetails():
	page_name = "Account Profile"
	cur = mysql.connection.cursor()
	cur.execute("SELECT username FROM info WHERE username != %s", [session['username']])
	result = cur.fetchall()
	return render_template('viewDetails.html', result = result, page_name=page_name)


@app.route('/recepDash')
@is_recep_level
def recepDash():
	return render_template('recepDash.html')

class trainorForm(Form):
	name = RadioField('Select Username', choices = choices)
	date = DateField('Date', format='%Y-%m-%d')
	report = StringField('Report', [validators.InputRequired()])
	rate = RadioField('Result', choices = [('good', 'good'),('average', 'average'),('poor', 'poor') ])


@app.route('/trainorDash', methods = ['GET', 'POST'])
@is_logged_in
@is_trainor
def trainorDash():
	choices.clear()
	cur = mysql.connection.cursor()
	cur.execute("SELECT name, count FROM equip")
	equips = cur.fetchall()
	#app.logger.info(equips)
	cur.execute("SELECT username FROM members WHERE trainor = %s", [session['username']])
	members_under = cur.fetchall()
	cur.close()
	cur = mysql.connection.cursor()

	q = cur.execute("SELECT username FROM members WHERE trainor = %s", [session['username']])
	b = cur.fetchall()
	for i in range(q):
		tup = (b[i]['username'],b[i]['username'])
		choices.append(tup)
	cur.close()

	form = trainorForm(request.form)

	if request.method == 'POST':
		date = form.date.data
		username = form.name.data
		report = form.report.data
		rate = form.rate.data
		if rate == 'good':
			rate = 1
		elif rate == 'average':
			rate = 2
		else:
			rate = 3
		#app.logger.info(request.form.input_date)
		#app.logger.info(date)
		if datetime.now().date()<date:
			flash('You cannot predict furture, buoy!!', 'warning')
			choices.clear()
			return redirect(url_for('trainorDash'))


		cur = mysql.connection.cursor()
		p = cur.execute("SELECT date FROM progress WHERE username = %s", [username])
		entered = []
		q = cur.fetchall()
		for i in range(p):
			entered.append(q[i]['date'])


		if date in entered:
			cur.execute("UPDATE progress SET daily_result = %s, rate = %s WHERE username = %s and date = %s", (report,rate, username, date))
			mysql.connection.commit()
			cur.close()
			choices.clear()
			flash('Succesfully updated!', 'success')
			return redirect(url_for('trainorDash'))


		cur.execute("INSERT INTO progress(username, date, daily_result, rate) VALUES(%s, %s, %s, %s)", (username, date, report, rate))
		mysql.connection.commit()
		cur.close()
		choices.clear()
		flash('Progress updated and Reported', 'info')
		return redirect(url_for('trainorDash'))

	return render_template('trainorDash.html', equips = equips, form = form, members = members_under)


class UpdatePlanForm(Form):
	name = StringField('Plan Name', [validators.Length(min=1, max=50)])
	exercise = StringField('Exercise', [validators.Length(min = 1, max = 100)])
	reps = IntegerField('Reps', [validators.NumberRange(min = 1, max = 20)])
	sets = IntegerField('Sets', [validators.NumberRange(min = 1, max = 20)])


@app.route('/updatePlans', methods = ['GET', 'POST'])
@is_trainor
def updatePlans():
	form = UpdatePlanForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		exercise = form.exercise.data
		reps = form.reps.data
		sets = form.sets.data
		cur = mysql.connection.cursor()
		cur.execute("SELECT name, exercise FROM plans WHERE name = %s and exercise = %s", (name, exercise))
		result = cur.fetchall()
		if len(result)>0:
			cur.execute("UPDATE plans SET sets=%s, reps= %s WHERE name = %s and exercise = %s", (sets, reps, name, exercise))
		else:
			cur.execute("INSERT INTO plans(name, exercise, sets, reps) VALUES(%s, %s, %s, %s)", (name, exercise, sets, reps))
		mysql.connection.commit()
		cur.close()
		flash('You have updated the plan schemes', 'success')
		return redirect(url_for('trainorDash'))
	return render_template('addPlan.html', form = form)

class GameLevelForm(Form):
	glevel = SelectField('Select a game level:', validators=[InputRequired()],
						 choices=[('GP', 'Guru Play'),
								  ('CP', 'Challenger Play'),
								  ('EP', 'Easy Play')])

	ggoal = SelectField('Select a game goal:', validators=[InputRequired()],
						 choices=[('CA', 'Career Achievement'),
								  ('MA', 'Money Achievement'),
								  ('IA', 'Investment Achievement'),
								  ('AA', 'Acquisitions Achievement')])

@app.route('/memberDash/<string:username>', methods=['GET', 'POST'])
@is_logged_in
def memberDash(username):
	page_name = "Dashboard"
	if username!=session['username']:
		flash('You aren\'t authorised to view other\'s Dashboards', 'danger')
		return redirect(url_for('memberDash', username=session['username'], page_name=page_name))
	form = GameLevelForm()
	if request.method == 'POST' and form.validate():
		selected_level = form.glevel.data
		selected_goal = form.ggoal.data
		# Process the selected level
		flash("You selected: {selected_level}", "success")
		return redirect(url_for('memberDash', username=username, page_name=page_name))
	return render_template('memberDash.html', user=username, form=form, page_name=page_name)



@app.route('/profile/<string:username>')
@is_logged_in
def profile(username):
	page_name = "Profile"
	if username == session['username']:
		cur = mysql.connection.cursor()
		cur.execute("SELECT * FROM info WHERE username = %s", [username])
		result = cur.fetchone()
		return render_template('profile.html', result=result, page_name=page_name)
	return redirect(url_for('memberDash', username=username, page_name=page_name))
	flash('You cannot view other\'s profile', 'warning')
	if session['prof']==3:
		return redirect(url_for('trainorDash'))
	return redirect(url_for('memberDash', username = username, page_name=page_name))


class EditForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	email = StringField('Email', [validators.Length(min = 1, max = 100)])
	# city = StringField('City', [validators.Length(min = 1, max = 100)])
	# phone = StringField('Phone', [validators.Length(min = 1, max = 100)])


@app.route('/edit_profile/<string:username>', methods = ['GET', 'POST'])
@is_logged_in
def edit_profile(username):
	page_name = "Edit Profile"

	if username != session['username']:
		flash('You aren\'t authorised to edit other\'s details', 'warning')
		if session['prof']==4:
			return redirect(url_for('memberDash', username = username, page_name=page_name))
		if session['prof']==1:
			return redirect(url_for('adminDash'))
		if session['prof']==2:
			return redirect(url_for('recepDash', username = username, page_name=page_name))
		if session['prof']==3:
			return redirect(url_for('trainorDash', username = username, page_name=page_name))

	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM info WHERE username = %s", [username]);
	result = cur.fetchone()

	form = EditForm(request.form)

	form.name.data = result['name']
	form.email.data = result['Email']
	# form.city.data = result['city']
	# form.phone.data = result['phone']

	cur.close()

	if request.method == 'POST' and form.validate():
		#app.logger.info("setzdgxfhcgjvkhbjlkn")
		name = request.form['name']
		email = request.form['email']

		app.logger.info(name)
		app.logger.info(email)

		cur = mysql.connection.cursor()

		q = cur.execute("UPDATE info SET name = %s, email = %s WHERE username = %s", (name, email, username))
		app.logger.info(q)
		mysql.connection.commit()
		cur.close()
		flash('You successfully updated your profile!!', 'success')
		if session['prof']==4:
			return redirect(url_for('memberDash', username = username, page_name=page_name))
		if session['prof']==1:
			return redirect(url_for('adminDash'))
		if session['prof']==2:
			return redirect(url_for('recepDash', username = username, page_name=page_name))
		if session['prof']==3:
			return redirect(url_for('trainorDash', username = username, page_name=page_name))
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
	#manager = Manager(app)
	#manager.secret_key = '528491@siva'
	#manager.run()
	app.run()