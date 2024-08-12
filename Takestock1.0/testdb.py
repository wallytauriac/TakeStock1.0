from flask import Flask
from flask_mysqldb import MySQL

class DB_Mgr:
    def __init__(self, obj):
        self.mysql = obj

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

    def update_player_number(self, username, player_number):
        status = "NOK"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute("UPDATE players SET player_number = %s WHERE username = %s", (player_number, username))
            self.mysql.connection.commit()
            cur.close()
            status = "OK"
        except Exception as e:
            print(f"Database error: {e}")
        return status

    def get_players_with_details(self):
        status = "NOK"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute("SELECT username, player_number, status FROM players")
            players = cur.fetchall()
            cur.close()
            status = "OK"
        except Exception as e:
            print(f"Database error: {e}")
            players = []
        return status, players

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
                update_status = db.update_player_number(username, i + 1)
                if update_status == "OK":
                    print(f"Updated player number for {username}")
                else:
                    print(f"Failed to update player number for {username}")
            # Get detailed player information
            status, players = db.get_players_with_details()
            if status == "OK":
                print("Player Details:", players)
            else:
                print("Failed to retrieve player details")
        else:
            print("DB error")
