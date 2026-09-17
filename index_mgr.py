from ts_database import *
from app_factory import create_app, mysql
from icecream import ic
import random
import decimal


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
        q, result = db.get_positions_data(self.table_name)
        if q > 0:
            tbl_length = int(q)
            if tbl_length > 1:
                rng = random.Random()
                data = {}
                data["low"] = int(1)
                data["high"] = tbl_length
                data["current"] = rng.randint(data["low"], data["high"])
            else:
                raise Exception(f"Error Condition: Table {self.table_name} has only one row...")
        else:
            raise Exception(f"Error Condition: Table {self.table_name} has no data rows...")

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


db = DB_Mgr(mysql)
tablelist = ["commodities", "address", "business", "lifecenter",
            "stockcenter", "shopping", "jobcenter", "learncenter",
            "bankercycle", "opportunities"]

_im_instance = None


def get_im():
    global _im_instance
    if _im_instance is None:
        _im_instance = IndexMgr(tablelist)   # only runs on first real call, not at import
    return _im_instance


class StockMgr:
    def __init__(self):
        self.table_name = "stocks"
        self.column_names = []
        self.stock_data = {
            'stock_count': 100,
            'stock_value': decimal.Decimal('0.00'),
            'stock_description': " ",
            'stock_cost': decimal.Decimal('0.00')
            }

    def set_position(self, row1: int, row2: int):
        rng = random.Random()
        position = rng.randint(row1, row2)
        return position

    def get_stock_row(self, row: int):
        status, result, column_names = db.get_table_row(self.table_name, row)
        if status == "NOK":
            raise RuntimeError(f"TakeStock {self.table_name} table read failure or key not found.")
        self.column_names = column_names
        return result[0]  # unwrap here, once

    def build_stock_array(self, stock_row, player_number):
        stock_array = []

        for column, value in stock_row.items():
            if column != "id":
                amt = decimal.Decimal(value)
                entry = self.stock_data.copy()  # start with all current fields
                entry['stock_value'] = amt
                entry['stock_cost'] = amt * 100
                entry['stock_description'] = column
                stock_array.append(entry)

        return stock_array

    def store_investment(self, stock_data, req_id, player_number):
        stat = "NOK"
        ndx = int(req_id) - 1
        new_value = decimal.Decimal(stock_data[ndx]['stock_cost']) * decimal.Decimal('1.10')
        invest_data = {
            'invest_type': "STCK",
            'invest_count': stock_data[ndx]['stock_count'],
            'invest_amount': decimal.Decimal(stock_data[ndx]['stock_cost']),
            'invest_description': stock_data[ndx]['stock_description'],
            'player_number': player_number,
            'invest_value': decimal.Decimal(new_value)
        }

        stat = db.insert_investments_from_sale(invest_data)
        return stat


