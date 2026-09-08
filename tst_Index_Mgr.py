from flask import Flask
from flask_mysqldb import MySQL
import random

class DB_Mgr:
    def __init__(self, obj):
        self.mysql = obj

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

class IndexMgr:
    def __init__(self, tablelist):
        self.index_table = {}

        for table in tablelist:
            self.table_name = table
            self.data = self.load_data()

            self.index_table[table] = {
                "low": self.data["low"],
                "high": self.data["high"],
                "current": self.data["current"],
            }

        print(f"Loaded Index Table data: {self.index_table}")

    def load_data(self):
        """
        Loads a row of data from the MySQL table into memory.
        Returns: dict: The table data loaded into memory.
        """
        status, result = db.get_positions_data(self.table_name)
        if status == "NOK":
            raise Exception("Error Condition: Load investment table failed...")

        tbl_length = int(len(result))
        rng = random.Random()

        data = {}
        data["low"] = int(1)
        data["high"] = tbl_length
        data["current"] = rng.randint(data["low"], data["high"])
        return data

    def get_table_pointer(self, table_name):
        return self.index_table[table_name]["current"]

    def reset_table_pointer(self, table_name):
        status = "NOK"
        rng = random.Random()
        low_nbr = self.index_table[table_name]["low"]
        high_nbr = self.index_table[table_name]["high"]
        nbr = int(rng.randint(low_nbr, high_nbr))
        self.index_table[table_name]["current"] = nbr
        status = "OK"
        return status


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
        tablelist = ["commodities", "address"]
        im = IndexMgr(tablelist)
        ptr = im.get_table_pointer("commodities")
        print(f"Table commodities Get ptr: {ptr}")
        stat = im.reset_table_pointer("commodities")
        ptr = im.get_table_pointer("commodities")
        print(f"Table commodities Get reset ptr: {ptr}")
