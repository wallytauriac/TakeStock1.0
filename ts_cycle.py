import decimal
from datetime import date, timedelta, datetime
from decimal import Decimal
from mysql.connector import Error
from typing import Dict, Any, Optional, Tuple, Set
from flask import Flask
from flask_mysqldb import MySQL
from ts_database import DB_Mgr
import copy
import random
from app_factory import create_app, mysql
db = DB_Mgr(mysql)

"""
app = Flask(__name__)
# This code is needed to test this module without the main module
# Configure MySQL
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Evenodd!512'
app.config['MYSQL_DB'] = 'Takestock1.0'
app.config['MYSQL_HOST'] = 'localhost'

mysql = MySQL(app)
"""

class Cycle:
    def __init__(self, table_name: str, id: int):
        self.table_name = table_name
        self.id = id
        self.data = self.load_data()
        print(f"Loaded data: {self.data}")
        self.code = self.data['code']
        self.type = self.data['type']
        self.short_description = self.data['short_description']
        self.long_description = self.data['long_description']
        self.amount = self.data['amount']
        self.count = self.data['count']
        self.center_row = len(self.data) // 2
        self.current_position = self.center_row

    def load_data(self) -> Dict[str, Any]:
        """
        Loads a row of data from the MySQL table into memory.
        Returns: dict: The table data loaded into memory.

        with app.app_context():
            db = DB_Mgr(mysql)
        """
        status, result, column_names = db.get_table_row(self.table_name, self.id)
        if status == "NOK":
            raise Exception("Error Condition: Load Data from cycle tables failed...")
        if result:
            row = result[0]
            data = dict(zip(column_names, row))
            print(f"{self.table_name} Table data: ", data)
            return data
        else:
            return {}

    def get_data(self, key):
        """GET-like method to retrieve data."""
        return self.data.get(key, "Job cycle key not found")

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



# Step 2: Define the Subclasses
class JobCycle(Cycle):
    def jc_method(self, key):
        pass

class LifeCycle(Cycle):
    def lc_method(self, key):
        pass

class CollegeCycle(Cycle):
    def cc_method(self, key):
        pass

class StockCycle(Cycle):
    def sc_method(self, key):
        pass

class ShoppingCycle(Cycle):
    def sc_method(self, key):
        pass

class SellCycle(Cycle):
    def sc2_method(self, key):
        pass

class BankerCycle(Cycle):
    def calculate_interest(self, rate: float) -> Decimal:
        """  Calculate interest based on the amount and a given interest rate.   """
        interest = round(Decimal(self.amount) * Decimal(rate / 100), 2)
        return interest

    def check_eligibility(self, min_amount: Decimal) -> bool:
        """  Check if the current amount meets the minimum eligibility criteria.
        """
        return self.amount >= min_amount

    def update_amount(self, transaction_amount: Decimal) -> None:
        """  Update the amount based on a transaction.
        """
        self.amount += transaction_amount
        print(f"Updated amount: {self.amount}")

