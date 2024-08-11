from datetime import date, timedelta, datetime
from decimal import Decimal

import mysql.connector
import random
from random import randint, random
from typing import Dict, Any, Optional, Tuple, Set
from mysql.connector import Error
from ts_database import *


class PriceIndex:
    """
    The PriceIndex class interacts with a MySQL table representing a Price index.
    It loads the table data into memory upon instantiation and provides methods
    to select the center row, move randomly up or down from the current position,
    and recalculate the value of the current position.
Attributes:
        db_config (dict): Database configuration.
        table_name (str): Name of the MySQL table to load.  [Stocks, Commodities ]
        data (list of dict): The table data loaded into memory.
        center_row (int): The index of the center row of the data.
        current_position (int): The current position in the data.
    """
    """
        Initializes the PriceIndex class.
Parameters:
            db_config (dict): Database configuration containing host, user, password, and database name.
            table_name (str): Name of the MySQL table to load.
    """

    def __init__(self, db_config, table_name):
        self.db_config = db_config
        self.table_name = table_name
        self.data = self.load_data()
        self.center_row = len(self.data) // 2
        self.current_position = self.center_row

    def load_data(self) -> list:
        """
        Loads data from the MySQL table into memory.
        Returns: list of dict: The table data loaded into memory.
        """
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {self.table_name}")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data

    def get_center_row(self) -> dict:
        """
        Returns the center row of the data.
        Returns: dictionary
        """
        return self.data[self.center_row]

    def get_current_position(self) -> dict:
        return self.data[self.current_position]

    def move_randomly(self) -> dict:
        """
        Moves randomly from the current position one or more rows up or down.
        Parameters: direction (random -1 or +1) to set the direction
                    steps (random int): Number of steps to move up or down.
        Returns:    dict: The new current position row.
        """
        direction = random.choice([-1, 1])
        mylist = [0, 1, 2, 3, 3, 5, 2, 7]
        steps = random.choices(mylist, weights=[5, 5, 2, 1, 1, 4, 1, 1], k=1)
        # steps = random.randint(0, 7)
        x = self.current_position + direction * steps[0]
        new_position = max(0, min(x, len(self.data) - 1))
        self.current_position = new_position
        return self.data[self.current_position]

    def recalculate_value(self) -> float:
        """
        Recalculates the value of the current position.
Returns:    float: The recalculated value of the current position.
        """
        current_row = self.data[self.current_position]
        return sum(value for value in current_row.values() if isinstance(value, (int, float)))


class GameBoard:
    def __init__(self, db_config: Dict[str, Any], game_ID: str):
        self.db_config = db_config
        self.table_name = "game"
        self.game_ID = game_ID
        self.data: Optional[Dict[str, Any]] = self.load_data()
        self.player_count = 0
        self.move_count = 0
        self.gdp = 0
        self.population = 0
        self.pop_chg = 0.03
        self.total_spending = 0
        self.total_earnings = 0

    def load_data(self) -> Optional[Dict[str, Any]]:
        # Loads data from the MySQL table into memory.
        # Returns: Game variables as a dictionary or None if no data is fetched
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {self.table_name} WHERE game_ID = %s", (self.game_ID,))
        data = cursor.fetchone()
        cursor.close()
        conn.close()
        print(f"Fetched data: {data}")  # Debugging line
        return data

    def get_game_data(self):
        return self.data

    def get_cpi(self):
        credits = self.data.get('total_earnings')
        debits = self.data.get('total_spending')
        nl = [1, 2, 3]
        num = random.choice(nl)
        if credits > 0:
            cpi = ((debits / credits) / 10) + num
        else:
            cpi = 1.00
        return cpi

    def get_status(self) -> Optional[Any]:
        # Retrieves the status from the loaded data
        ndx = "status"
        if self.data:
            status = self.data.get(ndx, None)
        else:
            status = None
        return status

    def check_player_count(self):
        return self.data.get('player_count')

    def update_counts(self, value):
        self.data['move_count'] = value

    def get_move_count(self):
        return self.data.get("move_count")

    def update_gdp(self, value):
        self.data['gdp'] = value

    def update_population(self, value):
        self.data['population'] += value

    def get_game_level(self):
        glevel = self.data.get("game_level", None)
        return glevel

    def get_game_goal(self):
        return self.data.get('game_goal')

    def update_earnings(self, value):
        self.data['total_earnings'] += value

    def get_earnings(self):
        return self.data.get("total_earnings")

    def update_spending(self, value):
        self.data['total_spending'] += value

    def get_spending(self):
        return self.total_spending


