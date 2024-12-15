from flask import Flask, g
from flask_mysqldb import MySQL
import pickle
from datetime import datetime, date

app = Flask(__name__)

# Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Evenodd!512'
app.config['MYSQL_DB'] = 'takestock1.0'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def save_session_to_db(session_id, key, value, data_type):
    serialized_value = pickle.dumps(serialize_value(value))
    cursor = g.mysql.connection.cursor()
    cursor.execute(
        "REPLACE INTO sessions (id, session_key, session_value, data_type) VALUES (%s, %s, %s, %s)",
        (session_id, key, serialized_value, data_type)
    )
    g.mysql.connection.commit()
    cursor.close()

def get_session_from_db(session_id):
    cursor = g.mysql.connection.cursor()
    cursor.execute("SELECT session_key, session_value, data_type FROM sessions WHERE id = %s", (session_id,))
    session_data = cursor.fetchall()
    cursor.close()

    sessions = {}
    for row in session_data:
        key = row['session_key']
        value = pickle.loads(row['session_value'])
        sessions[key] = deserialize_value(value)
    return sessions

def serialize_value(value):
    if isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [serialize_value(item) for item in value]
    elif isinstance(value, tuple):
        return tuple(serialize_value(item) for item in value)
    elif isinstance(value, (datetime, date)):
        return value.isoformat()  # Convert date/datetime to string
    return value

def xdeserialize_value(value):
    date_columns = ['start_date', 'end_date', 'birthdate', 'login_time']
    if isinstance(value, dict):
        return {k: deserialize_value(v) if k not in date_columns else datetime.strptime(v, '%a, %d %b %Y %H:%M:%S GMT') for k, v in value.items()}
    elif isinstance(value, list):
        return [deserialize_value(item) for item in value]
    elif isinstance(value, tuple):
        return tuple(deserialize_value(item) for item in value)
    return value
def deserialize_value(value):
    date_columns = ['start_date', 'end_date', 'birthdate', 'login_time']
    if isinstance(value, dict):
        return {k: (datetime.strptime(v, '%a, %d %b %Y %H:%M:%S GMT').strftime('%a, %d %b %Y %H:%M:%S GMT') if k in date_columns else deserialize_value(v)) for k, v in value.items()}
    elif isinstance(value, list):
        return [deserialize_value(item) for item in value]
    elif isinstance(value, tuple):
        return tuple(deserialize_value(item) for item in value)
    return value

@app.route('/set/<key>')
def set_session(key):

    username = "John Doe"
    user_prefs = {'theme': 'dark', 'language': 'en'}
    shopping_cart = ['apple', 'banana', 'orange']
    user_roles = [{'role': 'admin', 'permissions': ['read', 'write']}, {'role': 'guest', 'permissions': ['read']}]
    gc = {'cpi': '1.60', 'game_ID': 'TS2024-07-14', 'game_goal': 'CA', 'game_level': 'GP', 'gdp': '2.00',
           'gs_gdp': '0.06', 'move_count': 3, 'player_count': 2, 'population': 1010200, 'population_chg': '0.00',
           'round_count': 2, 'start_date': 'Sun, 14 Jul 2024 00:00:00 GMT', 'status': 'Active',
           'total_earnings': '1333333.00', 'total_spending': '531060.00', 'username': 'wallytauriac'}

    value = None
    type = None
    if key == "username":
        value = username
        type = "str"
    elif key == "user_prefs":
        value = user_prefs
        type = "dict"
    elif key == "shopping_cart":
        value = shopping_cart
        type = "list"
    elif key == "user_roles":
        value = user_roles
        type = "listd"
    elif key == "game_data":
        value = gc
        type = "dict"

    session_id = 'test_session'  # For testing, using a static session ID
    save_session_to_db(session_id, key, value, type)
    return f'Session data set: {key}={value} and type is {type}'

@app.route('/get/<key>')
def get_session(key):
    session_id = 'test_session'  # For testing, using a static session ID
    data = get_session_from_db(session_id)
    return f'Session data: {data.get(key, "Not Found")}'

@app.before_request
def before_request():
    g.mysql = mysql

if __name__ == '__main__':
    app.run(debug=True)