class CycleExt:
    def __init__(self):
        self.cycle = None

    def get_cycle_table_name(self, key: str):
        cycle_tbl = {
            "Life Cycle": "lifecenter",
            "Stock Cycle": "stockcenter",
            "Shopping Cycle": "shopping",
            "Job Cycle": "jobcenter",
            "College Cycle": "learncenter",
            "Sell Cycle": "sellcycle",
            "Banker Cycle": "bankercycle"
        }
        return cycle_tbl[key]

    def get_cycle_table_by_code(self, key: str):
        cycle_tbl = {
            "LC2": "lifecenter",
            "SC": "stockcenter",
            "SC2": "shopping",
            "JC": "jobcenter",
            "LC": "learncenter",
            "SC3": "sellcycle",
            "BC": "bankercycle"
        }
        return cycle_tbl[key]

    def get_cycle_tax_code(self, key: str):
        cycle_tbl = {
            "PTAX ON": 1,
            "PTAX OFF": 0,
            "FTAX ON": 1,
            "FTAX OFF": 0
        }
        cycle_tbl2 = {
            "PTAX ON": "ptax_assess",
            "PTAX OFF": "ptax_assess",
            "FTAX ON": "ftax_assess",
            "FTAX OFF": "ftax_assess"
        }
        return cycle_tbl2[key], cycle_tbl[key]

    def get_cycle_message(self, key):
        cycle_msg = {
            "Life Cycle": "Life Cycle - Is a chance to experience life challenges. "
                          "The experiences will end in money gains or losses.",
            "Stock Cycle": "Stock Cycle - Think of this opportunity as a conference"
                           " you attend and get a chance to gain or lose in the stock market.",
            "Shopping Cycle": "Shopping Cycle - There is nothing like a good shopping experience"
                              " at your favorite stores.",
            "Job Cycle": "Job Cycle - You may not feel like you are on the job. "
                         "But the results can be interesting.",
            "College Cycle": "College Cycle - Here is a chance to further education. "
                             "Well it is a good experience.",
            "Sell Cycle": "Sell Cycle - You been wondering when you might be abe to sell some of your stuff.",
            "Banker Cycle": "Banker Cycle - Now, you have a chance to visit with your neighborhood banker. "
                            "Get your needs met."
        }
        return cycle_msg[key]

    def get_info_message(self, action, cycle, itype):
        msg = None
        if cycle == "SC" and action == "remove":
            msg = "This event culminates in the loss of any " + itype + " investments you owned. A loss can happen."
        if cycle == "SC" and action == "double":
            msg = "What an exciting event! Your " + itype + " investment count just doubled. Good times!"
        if cycle == "SC" and action == "insert":
            msg = "Good investment! Your " + itype + " investment is a great addition. Keep on investing!"
        if cycle == "LC2" and action == "flag":
            msg = "Tax assessment change! Your tax status has been modified."
            stat_flag = {
                "PTAX ON": "Property taxes will be assessed every 10th round.",
                "PTAX OFF": "Property tax assessment has been turned off for you.",
                "FTAX ON": "City taxes will be assessed every 10th round.",
                "FTAX OFF": "City tax assessment has been turned off for you."
            }
            msg2 = stat_flag[itype]
            msg = msg +  " " + msg2
        if cycle == "SC2" and action == "insert":
            msg = ("Useful investment! Your shopping investment choice is a great addition. "
                   "You can always sell it if you dont need it.")
        if cycle == "JC":
            msg1 = " "
            msg2 = " "
            if int(action) > 0 and itype != "ZERO":
                msg1 = "Congratulations on your raise! "
            if itype == "ZERO":
                msg2 = "Sorry about the loss. "
            msg = "Jobs are beneficial. "
            msg = msg1 + msg2
        if cycle == "LC" and itype == 1:
            msg = "Congratulations! Your degree will be reflected in your salary pay. "
        if cycle == "BC" and itype == "OFF":
            msg = "Insurance payment assessment change! Your insurance pay status has been turned off."


        return msg

class Opportunity:
    def __init__(self, data):
        self.data = data

    def stock_check_removal(self, player_number):
        stat = "none"
        if self.data['short_description'] == "Stock Sell":
            x = db.delete_investments_by_code("STCK", player_number)
            if x == "OK":
                stat = "done"
        return stat

    def set_buy_type(self, data, shrt_desc):

        if "buy_type" in data:
            if shrt_desc == "Stock Sell":
                data['buy_type'] = "bs"
        return data

    def cash_out(self, player_number):
        stat = "none"
        if self.data['short_description'] == "Cash OUT":
            x = db.delete_investments_by_code("STCK", player_number)
            y = db.delete_investments_by_code("PPTY", player_number)
            if x == "OK" and y == "OK":
                stat = "done"
        return stat

    def set_player_flags(self, player_number):
        stat = "none"
        result = db.get_player_by_number(player_number)
        if self.data['short_description'] == "Property_Insurance":
            result['ins_assess'] = 0
            resp = db.update_player_by_flag(result)
            stat = "done"
        elif self.data['short_description'] == "Promotion":
            result['job_level'] = int(result['job_level']) + int(1)
            resp = db.update_player_by_flag(result)
            stat = "done"
        elif self.data['short_description'] == "Property Sell":
            y = db.delete_investments_by_code("PPTY", player_number)
            stat = "done"

        return stat

    def process_raise_event(self, amt, player_number):
        stat = "none"
        result = db.get_player_by_number(player_number)
        if self.data['short_description'] == "Salary increase":
            result['salary'] = decimal.Decimal(result['salary']) + decimal.Decimal(amt)
            resp = db.update_player_by_flag(result)
            stat = "done"

        return stat