class banker:
    def __init__(self):
        pass
    """
        *** During game start
        o declare their inheritance money which is what a player starts out with as cash-on-hand
        o set each players starting salary
        o tell each player their first event unless the player asks to buy or sell.
        
    	o The banker will address each player
		    ○   Manage player's next event
		    ○   End of Round Management (Pay salaries, Adj. Index/GDP)

    """

    def calc_inheritance(self, player_count):
        inherit = []
        max = 1000000
        for pc in range(player_count):
            inherit.append(round(max/(pc+1), 0))
        iv = random.choice(inherit)
        return iv

    def calc_salary(self, player_count):
        salaries = []
        max = 10000
        for pc in range(player_count):
            salaries.append(round(max/(pc+1), 0))
        sv = random.choice(salaries)
        return sv

class Players:
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.table_name = "players"
        self.data = {}
        self.player_number = 0
        self.cash_on_hand = 0
        self.property_value = 0
        self.stock_value = 0
        self.commodity_value = 0
        self.other_investments = 0
        self.job_level = 0

    def load_data(self, username):
        # Loads data from the MySQL table into memory.
        # Returns: Player variables as a dictionary or None if no data is fetched
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {self.table_name} WHERE username = %s", [username])
        data = {}
        data = cursor.fetchone()
        cursor.close()
        conn.close()
        print(f"Fetched data: {data}")  # Debugging line
        self.data = data
        return data

    def get_player_data(self):
        return self.data


class Game_Assets:
    def __init__(self, db_config, table_name):
        self.db_config = db_config
        self.table_name = table_name
        self.data = self.load_data()

    def load_data(self) -> list:
        """
        Loads data from the MySQL table into memory.
        Returns: list of dict: The table data loaded into memory.
        Valid Tables: business, jobcenter, lifecenter, learncenter, stockcenter
        """
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {self.table_name}")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data

    def get_row(self, id):
        arr = dict(self.data[id-1])
        return arr

class Game_Action:
    """
    • Game Action object - one per player
        • Move type (SP, TP, IV, or RP)
        • Move gain
        • Move loss
        • Travel (Y/N)
        • Economy ID (randomly generated)
        • Index ID
        • Action type array and index
    • Game Action methods
        • Instantiate
        • Get COH adjustment
        • Get economy ID
        • Get action data based on index ID
        • Update attributes

    """

    def __init__(self):
        self.initialize_move_attributes()
        self.initialize_travel()
        self.initialize_economy()
        self.initialize_index()
        self.initialize_action_type()

    def initialize_move_attributes(self):
        self.move_type = "SP"
        self.move_gain = 0
        self.move_loss = 0

    def initialize_travel(self):
        self.travel = "N"

    def initialize_economy(self):
        self.economy_ID = 25

    def initialize_index(self):
        self.index_ID = random.randint(1, 50)

    def initialize_action_type(self):
        self.action_type = [{}]

    # Setter methods for individual attributes
    def set_move_type(self, move_type):
        self.move_type = move_type

    def set_move_gain(self, move_gain):
        self.move_gain = move_gain

    def set_move_loss(self, move_loss):
        self.move_loss = move_loss

    def set_travel(self, travel):
        self.travel = travel

    def set_economy_ID(self, economy_ID):
        self.economy_ID = economy_ID

    def set_index_ID(self, index_ID):
        self.index_ID = index_ID

    def set_action_type(self, action_type):
        self.action_type = action_type

    # Method to update multiple attributes at once
    def update_attributes(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"{key} is not a valid attribute of {self.__class__.__name__}")


