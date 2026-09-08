from flask import Flask
from flask_mysqldb import MySQL

class DB_Mgr:
    def __init__(self, obj):
        self.mysql = obj

    def get_table_data(self, table_name):
        status = "NOK"
        cur = self.mysql.connection.cursor()
        #cur.execute("SELECT DATABASE(), @@hostname, @@port, @@socket, CURRENT_USER();")
        #print("Connection Data2: ", cur.fetchone())
        sql = "SELECT * FROM " + table_name + ";"
        #sql = "SHOW CREATE TABLE stocks"
        print("SQL Data: ", repr(sql))
        q = cur.execute(sql)
        b = cur.fetchall()
        cur.close()
        status = "OK"
        return status, b

    def get_positions_data(self, table_name):
        status = "NOK"
        cur = self.mysql.connection.cursor()
        #cur.execute("SELECT DATABASE(), @@hostname, @@port, @@socket, CURRENT_USER();")
        #print("Connection Data1", cur.fetchone())
        try:
            # query = f"SELECT * FROM {table_name};"
            query = "SELECT COUNT(*) FROM stocks"
            print("QUERY Data: ", repr(query))
            cur.execute(query)
            result = cur.fetchall()
            cur.close()
            status = "OK"
            return status, result
        except Exception as e:
            print(f"An error in get_positions_data occurred: {e}")
            cur.close()
            return 0, []

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
        table_name = "stocks"
        status, stocks = db.get_positions_data(table_name)
        if status == "OK":
            print("Stock Data:", stocks)
        else:
            print("Failed to retrieve Stock1 details")
        # Get detailed player information
        status, stock2 = db.get_table_data(table_name)
        if status == "OK":
            print("Stock Details:", stock2)
        else:
            print("Failed to retrieve Stock2 details")