class Options:
    def __init__(self, ctgy=None, type=None, desc=None, invest=None, options=None):

        self.ctgy = ctgy
        self.type = type
        self.desc = desc
        self.invest = invest
        if options is None:
            self.option = []
        else:
            self.option = options
        self.load = self.load_data()
        self.options = self.option + self.load

    def load_data(self):
        d = {}

        options = []
        rnge = len(self.ctgy)
        for i in range(rnge):
            if self.type is not None:
                d['opt_type'] = self.type[i]
            if self.ctgy is not None:
                d['opt_ctgy'] = self.ctgy[i]
            if self.desc is not None:
                d['opt_desc'] = self.desc[i]
            if self.invest is not None:
                d['opt_invest'] = self.invest[i]
            options.append(d)
            d = {}
            self.load = options

        return self.load

    def add_row(self, ctgy=None, type=None, desc=None, invest=None):
        d = {}
        options = self.options
        self.ctgy = ctgy
        self.type = type
        self.desc = desc
        self.invest = invest
        #rnge = len(self.ctgy)
        for i in range(1):
            if self.type is not None:
                d['opt_type'] = self.type[i]
            if self.ctgy is not None:
                d['opt_ctgy'] = self.ctgy[i]
            if self.desc is not None:
                d['opt_desc'] = self.desc[i]
            if self.invest is not None:
                d['opt_invest'] = self.invest[i]
            self.options.append(d)
        d = {}

    def get_options(self):
        return self.options

class Positions:
    def __init__(self, table_name):
        self.table_name = table_name
        self.visited_positions = self.load_data(table_name)

    def load_data(self, table_name):
        v_pos = set()
        q, result = db.get_positions_data(table_name)
        if q > 0:
            for r in result:
                if table_name == "positions":
                    v_pos.add(r['value'])
                else:
                    v_pos.add(r['id'])
        else:
            pass

        return v_pos

    def add_position(self, new_pos):
        self.visited_positions.add(new_pos)
        status = "OK"
        return status

    def retrieve_count(self):
        return len(self.visited_positions)

    def update_data(self):
        status = "NOK"
        status = db.clear_positions_data(self.table_name)
        if status == "OK":
            try:
                status = db.update_positions_data(self.table_name, self.visited_positions)
            except Exception as e:
                raise Exception(f"Update positions data failed... {e}")
        else:
            raise Exception(f"Clear Positions data error: Update - {self.table_name}")
        status = "OK"
        return status

