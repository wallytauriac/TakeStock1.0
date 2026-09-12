import decimal
from datetime import date, timedelta, datetime
from decimal import Decimal
import mysql
import mysql.connector
import random
import re
import copy
from typing import Dict, Any, Optional, Tuple, Set
from mysql.connector import Error
from ts_database import *
from ts_cycle import *
from app_factory import create_app, mysql
db = DB_Mgr(mysql)

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

    def __init__(self, table_name):
        self.table_name = table_name
        self.data = self.load_data()
        self.center_row = len(self.data) // 2
        self.current_position = self.center_row
        self.ids = list(range(1, len(self.data)))
        self.max_attempts = 100  # Maximum number of attempts to find a new position

    def load_data(self) -> list:
        """
        Loads data from the MySQL table into memory.
        Returns: list of dict: The table data loaded into memory.
        """
        status, data = db.get_table_data(self.table_name)
        if status == "NOK":
            print("Error Condition: Load Data for SPBC tables failed...")
            exit(1)
        return data

    def get_center_row(self) -> dict:
        """
        Returns the center row of the data.
        Returns: dictionary
        """
        return self.data[self.center_row]

    def get_starting_position(self) -> dict:
        return self.data[self.current_position]

    def get_new_row(self) -> dict:
        return self.data[self.current_position]

    def get_new_position(self) -> dict:
        """
        Moves randomly from the current position one or more rows up or down.
        Parameters: direction (random -1 or +1) to set the direction
                    steps (random int): Number of steps to move up or down.
        Returns:    dict: The new current position row.
        """
        p = Positions(self.table_name)

        attempts = 1
        steps = random.choices(self.ids, k=1)
        new_position = steps[0]
        while new_position in p.visited_positions and attempts != self.max_attempts:
            steps = random.choices(self.ids, k=1)
            new_position = steps[0]
            attempts += 1

        if len(p.visited_positions) == len(self.data) or attempts == self.max_attempts:
            print(f"1st VP array: {p.visited_positions}")
            p.visited_positions.clear()
            p.visited_positions.add(new_position)

        if attempts != self.max_attempts and len(p.visited_positions) != len(self.data):
            p.visited_positions.add(new_position)

        status = p.update_data()
        self.current_position = new_position
        return self.current_position

    def get_product_value(self, row, choice):

        value = row[choice]
        return value

    def recalculate_value(self) -> float:
        """
        Recalculates the value of the current position.
Returns:    float: The recalculated value of the current position.
        """
        current_row = self.data[self.current_position]
        return sum(value for value in current_row.values() if isinstance(value, (int, float)))

    def choose_stock_brand(self, type):
        # Stock or COMM Offer
        stocks = ["oNg", "robotics", "gold", "paper", "utility", "auto", "airline"]
        comm = ["Mutual", "Diamonds", "Grain", "Security", "Silver", "Certificates", "Money"]
        count = [100, 50, 10, 25, 200, 20]
        sc = random.choice(stocks)
        cc = random.choice(count)
        if type == "STCK":
            choice = random.choice(stocks)
        else:
            choice = random.choice(comm)
        return choice, cc

