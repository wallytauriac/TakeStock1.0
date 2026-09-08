import pickle
import random
from random import randint, choice

from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from passlib.hash import sha256_crypt

from flask_mysqldb import MySQL
from ts_validation import ChangePasswordForm, AddMemberForm, EditForm, GameForm, GameLevelForm
import mysql
import mysql.connector
import random
from typing import Dict, Any, Optional, Tuple, Set
from mysql.connector import Error
from datetime import datetime

db_config = {
    'user': 'root',
    'password': 'Evenodd!512',
    'host': 'localhost',
    'database': 'takestock1.0'
}


class DB_Mgr:
    def __init__(self, obj):
        self.mysql = obj

    def get_player_investment_stats(self, player_number):
        status = "NOK"

        cur = self.mysql.connection.cursor()
        try:
            q = cur.execute('Select invest_type, count(invest_count) as inv_cnt FROM investments '
                            'where player_number = %s GROUP BY invest_type', [player_number])
        except Exception as e:
            print(f"DB Investment Statistics error: {e}")
        result = cur.fetchall()
        cur.close()
        status = "OK"
        return status, result

    def get_player_investment_history(self, player_number):
        status = "NOK"
        # conn = mysql.connector.connect(**db_config)
        # cur = conn.cursor(dictionary=True)
        cur = self.mysql.connection.cursor()
        try:
            q = cur.execute('Select * FROM investments '
                            'where player_number = %s', [player_number])
            result = cur.fetchall()
        except Exception as e:
            print(f"DB Investment History error: {e}")

        cur.close()
        status = "OK"
        return status, result

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

    def get_players_game_card(self, game_ID, allcolumn="N"):
        status = "NOK"
        try:
            cur = self.mysql.connection.cursor()
            if allcolumn == "N":
                cur.execute("SELECT username, player_number, status FROM players where game_ID = %s", [game_ID])
            else:
                cur.execute("SELECT * FROM players where game_ID = %s", [game_ID])
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

    def get_game_card(self, game_ID):
        status = "NOK"
        cur = self.mysql.connection.cursor()
        q = cur.execute("SELECT * FROM game WHERE game_ID = %s", [game_ID])
        result = cur.fetchone()
        cur.close()
        status = "OK"
        return status, result

    def put_game_card(self, gc):
        glevel = gc['game_level']
        ggoal = gc['game_goal']
        player_count = gc['player_count']
        status = gc['status']
        total_spending = gc['total_spending']
        total_earnings = gc['total_earnings']
        game_ID = gc['game_ID']
        population = gc['population']
        pop_chg = gc['population_chg']
        cur = self.mysql.connection.cursor()
        q = cur.execute("UPDATE game "
                        "SET game_level = %s, game_goal = %s, player_count = %s,"
                        " status = %s, total_spending = %s, total_earnings = %s,"
                        " population = %s, population_chg = %s"
                        " WHERE game_id = %s", (glevel, ggoal, player_count, status, total_spending, total_earnings,
                                                population, pop_chg, game_ID))
        self.mysql.connection.commit()
        cur.close()
        status = "OK"
        return status


    def update_game(self, form):
        glevel = form.glevel.data
        ggoal = form.ggoal.data
        player_count = form.player_count.data
        status = form.status.data
        game_ID = form.game_ID.data
        start_date = form.start_date.data
        username = session.get('username')
        population = form.population.data
        population_chg = form.population_chg.data

        stat = "NOK"
        cur = self.mysql.connection.cursor()

        q = cur.execute("UPDATE game "
                        "SET game_level = %s, game_goal = %s, player_count = %s,"
                        " status = %s, start_date = %s, username = %s,"
                        " population = %s, population_chg = %s "
                        " WHERE game_id = %s",
                        (glevel, ggoal, player_count, status, start_date, username, population, population_chg, game_ID)
                        )
        self.mysql.connection.commit()
        cur.close()
        stat = "OK"
        return q, stat

    def update_game_from_setup(self, form):
        glevel = form.glevel.data
        ggoal = form.ggoal.data
        player_count = form.player_count.data
        game_ID = form.game_ID.data

        gdp = 1000000

        stat = "NOK"
        cur = self.mysql.connection.cursor()

        q = cur.execute("UPDATE game "
                        "SET game_level = %s, game_goal = %s, player_count = %s,"
                        " gdp = %s "
                        " WHERE game_id = %s",
                        (glevel, ggoal, player_count, gdp, game_ID)
                        )
        self.mysql.connection.commit()
        cur.close()
        stat = "OK"
        return q, stat

    def update_game_player(self, amount, gc, dataopt):
        stat = "NOK"
        username = dataopt['user']
        data = dataopt['data']
        if "buy_type" in data:
            buy_type = data['buy_type']
        else:
            buy_type = "OTHR"
        game_ID = gc['game_ID']
        round_count = data['player_round']
        move_count = data['player_move']
        total_spending = float(gc['total_spending']) + float(amount)
        player_number = data['player_number']
        cash_on_hand = 0
        cur = self.mysql.connection.cursor()
        q = cur.execute("UPDATE game "
                        "SET round_count = %s, move_count = %s, total_spending = %s "
                        " WHERE game_id = %s",
                        (round_count, move_count, total_spending, game_ID)
                        )
        self.mysql.connection.commit()
        q = cur.execute('SELECT * FROM players WHERE username = %s', [username])
        result = cur.fetchone()
        if result['cash_on_hand'] > float(amount):
            cash_on_hand = result['cash_on_hand'] - float(amount)
        stck = result['stock_value']
        ppty = result['property_value']
        bus = result['business_value']
        comm = result['commodity_value']
        othr = result['other_investments']
        if buy_type == "bs":
            stck = float(stck) + float(amount)
        elif buy_type == "bp":
            ppty = float(ppty) + float(amount)
        elif buy_type == "bb":
            bus = float(bus) + float(amount)
        elif buy_type == "bc":
            comm = float(comm) + float(amount)
        else:
            othr = float(othr) + float(amount)

        sql = ("UPDATE players SET cash_on_hand = %s, stock_value = %s, property_value = %s, business_value = %s, commodity_value = %s, other_investments = %s WHERE game_id = %s and username = %s")
        val = (cash_on_hand, stck, ppty, bus, comm, othr, game_ID, username)
        try:
            cur.execute(sql, val)
        except Exception as e:
            print(f"Database error: {e}")
        self.mysql.connection.commit()
        cur.close()
        stat = "OK"
        return stat

    def get_investments_by_code(self, code, player_number):
        status = "NOK"
        cur = self.mysql.connection.cursor()
        q = cur.execute("SELECT * FROM investments WHERE invest_type = %s and player_number = %s", [code, player_number])
        result = cur.fetchall()
        cur.close()
        if q > 0:
            status = "OK"
        else:
            print("Database error:", "get_investments_by_code failed")
        return status, result

    def get_investments_by_desc(self, code, desc, player_number):
        status = "NOK"
        cur = self.mysql.connection.cursor()
        q = cur.execute(
            "SELECT * FROM investments WHERE invest_type = %s and player_number = %s and invest_description = %s",
            [code, player_number, desc])
        result = cur.fetchall()
        cur.close()
        if q > 0:
            status = "OK"
        else:
            print("Database error:", "get_investments_by_desc failed")
        return status, result
    def update_investment_by_id(self, inv_data):
        # Investment update code lost...This code needs rebuild
        status = "OK"
        return status


    def update_goal_by_id(self, goal_data):
        # Goal update code lost...This code needs rebuild
        status = "OK"
        return status


    def insert_investments_from_sale(self, invest_data):
        # Dictionary passed with data to update
        stat = "NOK"
        # Constructing the SQL update statement
        invest_type = invest_data['invest_type']
        invest_count = invest_data['invest_count']
        invest_amount = invest_data['invest_amount']
        invest_description = invest_data['invest_description']
        player_number = invest_data['player_number']
        invest_value = invest_data['invest_value']
       # insert_clause = ', '.join((f"{keys}" for keys in invest_data.keys()))
       # insert_clause = ', '.join(
       #     [f"'{values}'" if i in [0, 3] else f"{values}" for i, values in enumerate(invest_data.values())])
        cur = self.mysql.connection.cursor()

        sql = (
            "INSERT INTO investments (invest_type, invest_count, invest_amount, invest_description, player_number,"
            " invest_value) VALUES(%s, %s, %s, %s, %s, %s)")
        print("Query ", sql)

        val = (invest_type, invest_count, invest_amount, invest_description, player_number, invest_value)
        print("Value ", val)
        cur.execute(sql, val)

        self.mysql.connection.commit()
        cur.close()
        stat = "OK"
        return stat

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
        population_chg = form.population_chg.data
        gs_gdp = form.population.data * 100
        try:
            q = cur.execute("INSERT INTO game(username, game_ID, player_count, start_date, status, population, pop_chg,"
                            " game_level, game_goal, gs_gdp) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (username, game_ID, player_count, start_date, status, population, population_chg,
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

    def update_player2(self, result):
        stat = "NOK"
        username = result['username']
        salary = result['salary']
        game_ID = result['game_ID']
        cash_on_hand = result['cash_on_hand']
        status = "Ready"

        city_addr = "1248.70"
        choice = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        inheritance = random.choice(choice)
        salary = float(salary) + 1500.00
        cash_on_hand = float(cash_on_hand) + float(inheritance * 7500)

        cur = self.mysql.connection.cursor()
        q = cur.execute("UPDATE players SET status = %s, game_ID = %s, salary = %s, cash_on_hand = %s WHERE username = %s",
                        (status, game_ID, salary, cash_on_hand, username))
        self.mysql.connection.commit()
        cur.close()
        stat = "OK"
        return stat

    def update_gp(self, gp):
        stat = "NOK"
        username = gp.username
        salary = gp.salary
        cash_on_hand = gp.cash_on_hand
        property_value = gp.property_value
        stock_value = gp.stock_value
        commodity_value = gp.commodity_value
        business_value = gp.business_value
        othr_value = gp.othr_value

        cur = self.mysql.connection.cursor()
        q = cur.execute("UPDATE players SET cash_on_hand = %s, salary = %s, "
                        " property_value = %s, stock_value = %s, commodity_value = %s, "
                        " business_value = %s, othr_value = %s WHERE username = %s",
                        (cash_on_hand, salary, property_value, stock_value, commodity_value,
                         business_value, othr_value, username))
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

    def get_table_data(self, table_name):
        status = "NOK"
        cur = self.mysql.connection.cursor()
        sql = "SELECT * FROM " + table_name
        q = cur.execute(sql)
        b = cur.fetchall()
        cur.close()
        status = "OK"
        return status, b

    def get_table_row(self, table_name, row_id):
        status = "NOK"
        cur = self.mysql.connection.cursor()
        try:
            # Assuming 'id' is the primary key in the table
            query = f"SELECT * FROM {table_name} WHERE id = %s"
            cur.execute(query, (row_id,))
            result = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
            cur.close()
            status = "OK"
            return status, result, column_names
        except Exception as e:
            print(f"An get_table_row error occurred: {e}")
            cur.close()
            return status, [], []

    def delete_investments_by_code(self, code, player_number):
        status = "NOK"
        cur = self.mysql.connection.cursor()
        try:
            query = "DELETE FROM investments WHERE invest_type = %s AND player_number = %s"
            cur.execute(query, (code, player_number))
            self.mysql.connection.commit()
            cur.close()
            status = "OK"
        except Exception as e:
            print(f"An Delete_Investments by Code error occurred: {e}")
            self.mysql.connection.rollback()
            cur.close()
        return status

    def delete_investment_by_id(self, id):
        status = "NOK"
        cur = self.mysql.connection.cursor()
        try:
            query = "DELETE FROM investments WHERE invest_id = %s"
            cur.execute(query, (id,))
            self.mysql.connection.commit()
            cur.close()
            status = "OK"
        except Exception as e:
            print(f"Delete_Investment by ID error occurred: {e}")
            self.mysql.connection.rollback()
            cur.close()
        return status

    def get_requests_by_ctgy(self, ctgy):
        status = "NOK"
        cur = self.mysql.connection.cursor()
        q = cur.execute("SELECT * FROM requests WHERE ctgy = %s", [ctgy])
        result = cur.fetchall()
        cur.close()
        if q > 0:
            status = "OK"
        else:
            print("Database error:", "get_requests_by_ctgy failed")
        return q, result


    def get_player_by_number(self, player_number):
        status = "NOK"
        cur = self.mysql.connection.cursor()
        try:
            query = "SELECT * FROM players WHERE player_number = %s"
            cur.execute(query, (player_number,))
            result = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
            cur.close()
            if result:
                status = "OK"
                player_data = dict(zip(column_names, result[0]))
                return status, player_data
            else:
                return status, {}
        except Exception as e:
            print(f"An error in get_player_by_ number occurred: {e}")
            cur.close()
            return status, {}

    def update_player_by_flag(self, player_data):
        status = "NOK"
        cur = self.mysql.connection.cursor()
        try:
            # Dynamically build the query based on provided player_data keys and values
            set_clause = ", ".join([f"{key} = %s" for key in player_data.keys() if key != 'player_number'])
            query = f"UPDATE players SET {set_clause} WHERE player_number = %s"
            values = list(player_data.values())
            cur.execute(query, values)
            self.mysql.connection.commit()
            cur.close()
            status = "OK"
        except Exception as e:
            print(f"An error in update_player_by_flag occurred: {e}")
            cur.close()
        return status

    def get_positions_data(self, table_name):
        status = "NOK"
        cur = self.mysql.connection.cursor()
        try:
            query = f"SELECT * FROM {table_name}"
            cur.execute(query)
            result = cur.fetchall()
            cur.close()
            status = "OK"
            return len(result), result
        except Exception as e:
            print(f"An error in get_positions_data occurred: {e}")
            cur.close()
            return 0, []

    def clear_positions_data(self, table_name):
        status = "OK"
        if table_name == "positions":
            status = "NOK"
            cur = self.mysql.connection.cursor()
            try:
                query = f"DELETE FROM {table_name}"
                cur.execute(query)
                self.mysql.connection.commit()
                cur.close()
                status = "OK"
            except Exception as e:
                print(f"An error in clear_positions_data occurred: {e}")
                cur.close()
        return status

    def update_positions_data(self, table_name, visited_positions):
        status = "NOK"
        listid = table_name

        cur = self.mysql.connection.cursor()
        try:
            for pos in visited_positions:
                query = f"INSERT INTO positions (list_id, value) VALUES (%s, %s)"
                cur.execute(query, (listid, pos))
            cur.close()
            self.mysql.connection.commit()
            cur.close()
            status = "OK"
        except Exception as e:
            print(f"An error in update_positions_data occurred: {e}")
            cur.close()
        return status

    def insert_billpay(self, billpay_data):
        status = "NOK"
        cur = self.mysql.connection.cursor()
        try:
            query = """
            INSERT INTO billpay (bill_type, bill_round, bill_amount, bill_description, player_number, bill_value, invest_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                billpay_data['bill_type'],
                billpay_data['bill_round'],
                billpay_data['bill_amount'],
                billpay_data['bill_description'],
                billpay_data['player_number'],
                billpay_data['bill_value'],
                billpay_data['invest_id']
            )
            cur.execute(query, values)
            self.mysql.connection.commit()
            cur.close()
            status = "OK"
        except Exception as e:
            print(f"An error in insert_billpay occurred: {e}")
            cur.close()
        return status

    def insert_roi_card(self, roi_data):
        status = "NOK"
        cur = self.mysql.connection.cursor()
        try:
            query = """
            INSERT INTO Investment_return (roi_type, roi_units, roi_rent, roi_BLDG_type, roi_PPTY_type, roi_Property, player_number, roi_price, max_qtrly_roi, ppty_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                roi_data['roi_type'],
                roi_data['roi_units'],
                roi_data['roi_rent'],
                roi_data['roi_BLDG_type'],
                roi_data['roi_PPTY_type'],
                roi_data['roi_Property'],
                roi_data['player_number'],
                roi_data['roi_price'],
                roi_data['max_qtrly_roi'],
                roi_data['ppty_id']
            )
            cur.execute(query, values)
            self.mysql.connection.commit()
            cur.close()
            status = "OK"
        except Exception as e:
            print(f"An error in insert_roi_card occurred: {e}")
            cur.close()
        return status

    def serialize_value(self, value):
        if isinstance(value, dict):
            return {k: self.serialize_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.serialize_value(item) for item in value]
        elif isinstance(value, tuple):
            return tuple(self.serialize_value(item) for item in value)
        elif isinstance(value, (datetime)):
            return value.isoformat()
        return value

    def pickle_save(self, session_id, key, value, data_type):
        serialized_value = pickle.dumps(self.serialize_value(value))
        cursor = self.mysql.connection.cursor()
        cursor.execute(
            "REPLACE INTO sessions (id, session_key, session_value, data_type) VALUES (%s, %s, %s, %s)",
            (session_id, key, serialized_value, data_type)
        )
        self.mysql.connection.commit()
        cursor.close()

    def deserialize_value(self, value):
        if isinstance(value, dict):
            return {k: (datetime.strptime(v, '%a, %d %b %Y %H:%M:%S GMT').strftime('%a, %d %b %Y %H:%M:%S GMT') if k in date_columns else self.deserialize_value(v)) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.deserialize_value(item) for item in value]
        elif isinstance(value, tuple):
            return tuple(self.deserialize_value(item) for item in value)
        return value

    def pickle_get(self, session_id):
        cursor = self.mysql.connection.cursor()
        cursor.execute("SELECT session_key, session_value, data_type FROM sessions WHERE id = %s", (session_id,))
        session_data = cursor.fetchall()
        cursor.close()

        sessions = {}
        for row in session_data:
            key = row['session_key']
            value = pickle.loads(row['session_value'])
            sessions[key] = self.deserialize_value(value)
        return sessions


"""
# test class
# Initialize Flask app
app = Flask(__name__)



mysql = MySQL(app)  # Properly initialize MySQL with the Flask app
# Create an instance of DB_Mgr
db = DB_Mgr(mysql)
status, investments = db.get_player_investment_history(session['player_number'])

if status == "OK":
    for item in investments:
        print(item)
    # type = ['PPTY', 'STCK', 'BUS', 'OTHR']
    # desc = ['Personal House', 'Airline   (Count=100)', 'Partnership (Wally Mart)', 'Diamond Necklace']
    # inv = ['$  100,000',
    #        '$    1,000',
    #        '$   50,000',
    #        '$    2,000'
    #        ]
    # val = ['$  110,000',
    #        '$    2,000',
    #        '$   70,000',
    #        '$    5,000'
    #        ]

if __name__ == "__main__":
    with app.app_context():
        # MySQL configurations
        app.config['MYSQL_HOST'] = 'localhost'
        app.config['MYSQL_USER'] = 'root'
        app.config['MYSQL_PASSWORD'] = 'Evenodd!512'
        app.config['MYSQL_DB'] = 'takestock1.0'
        app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

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
"""