class Billpay:
    def __init__(self):
        self.table_name = "billpay"
        self.billpay_data = {
            'bill_type': " ",
            'bill_round': 0,
            'bill_amount': decimal.Decimal('0.00'),
            'bill_description': " ",
            'player_number': 0,
            'bill_value': decimal.Decimal('0.00'),
            'invest_id': 0
        }

    def set_bill_type(self, bill_desc):

        types = {
            "Property Insurance": "PRPI",
            "Car Insurance": "CARI",
            "Property Tax": "PRPT",
            "Federal Tax": "FEDT",
            "Utilities": "UTIL",
            "Rent Payment": "RENT",
            "Loan Payment": "LOAN"
        }
        self.billpay_data['bill_type'] = types[bill_desc]
        self.billpay_data['bill_description'] = bill_desc
        return types[bill_desc]

    def get_data_by_key(self, key):
        """GET-like method to retrieve data."""
        return self.billpay_data.get(key, "Bill pay key not found")

    def add_data_by_key(self, key, value):
        """POST-like method to add new data."""
        status = "NOK"
        if key in self.billpay_data:
            self.billpay_data[key] = value
            status = "OK"
        else:
            status = "NOK"
        return status

    def insert_billpay_card(self):
        stat = "NOK"
        stat = db.insert_billpay(self.billpay_data)
        self.clear_billpay_card()
        return stat

    def clear_billpay_card(self):
        self.billpay_data = {
            'bill_type': " ",
            'bill_round': 0,
            'bill_amount': decimal.Decimal('0.00'),
            'bill_description': " ",
            'player_number': 0,
            'bill_value': decimal.Decimal('0.00'),
            'invest_id': 0
        }

    def build_billpay_card(self, player, data):
        """
        TYPES OF BILLS
            The DATA value is a list with dictionary rows - expect one row
            Keys: bill_description, bill_amount
            See details in flags and bill_type arrays
        """
        status = "NOK"
        flags = {"pi": "N", "ci": "N", "pt": "N", "ft": "N",
                 "ut": "N", "rp": "N", "lp": "N"
                 }
        bill_type = {"pi": "Property Insurance", "ci": "Car Insurance", "pt": "Property Tax", "ft": "Federal Tax",
                     "ut": "Utilities", "rp": "Rent Payment", "lp": "Loan Payment"
                     }
        if len(data) > 0:
            print("Billpay data: ", data)
            if isinstance(data, dict):
                data1 = []
                data1.append(data)
            else:
                data1 = []
            print("Billpay data1: ", data1)
            for d in data1:
                # Preset common investment data
                x = self.set_bill_type(d['invest_description'])
                self.billpay_data['player_number'] = player['player_number']
                self.billpay_data['bill_amount'] = abs(d['invest_amount'])

                status = db.insert_billpay(self.billpay_data)
                if status == "NOK":
                    raise Exception("DB Error Condition: ISRT Bill Pay failed...")
                else:
                    self.clear_billpay_card()

        status = "OK"
        return status

class ROI_Card:
    def __init__(self):
        self.table_name = "Investment_return"
        self.roi_data = {
            'roi_type': " ",
            'roi_units': 0,
            'roi_rent': decimal.Decimal(0.00),
            'roi_BLDG_type': " ",
            'roi_PPTY_type': " ",
            'roi_Property': " ",
            'player_number': 0,
            'roi_price': decimal.Decimal(0.00),
            'max_qtrly_roi': decimal.Decimal(0.00),
            'ppty_id': 0
        }
    def get_data_by_key(self, key):
        """GET-like method to retrieve data."""
        return self.roi_data.get(key, "Bill pay key not found")

    def add_data_by_key(self, key, value):
        """POST-like method to add new data."""
        status = "NOK"
        if key in self.roi_data:
            self.roi_data[key] = value
            status = "OK"
        else:
            status = "NOK"
        return status

    def insert_roi_card(self):
        stat = "NOK"
        stat = db.insert_roi_card(self.roi_data)
        self.clear_roi_card()
        return stat

    def clear_roi_card(self):
        self.roi_data = {
            'roi_type': " ",
            'roi_units': 0,
            'roi_rent': decimal.Decimal('0.00'),
            'roi_BLDG_type': " ",
            'roi_PPTY_type': " ",
            'roi_Property': " ",
            'player_number': 0,
            'roi_price': decimal.Decimal('0.00'),
            'max_qtrly_roi': decimal.Decimal('0.00'),
            'ppty_id': 0
        }

    def load_roi_from_addr(self, addr_data, player_number, ppty_id):
        d = []

        for addr in addr_data:
            roi = Decimal(addr['units']) * Decimal(addr['Rent']) * Decimal(3)
            self.roi_data = {
                'roi_type': "ROI",
                'roi_units': addr['units'],
                'roi_rent': addr['Rent'],
                'roi_BLDG_type': addr['BLDG_type'],
                'roi_PPTY_type': addr['PPTY_type'],
                'roi_Property': addr['Property'],
                'player_number': player_number,
                'roi_price': addr['invest_price'],
                'max_qtrly_roi': roi,
                'ppty_id': ppty_id
            }
            d.append(self.roi_data)
        return d

    def build_insert_roi(self, addr: dict):
        stat = "NOK"
        roi = Decimal(addr['units']) * Decimal(addr['Rent']) * Decimal(3)
        self.roi_data = addr.copy()
        stat = self.insert_roi_card()

        return stat