class GoalMgr:

    # The 7 stock companies tracked per player. Used by the multi-company
    # goal resolvers (AAS, ASC) so we don't hardcode the field list twice.
    STOCK_COMPANIES = ['oNg', 'robotics', 'gold', 'paper', 'utility', 'auto', 'airline']

    # goal_code -> function(row) -> numeric value in the SAME UNITS as
    # game_target, so every goal can share one percentage formula.
    # Defined at class scope (not in __init__) since it only closes over
    # STOCK_COMPANIES, a class attribute — no need to rebuild it per instance.
    GOAL_RESOLVERS = {
        'AMA': lambda row: row['cash_on_hand'],
        'APV': lambda row: row['property_value'],
        'ASV': lambda row: row['stock_value'],
        'ABV': lambda row: row['business_value'],
        'ACV': lambda row: row['commodity_value'],
        'AJL': lambda row: row['job_level'],
        'ADL': lambda row: row['degree_level'],
        # Total stocks across all 7 companies vs. a single target (50,000).
        'ASC': lambda row: sum(row[co] for co in GoalMgr.STOCK_COMPANIES),
        # Average of each company's count (each capped at the per-company
        # target of 100) vs. target 100. Capping prevents one over-funded
        # company from masking shortfalls in the others.
        'AAS': lambda row: sum(min(row[co], 100) for co in GoalMgr.STOCK_COMPANIES) / len(GoalMgr.STOCK_COMPANIES),
    }

    def __init__(self):
        self.table_name1 = "gamegoals"
        self.table_name2 = "players"
        self.table_name3 = "investments"
        self.table_name4 = "game"
        self.game_ID = " "
        self.game_level = " "
        self.game_goal = " "
        self.game_goal_code = " "
        self.game_target = 0
        self.stock_data = {
            'plyr_number': 0,
            'oNg': 0,
            'robotics': 0,
            'gold': 0,
            'paper': 0,
            'utility': 0,
            'auto': 0,
            'airline': 0,
            'cash_on_hand': 0,
            'property_value': 0,
            'stock_value': 0,
            'business_value': 0,
            'commodity_value': 0,
            'job_level': 0,
            'degree_level': 0
        }

        # Re-instantiated every round / status request, so every step that
        # produces current state has to run here rather than being left to
        # the caller to remember. Goals are fixed at game start and never
        # change mid-game, but the object itself has no memory between
        # rounds, so get_game_goal() still has to re-fetch every time.
        self.player_data = self.load_data()
        self.get_game_goal()
        self.update_player_counts()
        ic(self.player_data)
        # self.plyr_prcntg = self.get_player_percentages()
        # ic(self.plyr_prcntg)


    def load_data(self) -> list:
        status, data = db.get_table_data(self.table_name2)
        if status == "NOK":
            raise RuntimeError("Error Condition: Load Data for GoalMgr Player table failed...")

        data1 = []  # real player rows only; no dummy template row
        for d in data:
            row = self.stock_data.copy()  # start from the template shape
            row['plyr_number'] = d['player_number']
            row['cash_on_hand'] = int(d['cash_on_hand'])
            row['property_value'] = int(d['property_value'])
            row['stock_value'] = int(d['stock_value'])
            row['business_value'] = int(d['business_value'])
            row['commodity_value'] = int(d['commodity_value'])
            row['job_level'] = d['job_level']
            row['degree_level'] = d['degree_level']
            self.game_ID = d['game_ID']
            data1.append(row)

        return data1

    def get_table_data(self, tbl_name):
        status = "NOK"
        status, result = db.get_table_data(tbl_name)
        if status == "NOK":
            raise Exception(f"Error Condition: Table {tbl_name} has no rows...")
        if len(result) == 1:
            return result[0]
        else:
            return result

    def get_game_goal(self):
        status, game_data, column_names = db.get_table_row_by_column(
            self.table_name4, "game_ID", self.game_ID)
        if status != "OK":
            return status

        self.game_level = game_data['game_level']
        self.game_goal_code = game_data['game_goal']

        stat, game_data2, column_names2 = db.get_table_row_by_columns(
             self.table_name1, "level_code", self.game_level,
             "goal_code", self.game_goal_code)
        if stat == "OK":
            ic(game_data2)
            self.game_goal = game_data2['goal']
            self.game_target = game_data2['target']
            ic(self.game_goal)
            ic(self.game_target)
            ic(stat)
        return stat

    def update_player_counts(self):
        status = "NOK"
        investments = self.get_table_data(self.table_name3)
        if len(investments) > 0:
            status = "OK"
            data1 = []
            for row in self.player_data:
                row = row.copy()
                for inv in investments:
                    if row['plyr_number'] == inv['player_number'] and inv['invest_type'] == "STCK":
                        row[inv['invest_description']] += inv['invest_count']
                data1.append(row)
            self.player_data = data1
        return status

    def calc_percentage(self, row) -> float:
        """Percentage of the active game goal a single player row has reached."""
        resolver = self.GOAL_RESOLVERS.get(self.game_goal_code)
        if resolver is None or not self.game_target:
            return 0.0
        value = resolver(row)
        pct = (value / self.game_target) * 100
        return round(min(pct, 100.0), 1)

    def get_player_percentages(self) -> list:
        """Returns [(plyr_number, pct), ...] for every player, e.g. to drive
        the 'Player Status' table on the game progress screen."""
        return [(row['plyr_number'], self.calc_percentage(row)) for row in self.player_data]

    def get_lead_player(self, player_pct_array):
        lead_player = "No Lead"
        high_pct = 0.0
        for plyr, pct in player_pct_array:
            if pct > high_pct:
                high_pct = pct
                lead_player = "Player " + str(plyr)
        return lead_player