class GameBoard:
    def __init__(self, game_ID: str):
        self.table_name = "game"
        self.game_ID = game_ID
        self.data: Optional[Dict[str, Any]] = self.load_data()
        if len(self.data) == 0:
            self.player_count = 0
            self.move_count = 0
            self.gdp = 0
            self.population = 0
            self.population_chg = 0.03
            self.total_spending = 0
            self.total_earnings = 0
            self.cpi = 0
        else:
            self.player_count = self.data['player_count']
            self.move_count = self.data['move_count']
            self.gdp = self.data['gdp']
            self.population = self.data['population']
            self.population_chg = self.data['population_chg']
            self.total_spending = self.data['total_spending']
            self.total_earnings = self.data['total_earnings']
            self.cpi = self.data['cpi']

    def load_data(self) -> Optional[Dict[str, Any]]:
        # Loads data from the MySQL table into memory.
        # Returns: Game variables as a dictionary or None if no data is fetched
        status, data = db.get_game_card(self.game_ID)
        if status == "NOK":
            print("Error Condition: Load Data for Game Board failed...")
            exit(1)
        return data

    def get_game_data(self):
        return self.data

    def update_gc(self, gc):
        gc['population'] = self.population
        gc['gdp'] = self.gdp
        gc['cpi'] = self.cpi
        return gc

    def put_game_data(self, gc):
        status = "NOK"
        status = db.put_game_card(gc)
        if status == "NOK":
            print("Error Condition: Update Data for Game Board failed...")
            exit(1)
        return status

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

    def update_cpi(self):
        earn = decimal.Decimal(self.data.get('total_earnings')) + decimal.Decimal(1)
        spend = decimal.Decimal(self.data.get('total_spending')) + decimal.Decimal(1)

        if earn > spend:
            x = (decimal.Decimal(spend) / decimal.Decimal(earn)) + decimal.Decimal(1.20)
        else:
            x = decimal.Decimal((earn / spend)) + decimal.Decimal(1.20)
        x = abs(x)
        y = round(decimal.Decimal(x), 2)
        while y > 2:
            y = y / 2
        cpi = decimal.Decimal(y)
        self.data['cpi'] = cpi

    def update_gdp(self):
        """
        ○ Calculate difference between spending and earnings by subtraction.
        Then divide that value by spending to yield -> gdp
		○ Add gdp + gs_gdp + pop_chg = CPI

        """

        diff = decimal.Decimal(self.data['total_spending']) - decimal.Decimal(self.data['total_earnings'])
        value = round(decimal.Decimal(diff) / decimal.Decimal((self.data['total_spending'] + 1)), 0)
        self.data['gdp'] = abs(value)

    def update_population(self):
        """
        o Use random choice to determine population growth and change
		○ New population: Add choice amount to current population
		○ Update population change value: (current population / new population) * 100
        """
        pop = [2000,1000, 5000, 500, 200, 500, 350]
        pop_inc = random.choice(pop)
        value = int(pop_inc) + int(self.data['population'])
        chg = round(int((self.data['population'] / value)) * 100, 2)
        self.data['population'] = value
        self.data['population_chg'] = decimal.Decimal(chg)

    def get_game_level(self):
        glevel = self.data.get("game_level", None)
        return glevel

    def get_game_goal(self):
        return self.data.get('game_goal')

    def update_earnings(self, value):
        self.data['total_earnings'] += round(Decimal(value), 2)

    def get_earnings(self):
        return self.data.get("total_earnings")

    def update_spending(self, value):
        self.data['total_spending'] += round(Decimal(value), 2)

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

    def extract_numeric_value(self, value_str):
        # Find all digits (including those that might be part of a decimal number)
        match = re.search(r'[\d.]+', value_str)
        if match:
            return int(match.group())  # or float(match.group()) if you are sure it is an integer
        return None  # or handle the case where no number is found

    def calc_inheritance(self):
        inherit = []
        max = 1000000
        for pc in range(5):
            inherit.append(round(max/(pc+1), 0))
        iv = random.choice(inherit)
        iv = decimal.Decimal(iv).quantize(decimal.Decimal('0.00'), rounding=decimal.ROUND_HALF_UP)
        return iv

    def calc_salary(self):
        salaries = []
        max = 10000
        for pc in range(5):
            salaries.append(round(max/(pc+1), 0))
        sv = random.choice(salaries)
        sv = decimal.Decimal(sv).quantize(decimal.Decimal('0.00'), rounding=decimal.ROUND_HALF_UP)
        return sv

    def calc_roi(self, inv_amt, game_ID):
        # CPI = (Total Earnings / Total Spending)  + 1
        stat, result = db.get_game_card(game_ID)
        cpi1 = result['cpi']
        earn = result['total_earnings']
        spend = result['total_spending']

        if earn > spend:
            x = float((spend / earn)) + 1.2
        else:
            x = float((earn / spend)) + 1.2
        x = abs(x)
        y = round(decimal.Decimal(x), 2)
        while y > 2:
            y = y / 2
        cpi2 = y
        cpi_list = [cpi1, cpi2, 1.25, 1.50]
        cpi_value = random.choice(cpi_list)
        mkt_value = decimal.Decimal(inv_amt) * decimal.Decimal(cpi_value)
        result['cpi'] = decimal.Decimal(cpi2)
        status = db.put_game_card(result)
        return decimal.Decimal(mkt_value)

    def choose_investment(self):
        number = [0, 1, 2, 3, 4]
        type = ["LOAN", "STCK", "PPTY", "OTHR", "BUS"]
        desc = ["Mortgage", "oNg", "All", "car", "All"]
        amt = [20000, 5000, 120000, 20000, 500000]
        rnum = random.choice(number)
        return type[rnum], desc[rnum], amt[rnum]

    def assess_purchase_power(self, user, amount):
        # Determine if the amount for new investment is less than cash-on-hand (Set STAT=OK)
        # If not, decide if a loan is approved, then create investment card and update COH (Set STAT=LOAN)
        # If loan not approved, Set STAT=NO
        loan_assess = ["Y", "N", "Y", "Y", "N", "N"]
        print(f"Assess amount: {amount}")
        amount = self.extract_numeric_value(amount)
        mkt_value = decimal.Decimal(amount) / decimal.Decimal(2)
        pc = Players(user)
        cash = pc.get_data("cash_on_hand")
        pn = pc.get_data("player_number")
        result, q = db.get_player_record(user)
        if decimal.Decimal(cash) >= decimal.Decimal(amount):
            stat = "OK"
        else:
            resp = random.choice(loan_assess)
            if resp == "Y":
                stat = "LOAN"
            else:
                stat = "NO"
        if stat == "LOAN":
            iv = Investment()
            x = iv.build_row_data("invest_amount", amount)
            x = iv.build_row_data("invest_value", mkt_value)
            x = iv.build_row_data("invest_type", "LOAN")
            x = iv.build_row_data("invest_description", "Banker Investment Loan")
            cnt = decimal.Decimal(amount) / decimal.Decimal(1000)
            x = iv.build_row_data("invest_count", int(cnt))
            x = iv.build_row_data("player_number", pn)
            x = iv.create_player_investment_data()
            id = session['last_invest_id']
            idata = [{"invest_description": "Loan Payment", "invest_amount": decimal.Decimal(amount),
                      "invest_count": id}
                     ]
            x = iv.build_bill_investments(pc.data, idata)

            # Update player record
            resp = pc.update_data("cash_on_hand", amount, action="A")
            x = pc.update_table()


        return stat

    def apply_for_loan(self, user, amount):
        # Decide if a loan is approved, then create investment card and update COH (Set STAT=LOAN)
        # If loan not approved, Set STAT=NO
        loan_assess = ["Y", "N", "Y", "Y", "N", "N"]
        print(f"Assess amount: {amount}")
        mkt_value = decimal.Decimal(amount) / decimal.Decimal(2)
        pc = Players(user)
        cash = pc.get_data("cash_on_hand")
        ppty_value = pc.get_data("property_value")
        bus_value = pc.get_data("business_value")
        pn = pc.get_data("player_number")

        if Decimal(ppty_value) >= Decimal(amount) or Decimal(bus_value) >= Decimal(amount):
            stat = "OK"
        else:
            resp = random.choice(loan_assess)
            if resp == "Y":
                stat = "LOAN"
            else:
                stat = "NO"
        if stat == "LOAN" or stat == "OK":
            stat = "OK"
            iv = Investment()
            x = iv.build_row_data("invest_amount", amount)
            x = iv.build_row_data("invest_value", mkt_value)
            x = iv.build_row_data("invest_type", "LOAN")
            x = iv.build_row_data("invest_description", "Signature Loan")
            cnt = decimal.Decimal(amount) / decimal.Decimal(1000)
            x = iv.build_row_data("invest_count", int(cnt))
            x = iv.build_row_data("player_number", pn)
            x = iv.create_player_investment_data()
            id = session['last_invest_id']
            idata = [{"invest_description": "Loan Payment", "invest_amount": decimal.Decimal(amount),
                      "invest_count": id}
                     ]
            x = iv.build_bill_investments(pc.data, idata)
            # insert billpay history
            bp = Billpay()
            bill_card = iv.invest_data
            bp.build_billpay_card(pc.data, bill_card)
            # Update player record
            resp = pc.update_data("cash_on_hand", amount, action="A")
            x = pc.update_table()

        return stat