class gps:
    def __init__(self, db_config):
        self.db_config = db_config
        self.gps = self.load_attributes()

    def load_attributes(self):
        table_name = "address"
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()
            cursor.close()
            conn.close()
            # Debug print to check the structure
            print("Loaded attributes:", data)
            return data
        except Error as e:
            print(f"Error executing SELECT query: {e}")
            return []

    def get_all_addresses(self):
        return self.gps

    def get_address_by_id(self, address_id):
        for address in self.gps:
            if isinstance(address, dict) and 'id' in address:
                if address['id'] == address_id:
                    # print("Selected Address data: ", address)
                    return address
        return None

    def count_addresses(self):
        return len(self.gps)

    def address_find(self, address_id):
        row: dict
        for row in self.gps:
            if row['id'] == address_id:
                print("Address found: ", row['Address'])

    def calc_distance(self, address1, address2):
        point1 = address1.split(".")
        point2 = address2.split(".")
        return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])


"""
Step 3: Test Database Connection Independently
Run a standalone script to test the database connection and fetching data:

python
Copy code
import mysql.connector
from mysql.connector import Error

db_config = {
    'user': 'root',
    'password': 'Evenodd!512',
    'host': 'localhost',
    'database': 'Takestock1.0'
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM address")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    print("Data fetched successfully:", data)
except Error as e:
    print(f"Error: {e}")
"""


"""
************ Logic for testing Player Class *******************
# Testing Player class
db_config = {
    'user': 'root',
    'password': 'Evenodd!512',
    'host': 'localhost',
    'database': 'Takestock1.0'
}
username = "wallytauriac"
Player1 = Players(db_config)
player1 = Player1.load_data(username)
print("Username is: ", player1["username"])
"""
"""
************ Logic for testing GameBoard Class *******************
# Example usage for GameBoard class
db_config = {
    'user': 'root',
    'password': 'Evenodd!512',
    'host': 'localhost',
    'database': 'Takestock1.0'
}
game_ID = "TS2024-07-14"
game_board = GameBoard(db_config, game_ID)
print(game_board.get_status())
"""
"""
************ Logic for testing PriceIndex Class *******************
# Example Usage
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Evenodd!512',
    'database': 'takestock1.0'
}

def print_elements(row, key="id"):
    for column in row:
        if column == key:
            print(column, ":", row[column])
            break
price_index = PriceIndex(db_config, 'stocks')
center_row = price_index.get_center_row()
print("Center Row:", center_row)
print_elements(center_row, key="id")
print_elements(center_row, key="oNg")
for i in range(5):
    print("iteration: ", i)
    current_position = price_index.get_current_position()
    print("Current Position:", current_position)
    new_position = price_index.move_randomly()
    print("New Position:", new_position)
    recalculated_value = price_index.recalculate_value()
    print("Recalculated Value:", recalculated_value)
"""
"""
************ Logic for testing Game_Action Class *******************
# Usage
obj = Game_Action()

# Update individual attributes
obj.set_move_type("New Move Type")
obj.set_travel("S")

# Update multiple attributes at once
obj.update_attributes(move_gain=10, move_loss=5, index_ID=42)

action_data = vars(obj)

# Check updates
print(action_data)
print(action_data["economy_ID"])
print(obj.index_ID)
"""
"""
************ Logic for testing GPS Class *******************
# Execution code
db_config = {
    'user': 'root',
    'password': 'Evenodd!512',
    'host': 'localhost',
    'database': 'Takestock1.0'
}
obj = gps(db_config)
addr_data = vars(obj)
print(addr_data)
property = obj.get_address_by_id(1)
print("Property location: ", property['Address'])
obj.address_find(2)
"""
