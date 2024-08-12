from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
from ts_validation import ChangePasswordForm, AddMemberForm, EditForm, GameForm, GameLevelForm


class DB_Mgr:
    def __init__(self, obj):
        self.mysql = obj

    def get_player_record(self, username):
        cur = self.mysql.connection.cursor()
        q = cur.execute('SELECT * FROM players WHERE username = %s', [username])
        result = cur.fetchone()
        cur.close()
        return result, q

    def validate_password(self, data, password_candidate, username):
        password = data['password']
        status = "NOK"
        if sha256_crypt.verify(password_candidate, password):
            session['logged_in'] = True
            session['username'] = username
            session['role'] = data['role']
            session['player_number'] = 1
            session['player_round'] = 1
            session['player_move'] = 1
            status = "OK"
        return status

    def update_password(self, username, form):
        status = "NOK"
        new = form.new_password.data
        entered = form.old_password.data
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT password FROM players WHERE username = %s", [username])
        old = (cur.fetchone())['password']
        cur.close()
        if sha256_crypt.verify(entered, old):
            cur.execute("UPDATE players SET password = %s WHERE username = %s", (sha256_crypt.encrypt(new), username))
            self.mysql.connection.commit()
            cur.close()
            status = "OK"
        return status

    def get_game_players(self, game_ID):
        status = "NOK"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute("SELECT username FROM players WHERE game_ID = %s", [game_ID])
            users = cur.fetchall()
            cur.close()
            status = "OK"
        except Exception as e:
            print(f"Database error: {e}")
            users = []
        return status, users

    def update_player_game_card(self, username, player_number, gstatus):
        status = "NOK"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute("UPDATE players SET player_number = %s, status = %s WHERE username = %s",
                        (player_number, gstatus, username))
            self.mysql.connection.commit()
            cur.close()
            status = "OK"
        except Exception as e:
            print(f"Database error: {e}")
        return status

    def get_players_game_card(self, game_ID):
        status = "NOK"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute("SELECT username, player_number, status FROM players where game_ID = %s", [game_ID])
            players = cur.fetchall()
            cur.close()
            status = "OK"
        except Exception as e:
            print(f"Database error: {e}")
            players = []
        return status, players

    def get_game_data(self, username):
        status = "NOK"
        cur = self.mysql.connection.cursor()
        q = cur.execute("SELECT * FROM game where username = %s", [username])
        result = cur.fetchone()
        cur.close()
        status = "OK"
        return status, result

    def update_game(self, form):
        glevel = form.glevel.data
        ggoal = form.ggoal.data
        player_count = form.player_count.data
        status = form.status.data
        game_ID = form.game_ID.data
        start_date = form.start_date.data
        username = session.get('username')
        population = form.population.data
        pop_chg = form.pop_chg.data

        status = "NOK"
        cur = self.mysql.connection.cursor()
        q = cur.execute("UPDATE game "
                        "SET game_level = %s, game_goal = %s player_count = %s,"
                        " status = %s, start_date = %s, username = %s,"
                        " population = %s, pop_chg = %s)"
                        " WHERE game_id = %s", (glevel, ggoal, player_count, status, start_date, username,
                                                population, pop_chg, game_ID))
        self.mysql.connection.commit()
        cur.close()
        status = "OK"
        return q, status

    def add_game(self, form):
        status = "NOK"
        cur = self.mysql.connection.cursor()
        glevel = form.glevel.data
        ggoal = form.ggoal.data
        player_count = form.player_count.data
        status = form.status.data
        game_ID = form.game_ID.data
        start_date = form.start_date.data
        username = session.get('username')
        population = form.population.data
        pop_chg = form.pop_chg.data
        gs_gdp = form.population.data * 100
        try:
            q = cur.execute("INSERT INTO game(username, game_ID, player_count, start_date, status, population, pop_chg,"
                            " game_level, game_goal, gs_gdp) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (username, game_ID, player_count, start_date, status, population, pop_chg,
                             glevel, ggoal, gs_gdp))
            self.mysql.connection.commit()
            cur.close()
            status = "OK"
        except:
            flash('DB Insert failed.', 'error')
            cur.close()
        return status, q

    def get_players(self):
        status = "NOK"
        values = []
        cur = self.mysql.connection.cursor()
        q = cur.execute("SELECT username FROM players")
        b = cur.fetchall()
        for i in range(q):
            values.append(b[i]['username'])
        cur.close()
        status = "OK"
        return status, values


    def add_player(self, form):
        status = "NOK"
        name = form.name.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        email = form.email.data
        role = request.form.get("roles")
        cur = self.mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO players(name, username, password, role, email) VALUES(%s, %s, %s, %s, %s)",
                        (name, username, password, role, email))
            self.mysql.connection.commit()
            cur.close()
            status = "OK"
            session['logged_in'] = True
            session['username'] = username
            session['role'] = role
        except:
            flash('DB Insert failed.', 'error')
            cur.close()
        return status

    def update_player(self, form):
        stat = "NOK"
        username = session['username']
        salary = form.salary.data
        game_ID = form.game_ID.data
        status = form.status.data

        cur = self.mysql.connection.cursor()
        q = cur.execute("UPDATE players SET status = %s, game_ID = %s, salary = %s WHERE username = %s",
                        (status, game_ID, salary, username))
        self.mysql.connection.commit()
        cur.close()
        stat = "OK"
        return stat, q

    def update_profile(self, form, username):
        stat = "NOK"
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        status = request.form['status']
        player_number = request.form['player_number']

        cur = self.mysql.connection.cursor()
        q = cur.execute("UPDATE players "
                        "SET name = %s, email = %s role = %s, status = %s, player_number = %s)"
                        " WHERE username = %s", (name, email, role, status, player_number, username))
        self.mysql.connection.commit()
        cur.close()
        stat = "OK"
        return stat, q

# test class
# Initialize Flask app
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Evenodd!512'
app.config['MYSQL_DB'] = 'takestock1.0'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)  # Properly initialize MySQL with the Flask app

# Create an instance of DB_Mgr
db = DB_Mgr(mysql)

# Test the methods directly within the application context
if __name__ == "__main__":
    with app.app_context():
        game_ID = "TS2024-07-14"
        status, users = db.get_game_players(game_ID)
        if status == "OK":
            print("Game Players:", users)
            # Example of updating player numbers
            for i, user in enumerate(users):
                username = user['username']
                gstatus = "Ready"
                update_status = db.update_player_game_card(username, i + 1, gstatus)
                if update_status == "OK":
                    print(f"Updated player number for {username}")
                else:
                    print(f"Failed to update player number for {username}")
            # Get detailed player information
            status, players = db.get_players_game_card(game_ID)
            if status == "OK":
                print("Player Details:", players)
                for i, player in enumerate(players):
                    print("Username: ", player['username'])
                    print("Player Number: ", player['player_number'])
                    print("Status: ", player['status'])

            else:
                print("Failed to retrieve player details")
        else:
            print("DB error")