class Players:
    def __init__(self, username):
        self.table_name = "players"
        self.data = self.load_data(username)
        self.username = username
        self.player_number = self.data['player_number']
        self.cash_on_hand = self.data['cash_on_hand']
        self.salary = self.data['salary']
        self.property_value = self.data['property_value']
        self.business_value = self.data['business_value']
        self.stock_value = self.data['stock_value']
        self.commodity_value = self.data['commodity_value']
        self.other_investments = self.data['other_investments']
        self.job_level = self.data['job_level']
        self.degree_level = self.data['degree_level']
        self.ptax_assess = self.data['ptax_assess']
        self.ftax_assess = self.data['ftax_assess']
        self.ins_assess = self.data['ins_assess']
        self.city_addr = self.data['city_addr']
        self.game_ID = self.data['game_ID']

    def load_data(self, username):
        # Loads data from the MySQL table into memory.
        # Returns: Player variables as a dictionary or None if no data is fetched
        data, q = db.get_player_record(username)
        print(f"Fetched data: {data}")  # Debugging line
        return data

    def get_player_data(self):
        return self.data

    def get_data(self, key):
        """GET-like method to retrieve data."""
        return self.data.get(key, "Player table key not found")

    def update_table(self):
        stat = db.update_player2(self.data)
        return stat


    def update_data(self, key, value, action="U"):
        """PUT-like method to update existing data."""
        if key not in self.data:
            return "Player table key not found"
        if action == "U":
            self.data[key] = value
        elif action == "A":
            self.data[key] = float(self.data[key]) + float(value)
        else:
            self.data[key] = float(self.data[key]) + float(-value)
        return "OK"

    def update_table_row(self):
        q = db.update_player2(self.username)

    def recalc_salary(self):
        # salary + (salary * degree_level * 0.5) + (salary * job_level * 0.7) rounded to the nearest dollar.
        d_val = int(self.data['degree_level'] * 0.5)
        d_sal = decimal.Decimal(self.data['salary']) * decimal.Decimal(d_val)
        j_val = int(self.data['job_level'] * 0.7)
        j_sal = decimal.Decimal(self.data['salary']) * decimal.Decimal(j_val)
        sal = decimal.Decimal(self.data['salary']) + decimal.Decimal(d_sal) + decimal.Decimal(j_sal)
        self.update_data("cash_on_hand", sal, action="A")
        return sal

    def adjust_salary_amount(self, salary_control):
        sc = 0.00
        if salary_control == "ZERO":
            self.update_data("salary", sc, action="U")
        elif salary_control == "OK":
            pass
        else:
            sc = int(salary_control)
            self.update_data("salary", sc, action="A")

    def assess_property_insurance_status(self):
        billpay_data = []
        istat = self.data['ins_assess']
        if istat:
            ins = decimal.Decimal(self.data['property_value']) * decimal.Decimal(-0.01)
            ins = round(decimal.Decimal(ins), 2)
            self.update_data("cash_on_hand", ins, action="A")
            billpay_data.append({"bill_description": "Property Insurance", "bill_amount": ins})
        return billpay_data

    def assess_car_insurance_status(self):
        billpay_data = []
        if self.data['car_assess'] > 0:
            ins = decimal.Decimal(300.00) * decimal.Decimal(self.data['car_assess']) * decimal.Decimal(-1.00)
            self.update_data("cash_on_hand", ins, action="A")
            billpay_data.append({"bill_description": "Car Insurance", "bill_amount": ins})
        return billpay_data

    def assess_tax_status(self):
        billpay_data1 = []
        billpay_data2 = []
        ptax = self.data['ptax_assess']
        ftax = self.data['ftax_assess']
        if ptax:
            bus = decimal.Decimal(self.data['business_value']) * decimal.Decimal(-0.01)
            self.update_data("cash_on_hand", bus, action="A")
            billpay_data1.append({"bill_description": "Property Tax", "bill_amount": bus})
        if ftax:
            city = decimal.Decimal(self.data['cash_on_hand']) * decimal.Decimal(-0.01)
            self.update_data("cash_on_hand", city, action="A")
            billpay_data2.append({"bill_description": "Federal Tax", "bill_amount": city})
        return billpay_data1, billpay_data2

    def verify_living_status(self):
        if self.city_addr == "" or self.city_addr == " ":
            response = "unhoused"
        else:
            response = "housed"
        return response

class Game_Assets:
    def __init__(self, table_name):
        self.table_name = table_name
        self.data = self.load_data()
        self.center_row = len(self.data) // 2
        self.current_position = self.center_row
        self.ids = list(range(1, len(self.data)))
        self.max_attempts = 100  # Maximum number of attempts to find a new position

    def load_data(self) -> list:
        """
        Loads data from the MySQL table into memory.
        Returns: list of dict: The table data loaded into memory.
        Valid Tables: business, jobcenter, lifecenter, learncenter, stockcenter
        """
        status, data = db.get_table_data(self.table_name)
        if status == "NOK":
            print("Error Condition: Load Data for cycle tables failed...")
            exit(1)
        return data

    def get_starting_position(self):
        return self.current_position

    def get_current_row(self):
        return self.data[self.current_position]

    def get_new_position(self):
        """
        Moves randomly from the current position one or more rows up or down.
        Parameters: direction (random -1 or +1) to set the direction
                    steps (random int): Number of steps to move up or down.
        Returns:    dict: The new current position row.
        """
        p = Positions(self.table_name)

        attempts = 1
        steps = random.choices(self.ids, k=1)
        new_position = steps[0]
        while new_position in p.visited_positions and attempts != self.max_attempts:
            steps = random.choices(self.ids, k=1)
            new_position = steps[0]
            attempts += 1

        if len(p.visited_positions) == len(self.data) or attempts == self.max_attempts:
            print(f"1st VP array: {p.visited_positions}")
            p.visited_positions.clear()
            p.visited_positions.add(new_position)

        if attempts != self.max_attempts and len(p.visited_positions) != len(self.data):
            p.visited_positions.add(new_position)

        status = p.update_data()
        print(f"table_name : {self.table_name}")
        print(f"Visited_positions: {p.visited_positions}")
        if status != "OK":
            raise Exception("Sorry, Visited positions update failed...")
        self.current_position = new_position
        return self.current_position

    def get_row(self, id):
        arr = dict(self.data[id])
        return arr

    def adjust_object_scope(self, key, value):
        data2 = []
        for data in self.data:
            if data[key] == value:
                data2.append(data)
        return data2

class PageLayout:
    def __init__(self):
        self.data = []
        self.data_row = {"product": " ", "type": " ", "description": " ", "id": 0,
                         "fees": 0.00, "price": 0.00, "sale_type": " "}

    def load_address_data(self, data_in):
        i = 0
        page_layout = []
        if len(data_in) > 0:
            page_layout = []
            for d in data_in:
                data_row = {
                    "product": d['District'],
                    "type": d['BLDG_type'],
                    "description": d['Property'],
                    "id": d['id'],
                    "fees": round(decimal.Decimal(d['Price']) * decimal.Decimal(0.06), 2),
                    "price": round(decimal.Decimal(d['Price']) * decimal.Decimal(1.06), 2),
                    "sale_type": d['PPTY_type']
                }
                page_layout.append(data_row)
                self.data = page_layout.copy()
        return page_layout

    def get_data(self, key):
        """GET-like method to retrieve data."""
        return self.data.get(key, "Page Layout key not found")

    def add_data(self, key, value):
        """POST-like method to add new data."""
        if key in self.data:
            return "Key already exists"
        self.data[key] = value
        return "Data added successfully"

    def update_data(self, key, value):
        """PUT-like method to update existing data."""
        if key not in self.data:
            return "Key not found"
        self.data[key] = value
        return "Data updated successfully"

    def delete_data(self, key):
        """DELETE-like method to remove data."""
        if key not in self.data:
            return "Key not found"
        del self.data[key]
        return "Data deleted successfully"

class Game_Action:
    """
    • Game Action object - one per player
        • Move type (SP, TP, IN, or RP)
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
        self.visited_positions = set()

    def initialize_move_attributes(self):
        self.move_type = "SP"
        self.move_gain = 0
        self.move_loss = 0

    def initialize_travel(self):
        self.travel = "N"

    def initialize_economy(self):
        self.position_ID = random.randint(1, 50)

    def initialize_index(self):
        self.index_ID = 25

    def get_action_items(self):
        ga = {
            'move_type' : self.move_type,
            'move_gain' : self.move_gain,
            'move_loss' : self.move_loss,
            'travel' : self.travel,
            'position_ID' : self.position_ID,
            'index_ID' : self.index_ID
        }
        return ga

       # Setter methods for individual attributes
    def set_move_type(self, move_type):
        self.move_type = move_type

    def set_move_gain(self, move_gain):
        self.move_gain = move_gain

    def set_move_loss(self, move_loss):
        self.move_loss = move_loss

    def set_travel(self, travel):
        self.travel = travel

    def set_position_ID(self, position_ID):
        self.position_ID = position_ID

    def set_index_ID(self, index_ID):
        self.index_ID = index_ID

    def reset_position_ID(self):
        self.position_ID = random.randint(1, 50)
        return self.position_ID

    def reset_index_ID(self, index_ID):
        ndx = [1, 2, -10, 10, -1]
        nbr = random.choice(ndx)
        self.index_ID = nbr + index_ID
        while self.index_ID < 0:
            self.index_ID = self.index_ID + 3
        while self.index_ID > 50:
            self.index_ID = self.index_ID - 3
        return self.index_ID

    def get_current_position(self):
        return self.position_ID

    def get_new_position(self):
        """
        Moves randomly from the current position one or more rows up or down.
        Parameters: direction (random -1 or +1) to set the direction
                    steps (random int): Number of steps to move up or down.
        Returns:    dict: The new current position.
        """
        direction = random.choice([-1, 1])
        mylist = [0, 1, 2, 3, 3, 5, 2, 7]
        steps = random.choices(mylist, weights=[5, 5, 2, 1, 1, 4, 1, 1], k=1)
        # steps = random.randint(0, 7)
        x = self.position_ID + direction * steps[0]
        new_position = max(0, min(x, 50 - 1))
        self.position_ID = new_position
        return self.position_ID

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

class Investment:
    def __init__(self):
        self.table_name = "investments"
        self.invest_data = {
            'invest_type': " ",
            'invest_count': 0,
            'invest_amount': decimal.Decimal('0.00'),
            'invest_description': " ",
            'player_number': 0,
            'invest_value': decimal.Decimal('0.00')
        }

    def build_row_data(self, key, value):
        """Accept a key and value pair to update investment card object"""
        if key not in self.invest_data:
            return "Key not found"
        self.invest_data[key] = value
        return "OK"

    def parse_row_data(self, data, player_number):
        """Based on a cycle card, build investment card data and insert"""
        self.invest_data['player_number'] = player_number
        amt = 1.25
        if data['code'] == "LC2":
            self.invest_data['invest_type'] = "OTHR"
            self.invest_data['invest_count'] = data['investment_check']
            self.invest_data['invest_amount'] = abs(data['COH'])
        elif data['code'] == "SC":
            self.invest_data['invest_type'] = data['investment_type']
            self.invest_data['invest_amount'] = abs(decimal.Decimal(data['amount']))
            self.invest_data['invest_count'] = data['count']
        elif data['code'] == "SC2":
            self.invest_data['invest_type'] = "OTHR"
            self.invest_data['invest_amount'] = abs(decimal.Decimal(data['amount']))
            self.invest_data['invest_count'] = int(1)
            self.invest_data['invest_description'] = data['long_description']
        elif data['code'] == "VAC":
            self.invest_data['invest_type'] = "OTHR"
            self.invest_data['invest_amount'] = round(decimal.Decimal(data['pkg_price']), 2)
            self.invest_data['invest_count'] = int(4)
            self.invest_data['own_code'] = "TRIP"
            amt = 1.00
        elif data['code'] == "SHP":
            self.invest_data['invest_type'] = "OTHR"
            self.invest_data['invest_amount'] = round(decimal.Decimal(data['sales_price']), 2)
            self.invest_data['invest_count'] = data['count']
            self.invest_data['invest_description'] = data['long_description']
            self.invest_data['own_code'] = "SHOP"
            amt = 1.00
        elif data['code'] == "BUS":
            self.invest_data['invest_type'] = "BUS"
            self.invest_data['invest_amount'] = round(decimal.Decimal(data['cost']), 2)
            self.invest_data['invest_count'] = int(1)
            self.invest_data['own_code'] = "TRIP:" + data['purpose']
            amt = 1.00
        elif data['code'] == "TRVL":
            self.invest_data['invest_type'] = "TRVL"
            self.invest_data['invest_amount'] = round(decimal.Decimal(data['cost']), 2)
            self.invest_data['invest_count'] = int(1)
            self.invest_data['own_code'] = "TRIP:" + data['purpose']
            amt = 1.00

        elif data['code'] == "LC":
            self.invest_data['invest_type'] = data['investment']
            self.invest_data['invest_amount'] = abs(decimal.Decimal(data['amount']))
            if data['investment'] == "LOAN":
                self.invest_data['invest_count'] = int(500)
            else:
                self.invest_data['invest_count'] = int(1)
        elif data['code'] == "BC":
            self.invest_data['invest_type'] = data['product']
            self.invest_data['invest_amount'] = abs(decimal.Decimal(data['amount']))
            self.invest_data['invest_count'] = data['invest_count']
        else:
            self.invest_data['invest_amount'] = abs(decimal.Decimal(data['amount']))
        if data['code'] != "SC2" and data['code'] != "SHP":
            self.invest_data['invest_description'] = data['short_description']
        self.invest_data['invest_value'] = round(decimal.Decimal(self.invest_data['invest_amount']) * decimal.Decimal(amt), 2)
        stat = db.insert_investments_from_sale(self.invest_data)
        return stat

    def create_player_investment_data(self):
        stat = db.insert_investments_from_sale(self.invest_data)
        return stat

    def get_player_investment_data(self, player_number):
        """
        Loads data from the MySQL investment table into memory.
        Returns: Dictionary list
        """
        status, data = db.get_player_investment_history(player_number)
        if status == "NOK":
            raise Exception("Error Condition: Load Data for investments table failed...")
        return data

    def double_stock_investment(self, type, player_number):
        """ Collect investment cards by player and type, double the count and value,
        and then update the rows
        """
        status, invest_cards = db.get_investments_by_code(type, player_number)
        if status == "OK":
            if len(invest_cards) > 0:
                for investment in invest_cards:
                    investment['invest_count'] = int(investment['invest_count']) * 2
                    investment['invest_value'] = float(investment['invest_value']) * float(2.00)
                    stat = db.update_investment_by_id(investment)
            else:
                status = "NOI"
        else:
            status = "NOK"
        return status

    def verify_loan(self, player):
        """ Verify player loan status
        """
        loan_status = True
        pay_loan = self.get_player_investments_by_desc(player['player_number'], "BILL", "Loan Payment")
        if len(pay_loan) > 0:

            for row in pay_loan:
                idata = [{"bill_description": "Loan Payment", "bill_amount": row['invest_amount']}]
                bp = Billpay()
                x = bp.build_billpay_card(player, idata)
                row['invest_value'] = decimal.Decimal(row['invest_value']) - decimal.Decimal(1000.00)
                player['cash_on_hand'] = decimal.Decimal(player['cash_on_hand']) - decimal.Decimal(1000.00)
                # Update LOAN bill investment card
                stat = self.update_bill_investment(row)
                loan_status = True
        else:
            loan_status = False
        return loan_status

    def verify_rent(self, player):
        """ Verify player rent status
        """
        pay_rent = self.get_player_investments_by_type(player['player_number'], "RENT")
        if len(pay_rent) > 0:
            rent_status = True
            for row in pay_rent:
                idata = [{"invest_description": "Rent Payment", "bill_amount": row['invest_amount']}]
                player['cash_on_hand'] = decimal.Decimal(player['cash_on_hand']) - decimal.Decimal(row['invest_amount'])
                bp = Billpay()
                x = bp.build_billpay_card(player, idata)
        else:
            rent_status = False
        return rent_status

    
    def verify_living_status(self, player_number):
        code = "PPTY"
        response = "unhoused"
        status, invest_cards1 = db.get_investments_by_code(code, player_number)
        if status == "OK":
            if len(invest_cards1) > 0:
                response = "Home Owner"
        code = "RENT"
        status, invest_cards2 = db.get_investments_by_code(code, player_number)
        if status == "OK":
            if len(invest_cards2) > 0:
                response = "Renter"
        return response

    def pay_other_bills(self, player):
        idata = [{"bill_description": "Utilities", "bill_amount": decimal.Decimal(500.00)}]
        player['cash_on_hand'] = decimal.Decimal(player['cash_on_hand']) - decimal.Decimal(500.00)
        bp = Billpay()
        stat = bp.build_billpay_card(player, idata)
        return stat

    def get_player_investments_by_type(self, player_number, type):
        status, data = db.get_player_investment_history(player_number)
        data1 = []
        if status == "NOK":
            raise Exception("Error Condition: Load Data Investments by type for table failed...")
        for d in data:
            if type == d['invest_type']:
                if d['invest_type'] == "STCK":
                    d['invest_description'] = d['invest_description'] + " - "+ str(d['invest_count'])
                data1.append(d)

        return data1

    def extract_trip_investments(self, data):
        data1 = []
        for d in data:
            if "TRIP" not in d['own_code']:
                data1.append(d)
        return data1

    def get_stock_investments(self, player_number):
        stocks = {"oNg": 0, "robotics": 0, "gold": 0, "paper": 0, "utility": 0, "auto": 0, "airline": 0}
        data = self.get_player_investments_by_type(player_number, "STCK")
        stock_count = int(0)
        # Load stocks array
        for stock in data:
            stocks[stock['invest_description']] = Decimal(stocks[stock['invest_description']]) + Decimal(stock['invest_count'])
        # Accumulate count of stocks (max 100 per company)
        for key, value in stocks.items():
            if value >= 100:
                stock_count += int(100)
            if value < 100:
                stock_count += int(value)
        return stocks, stock_count

    def get_player_investments_by_desc(self, player_number, type, desc):
        status, data = db.get_player_investment_history(player_number)
        data1 = []
        if status == "NOK":
            raise Exception("Error Condition: Load Data Investments by type for table failed...")
        for d in data:
            if type == d['invest_type'] and desc == d['invest_description']:
                data1.append(d)
        return data1

    def get_player_investments_by_code(self, player_number, value):
        status, data = db.get_player_investment_history(player_number)
        data1 = []
        if status == "NOK":
            raise Exception("Error Condition: Load Data Investments by type for table failed...")
        for d in data:
            if value in d['own_code']:
                data1.append(d)
        return data1

    def update_trip_investments(self, data):
        new_data = []
        trip = {}
        classes = ["First class", "Premium", "Economy"]
        types = {"TRVL": "Local Trip", "BUS": "Business Trip", "OTHR": "Vacation"}
        for row in data:
            if row['invest_type'] != "OTHR":
                purpose = row['own_code'].split(":")
            else:
                purpose = ["TRIP", "Rest and Relaxation"]
            trip = {
                "id": row['invest_id'],
                "type": types[row['invest_type']],
                "count": row['invest_count'],
                "description": row['invest_description'],
                "purpose": purpose[1],
                "flight_class": random.choice(classes),
                "points": int(row['invest_value'])
            }
            new_data.append(trip)
            trip = {}
        return new_data

    def get_bill_investment_by_loanid(self, player_number, type, loanid):
        status, data = db.get_player_investment_history(player_number)
        data1 = []
        if status == "NOK":
            raise Exception("Error Condition: Load Data Investments by type for table failed...")
        for d in data:
            if type == d['invest_type'] and loanid == d['invest_count']:
                data1.append(d)
        return data1

    def get_investment_by_id(self, id):
        status, data = db.get_investment_by_id(id)
        if status == "OK":
            return data
        else:
            return {}

    def update_investment_by_id(self, data):
        id = data['id']
        status = db.update_investment_by_id(data)
        if status  == "OK":
            return "OK"
        else:
            return "NOK"

    def remove_player_investments_by_type(self, player_number, type, delete="Y"):
        status = "NOK"
        if delete == "Y":
            status = db.delete_investments_by_code(type, player_number)
            if status == "NOK":
                raise Exception("DB Error Condition: Load Data Investments by type for table failed...")
        status = "OK"

        return status

    def remove_player_investments_by_desc(self, player_number, type, desc, delete="Y"):
        status = "NOK"
        if delete == "Y":
            status = db.delete_investments_by_desc(type, desc, player_number)
            if status == "NOK":
                raise Exception("DB Error Condition: Remove Investments by desc for table failed...")
        status = "OK"

        return status

    def remove_player_investments_by_id(self, id, delete="Y"):
        status = "NOK"
        if delete == "Y":
            status = db.delete_investment_by_id(id)
            if status == "NOK":
                raise Exception("DB Error Condition: Remove Investment by ID for table failed...")
        status = "OK"

        return status

    def build_bill_investments(self, player, idata):
        """
        TYPES OF BILLS
            Loan Payment investment card if loan investment cards exist

        """
        status = "NOK"
        print(f"IDATA: {idata}")
        data = idata.copy()
        flags = {"pi": "N", "ci": "N", "pt": "N", "ft": "N",
                 "ut": "N", "rp": "N", "lp": "N"
                 }
        bill_type = {"pi": "Property Insurance", "ci": "Car Insurance", "pt": "Property Tax", "ft": "Federal Tax",
                     "ut": "Utilities", "rp": "Rent Payment", "lp": "Loan Payment"
                     }
        if len(data) > 0:
            for d in data:
                if d['invest_description'] == bill_type['pi']:
                    flags['pi'] = "Y"
                if d['invest_description'] == bill_type['ci']:
                    flags['ci'] = "Y"
                if d['invest_description'] == bill_type['pt']:
                    flags['pt'] = "Y"
                if d['invest_description'] == bill_type['ft']:
                    flags['ft'] = "Y"
                if d['invest_description'] == bill_type['ut']:
                    flags['ut'] = "Y"
                if d['invest_description'] == bill_type['rp']:
                    flags['rp'] = "Y"
                if d['invest_description'] == bill_type['lp']:
                    flags['lp'] = "Y"
        # Preset common investment data
        self.invest_data['invest_type'] = "BILL"
        self.invest_data['player_number'] = player['player_number']
        n = 0
        datax = []

        for k, v in flags.items():
            amt = 0.00

            if v == "Y":

                if k == "pi":
                    amt = round(decimal.Decimal(player['property_value']) * decimal.Decimal(0.001), 2)
                if k == "ci":
                    amt = round(decimal.Decimal(player['car_assess']) * decimal.Decimal(300.00), 2)
                if k == "pt":
                    amt = round(decimal.Decimal(player['property_value']) * decimal.Decimal(0.01), 2)
                if k == "ft":
                    amt = round(decimal.Decimal(player['cash_on_hand']) * decimal.Decimal(0.01), 2)
                if k == "ut":
                    amt = decimal.Decimal(500.00)
                if k == "rp":
                    amt = round(decimal.Decimal(player['cash_on_hand']) * decimal.Decimal(0.0001), 2)
                if k == "lp":
                    amt = decimal.Decimal(1000.00)
                    self.invest_data['invest_amount'] = round(decimal.Decimal(amt), 2)
                    for d in data:
                        self.invest_data['invest_count'] = d['invest_count']
                        self.invest_data['invest_value'] = d['invest_amount']
                else:
                    self.invest_data['invest_amount'] = round(decimal.Decimal(amt), 2)
                self.build_row_data('invest_description', bill_type[k])
                #print(f"self invest data: {self.invest_data}")
                # data.append(self.invest_data)
                datax.append(copy.deepcopy(self.invest_data))
                n += 1
        #print(f"DATA Array: {data}")
        if len(datax) != 0:
            i = 0
            for i in range(len(datax)):
                status = "OK"
                #print(f"data by row: {data[i]}")
                status = db.insert_investments_from_sale(datax[i])
                if status == "NOK":
                    raise Exception("DB Error Condition2: ISRT Data Investments by type for table failed...")

        status = "OK"
        return status

    def update_bill_investment(self, card):
        stat = "NOK"
        stat = db.update_investment_by_id(card)
        return stat

    def pay_tax_bills(self, player):
        bills = self.get_player_investments_by_type(player['player_number'], "BILL")
        payments = []
        stat = "NOK"
        for b in bills:
            if "Tax" in b['invest_description']:
                if decimal.Decimal(player['cash_on_hand']) < decimal.Decimal(b['invest_amount']):
                    bnkr = banker()
                    amt = decimal.Decimal(b['invest_amount']) * decimal.Decimal(3)
                    stat = bnkr.assess_purchase_power(player['username'], b['invest_amount'])
                if stat == "LOAN":
                    player['cash_on_hand'] -= decimal.Decimal(b['invest_amount'])
                    stat = db.insert_billpay_history(b)
        return stat

    def build_loan_data(self, data_in):

        page_layout = []
        if len(data_in) > 0:
            page_layout = []
            for d in data_in:
                data_row = {
                    "type": "Loan Payments",
                    "pay_count": 1,
                    "id": d['invest_id'],
                    "payment": decimal.Decimal(d['invest_amount']),
                    "description": d['invest_description'],
                    "player_number": d['player_number'],
                    "amount": decimal.Decimal(d['invest_value'])
                }
                page_layout.append(data_row)
                self.data = page_layout.copy()
        return page_layout

class Sellcycle:
    def __init__(self, player_number: int):
        self.table_name = "sellcycle"
        self.player_number = player_number
        self.data = self.load_data()
        print(f"Loaded sellcycle data: {self.data}")

    def load_data(self):
        """
        Loads a row of data from the MySQL table into memory.
        Returns: dict: The table data loaded into memory.

        """
        status, result = db.get_player_investment_history(self.player_number)

        if status == "NOK":
            raise Exception("Error Condition: Load investment table failed...")
        filtered_data = [row for row in result if row["invest_type"] != "RENT" or row["invest_type"] != "INS"]

        return filtered_data

    def get_row_count(self):
        if len(self.data) > 0:
            response = len(self.data)
        else:
            response = 0
        return response

    def get_row(self, row):
        """GET-like method to retrieve data."""
        rcount = len(self.data)
        if row <= rcount:
            return self.data[row-1]
        else:
            return {}

    def delete_row(self, iv_sold):
        """GET-like method to retrieve data."""
        stat = "NOK"
        id = iv_sold['invest_id']
        status = db.delete_investment_by_id(id)
        stat = "OK"
        return stat

    def select_row(self):
        """GET-like method to retrieve data."""
        rcount = len(self.data)
        if rcount > 0:
            num_list = list(range(0, rcount))
            print(f"num_list: {num_list}")
            if rcount > 0:
                rnum = random.choice(num_list)
                print(f"rnum: {rnum}")

        if rcount == 0:
            return "No data", rcount
        else:
            return self.data[rnum], rcount

    def build_investment_for_sellcycle(self, desc):
        """GET-like method to retrieve data."""

        iv_data, rnum = self.select_row()
        iv_data['code'] = "SC3"


        if rnum == 0:
            iv_data['rnum'] = 1
            iv_data['invest_description'] = "No items for sale"
            iv_data['invest_value'] = 0
            iv_data['invest_count'] = 0
        else:
            iv_data['rnum'] = rnum
        desc.append("This is one of two Sell Cycle opportunities. It is an opportunity to interest the banker into "
                    "buying your possessions. The banker is always looking for a deal.")
        desc.append(iv_data['invest_description']) # Product info
        desc.append("$  " + str(iv_data['invest_value']))
        desc.append("  " + str(iv_data['invest_count']))
        return desc, iv_data

class ROI_Pay:
    def __init__(self):
        self.table_name = "investment_return"
        self.roi_data = self.load_data()
        self.select_roi_data = []

    def load_data(self) -> list:
        """
        Loads data from the MySQL table into memory.
        """
        status, data = db.get_table_data(self.table_name)
        if len(data) == 0:
            status = "OK"
            return data
        if status == "NOK":
            print(f"Error Condition: Load Data for ROI {self.table_name} table failed...")
            exit(1)
        return data

    def select_ROI_by_player(self, pn):
        data = [row for row in self.roi_data if row['player_number'] == pn]
        self.select_roi_data = data.copy()
        return data

    def update_game_tables(self, user):
        p = Players(user)
        game_ID = p.game_ID
        print(f"ROI UGT roi_data: {self.select_roi_data}")
        occupancy = [1.0, 0.8, 0.9, 0.5, 0.7, 0.6]
        gb = GameBoard(game_ID)
        game_data = gb.get_game_data()
        for row in self.select_roi_data:
            # Implement the logic to update the game table based on the selected row
            max_rent = Decimal(row['max_qtrly_roi'])
            occ_value = Decimal(random.choice(occupancy))
            rent = round(max_rent * occ_value, 2)
            game_data['total_earning'] = Decimal(game_data['total_earning']) + Decimal(rent)
            x = p.update_data("cash_on_hand", rent, action="A")
            x = p.update_data("other_investments", rent, action="A")
        update_status1 = gb.put_game_data(game_data)
        update_status2 = p.update_table()
        if update_status1 != "OK":
            print(f"Failed to update game table in update_game_table.")
        if update_status2 != "OK":
            print(f"Failed to update player table update_player_table.")
        return update_status1, update_status2

