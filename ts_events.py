import random
import csv
from icecream import ic
from ts_database import *
from ts_cycle import *
from ts_game import *
from typing import List, Dict, Any
from app_factory import create_app, mysql
db = DB_Mgr(mysql)

class Shopping:
    def __init__(self, table_name):
        self.table_name = table_name
        self.data = self.load_data()
        # print(f"Loaded data: {self.data}")

    def load_data(self):
        status, result = db.get_table_data(self.table_name)
        if status == "NOK":
            raise Exception(f"Error Condition: Load {self.table_name} table failed...")
        return result

    def get_onsale_rows(self):
        data_out = []
        for row in self.data:
            if row['short_description'] == "On Sale":
                data_out.append(row)
        return data_out

    def get_list_of_retailers(self, data_out):
        retailers = []
        store = []
        for row in data_out:
            if row['INVITES'] not in store:
                store.append(row['INVITES'])
                row['short_description'] = "Retail"
                retailers.append(row)

        return retailers

    def select_store_items(self, store_name):
        store_items = []
        for row in self.data:
            if row['INVITES'] == store_name:
                store_items.append(row)
        return store_items
    """
    Event: sales_day
    Get {sales_pct} - Free Shipping
    Product: short_description
    Sales Price: $ sales_price
    Reg Price: $ -amount
    Points earned: points
    """
    def create_sales_info(self, store_items):
        sale_items = []
        nbr = [0, 1, 2, 3]
        sales_day = ["Monday Sale", "Black Friday Sale", "Holiday Sale", "Inventory Sale"]
        sales_pct = ["10% off", "50% off", "25% off", "35% off" ]
        sales_calc = [0.90, 0.50, 0.75, 0.65]
        choice = random.choice(nbr)
        for row in store_items:
                row['short_desc2'] = str(row['count']) + "-piece deal"
                row['sales_day'] = sales_day[choice]
                sp = abs(row['amount'])
                row['amount'] = round(sp, 0)
                row['points'] = int(sp)
                sp = round(Decimal(sp) * Decimal(sales_calc[choice]), 0)
                row['sales_price'] = sp
                row['sales_pct'] = sales_pct[choice]
                sale_items.append(row)
        print(f"sale items: {sale_items}")
        return sale_items

class SelectedItems:
    def __init__(self, selected_data: List[Dict[str, Any]]):
        self.selected_data = selected_data

    def update_game_table(self, game_ID):
        print(f"SALES UGT selected_data: {self.selected_data}")
        gb = GameBoard(game_ID)
        game_data = gb.get_game_data()
        for row in self.selected_data:
            # Implement the logic to update the game table based on the selected row
            sprice = Decimal(row['sales_price'])
            game_data['total_spending'] = Decimal(game_data['total_spending']) + Decimal(sprice)
        update_status = gb.put_game_data(game_data)
        if update_status != "OK":
            print(f"Failed to update game table in update_game_table.")
        return update_status

    def update_player_table(self, user):
        p = Players(user)
        print(f"SALES UPT selected_data: {self.selected_data}")
        for row in self.selected_data:
            # Implement the logic to update the player table based on the selected row
            sprice = Decimal(row['sales_price'])
            points = Decimal(row['points'])
            x = p.update_data("cash_on_hand", sprice, action="S")
            x = p.update_data("other_investments", sprice, action="A")
            x = p.update_data("points", points, action="A")
        update_status = p.update_table()
        if update_status != "OK":
            print(f"Failed to update player table update_player_table.")

    def update_investments_table(self, pn):
        print(f"SALES UIT selected_data: {self.selected_data}")
        iv = Investment()
        update_status = "NOK"
        for row in self.selected_data:
            # Implement the logic to update the investments table based on the selected row
            row['code'] = "SHP"
            update_status = iv.parse_row_data(row, pn)
        if update_status != "OK":
            print(f"Failed to update investments table update_investments_table.")

    def build_page_data(self):
        count = len(self.selected_data)
        i = 1
        sprice = Decimal(0)
        points = int(0)
        for row in self.selected_data:
            row['id'] = i
            sprice = sprice + Decimal(row['sales_price'])
            points = points + int(row['points'])
            print(f"SPrice (loop): {sprice}")
            i += 1
        print(f"PPrice: {sprice}")
        new_row = {
            "id": count,
            "INVITES": "Products",
            "long_description": "TOTAL COST",
            "sales_price": sprice,
            "points": points
        }
        self.selected_data.append(new_row)
        return self.selected_data


class Travel:
    def __init__(self):
        self.table_name = "travel"
        self.data = self.load_data()
        # print(f"Loaded data: {self.data}")

    def load_data(self):
        status, result = db.get_table_data(self.table_name)
        if status == "NOK":
            raise Exception(f"Error Condition: Load {self.table_name} table failed...")
        return result

    def get_vacation_rows(self):
        data_out = []
        for row in self.data:
            if row['ctgy'] == "Vacation":
                data_out.append(row)
        return data_out

    def create_sales_info(self, data):
        data_out = []
        for row in data:
            row['ctgy'] = "Vacation package for 4"
            row['type'] = "Flight destination: "
            pkg_price = Decimal(row['cost']) * Decimal(4)
            row['pkg_price'] = pkg_price
            row['points'] = Decimal(row['points']) * Decimal(4)
            data_out.append(row)
        return data_out

class SelectedTravel:
    def __init__(self, selected_data: List[Dict[str, Any]]):
        self.selected_data = selected_data

    def update_game_table(self, game_ID):
        print(f"TRAVEL UGT selected_data: {self.selected_data}")

        gb = GameBoard(game_ID)
        game_data = gb.get_game_data()
        for row in self.selected_data:
            # Implement the logic to update the game table based on the selected row
            if "pkg_price" in row:
                pprice = Decimal(row['pkg_price'])
            else:
                pprice = Decimal(row['cost'])
            game_data['total_spending'] = Decimal(game_data['total_spending']) + Decimal(pprice)

        update_status = gb.put_game_data(game_data)
        if update_status != "OK":
            print(f"Failed to update game table in update_game_table.")
        return update_status

    def update_player_table(self, user):
        p = Players(user)
        new_selected_data = []
        home_address = p.get_data("city_addr")
        distance = self.calc_distance(home_address)
        adjusted_cost, travel_mode = self.calc_travel_cost(distance[0])
        print(f"distance/cost/travel_mode: {distance} / {adjusted_cost} / {travel_mode}")
        print(f"TRAVEL UPT selected_data: {self.selected_data}")
        for row in self.selected_data:
            # Implement the logic to update the player table based on the selected row
            if "pkg_price" in row:
                pprice = Decimal(row['pkg_price'])
            else:
                if travel_mode == "Plane":
                    pprice = round(Decimal(row['cost']), 2)
                else:
                    pprice = round(Decimal(adjusted_cost), 2)
                    row['cost'] = pprice
            new_selected_data.append(row)

            points = Decimal(row['points'])
            x = p.update_data("cash_on_hand", pprice, action="S")
            x = p.update_data("other_investments", pprice, action="A")
            x = p.update_data("points", points, action="A")
        self.selected_data = new_selected_data.copy()
        update_status = p.update_table()
        if update_status != "OK":
            print(f"Failed to update player table update_player_table.")

    def update_investments_table(self, pn):
        print(f"TRAVEL UIT selected_data: {self.selected_data}")
        iv = Investment()
        update_status = "NOK"
        for row in self.selected_data:
            # Implement the logic to update the investments table based on the selected row
            row['code'] = "VAC"
            update_status = iv.parse_row_data(row, pn)
        if update_status != "OK":
            print(f"Failed to update investments table update_investments_table.")

    def update_investments_table2(self, pn):
        print(f"TRAVEL UIT2 selected_data: {self.selected_data}")
        iv = Investment()
        update_status = "NOK"

        for row in self.selected_data:
            # Implement the logic to update the investments table based on the selected row
            row['code'] = "TRVL"
            update_status = iv.parse_row_data(row, pn)
        if update_status != "OK":
            print(f"Failed to update investments table update_investments_table.")

    def calc_distance(self, home_address):

        distance = []
        for row in self.selected_data:
            dest_address = row['bus_type']
            point1 = home_address.split(".")
            point2 = dest_address.split(".")
            dist = (abs(int(point1[0]) - int(point2[0]))) + (abs(int(point1[1]) - int(point2[1])))
            distance.append(dist)
        print(f"distance: {distance}")
        return distance

    def calc_travel_cost(self, distance):
        """
        "Cab"> Cab – inexpensive ($1.00/mile)
        "Portal"> Portal – expensive ($5.00/mile)
        "Train"> Train – moderate ($2.00/mile)
        "Plane"> Plane – low to moderate ($3.50/mile)
        """
        travel_mode = session['travel_mode']
        tcpm = {"Cab": 0.05, "Portal": 0.50, "Train": 0.10, "Plane": 0.40}
        travel_cost = round(Decimal(tcpm[travel_mode]) * Decimal(distance), 0)
        return travel_cost, travel_mode

    def build_page_data(self):
        count = len(self.selected_data)
        i = 1
        pprice = Decimal(0)
        points = int(0)
        for row in self.selected_data:
            row['id'] = i
            row['ctgy'] = "Vacation for 4"
            pprice = pprice + Decimal(row['pkg_price'])
            points = points + int(row['points'])
            print(f"PPrice (loop): {pprice}")
            i += 1
        print(f"PPrice: {pprice}")
        new_row = {
            "id": count,
            "ctgy": "Vacations",
            "short_description": "TOTAL COST",
            "long_description": " ",
            "pkg_price": pprice,
            "points": points
        }
        self.selected_data.append(new_row)
        return self.selected_data


class Business:
    def __init__(self):
        self.table_name = "companytravel"
        self.data = self.load_data()
        # print(f"Loaded data: {self.data}")

    def load_data(self):
        status, result = db.get_table_data(self.table_name)
        if status == "NOK":
            raise Exception(f"Error Condition: Load {self.table_name} table failed...")
        return result

    def get_company_rows(self):
        data_out = []
        for row in self.data:
            if row['ctgy'] == "Remote":
                row['cost'] = int(row['cost'])
                data_out.append(row)
        return data_out

    def get_local_rows(self):
        data_out = []
        for row in self.data:
            if row['ctgy'] == "Local":
                row['cost'] = int(row['cost'])
                data_out.append(row)
        return data_out

    def get_company_list(self, data_out):
        companies = []
        business = []
        positions = ["CEO", "CFO", "CIO",  "COO", "CEO"]
        for row in data_out:
            if row['business'] not in business:
                business.append(row['business'])
                row["salary"] = round(Decimal(row['cost']) * Decimal(0.5), 2)
                row["bonus"] = round(Decimal(row['points']) * Decimal(0.5), 2)
                row["position"] = random.choice(positions)
                companies.append(row)

        return companies

    def get_travel_list_by_company(self, data_out, company):
        company_list = []
        destinations = []
        print(f"data out: {data_out}")
        print(f"company: {company}")
        for row in data_out:
            if company == row['business']:
                if row['short_description'] not in destinations:
                    destinations.append(row['short_description'])
                    company_list.append(row)
        print(f"Company List: {company_list}")

        company_projects = random.sample(company_list, 3)
        return company_projects

    def build_page_data(self, company_projects):
        count = len(company_projects)
        trip_cost = Decimal(0)
        priority = ["High", "Medium", "Low"]
        i = 1
        pprice = Decimal(0)
        points = int(0)
        for row in company_projects:
            row['id'] = i
            row['priority'] = random.choice(priority)
            points = points + int(row['points'])
            trip_cost = round(Decimal(row['cost']) + trip_cost, 0)
            i += 1
        new_row = {
            "id": count,
            "priority": "Projects",
            "purpose": " ",
            "short_description": "TOTALS",
            "cost": trip_cost,
            "points": points
        }
        company_projects.append(new_row)
        return company_projects

class BusinessProjects:
    def __init__(self, selected_data: List[Dict[str, Any]]):
        self.selected_data = selected_data

    def update_game_table(self, game_ID):
        print(f"Projects UGT selected_data: {self.selected_data}")
        gb = GameBoard(game_ID)
        game_data = gb.get_game_data()
        for row in self.selected_data:
            # Implement the logic to update the game table based on the selected row
            sprice = Decimal(row['cost'])
            game_data['total_spending'] = Decimal(game_data['total_spending']) + Decimal(sprice)
        update_status = gb.put_game_data(game_data)
        if update_status != "OK":
            print(f"Failed to update game table in update_game_table.")
        return update_status

    def update_player_table(self, user):
        p = Players(user)
        print(f"Projects UPT selected_data: {self.selected_data}")
        for row in self.selected_data:
            # Implement the logic to update the player table based on the selected row
            sprice = Decimal(row['cost'])
            points = Decimal(row['points'])
            x = p.update_data("cash_on_hand", sprice, action="S")
            x = p.update_data("other_investments", sprice, action="A")
            x = p.update_data("points", points, action="A")
        update_status = p.update_table()
        if update_status != "OK":
            print(f"Failed to update player table update_player_table.")

    def update_investments_table(self, pn):
        print(f"Projects UIT selected_data: {self.selected_data}")
        iv = Investment()
        update_status = "NOK"
        for row in self.selected_data:
            # Implement the logic to update the investments table based on the selected row
            row['code'] = "BUS"
            update_status = iv.parse_row_data(row, pn)
        if update_status != "OK":
            print(f"Failed to update investments table update_investments_table.")

    def build_page_data(self):
        count = len(self.selected_data)
        i = 1
        sprice = Decimal(0)
        points = int(0)
        for row in self.selected_data:
            row['id'] = i
            sprice = sprice + Decimal(row['cost'])
            points = points + int(row['points'])
            print(f"Cost (loop): {sprice}")
            i += 1
        print(f"Cost: {sprice}")
        new_row = {
            "id": count,
            "INVITES": "Products",
            "long_description": "TOTAL COST",
            "sales_price": sprice,
            "points": points
        }
        self.selected_data.append(new_row)
        return self.selected_data

class TravelReport:

    def __init__(self, player_name, report_name, trip: dict):
        self.player_name = player_name
        self.report_name = report_name
        self.trip = trip
        if self.report_name != "Business Report":
            self.table_name = "travelreport"
            self.data = self.load_data()
        else:
            self.table_name = "businessreport"
            self.data = self.load_data()
        ic(self.table_name, self.trip, report_name, self.data)

    def load_data(self):
        status, result = db.get_table_data(self.table_name)
        if status == "NOK":
            raise Exception(f"Error Condition: Load {self.table_name} table failed...")
        return result

    def select_business_report(self):
        trip = self.trip.copy()
        ic(trip)
        for row in self.data:
            if row['project'] in self.trip['purpose']:
                trip['overview'] = row['overview']
                trip['recap'] = row['recap']
                trip['exec_sum'] = row['exec_sum']
                trip['milestones'] = row['milestones']
                trip['challenges'] = row['challenges']
                trip['people'] = row['people']
        ic(trip, self.trip)
        return trip

    def select_vacation_report(self):
        trip = self.trip.copy()
        for row in self.data:
            if row['destination'] == self.trip['description']:
                trip['custom1'] = row['custom1']
                trip['trip'] = row['trip']
                trip['sights'] = row['sights']
                trip['events'] = row['events']
                trip['people'] = row['people']
                trip['custom2'] = row['custom2']
        ic(trip, self.trip)
        return trip

    def select_random(self):
        selected_set = random.choice(self.data)
        self.custom1 = selected_set["custom1"]
        self.destination = selected_set["destination"]
        self.trip = selected_set["trip"]
        self.sights = selected_set["sights"]
        self.events = selected_set["events"]
        self.people = selected_set["people"]
        self.custom2 = selected_set["custom2"]

class GameGoals:
    def __init__(self):
        self.table_name = "gamegoals"
        self.data = self.load_data()
        # print(f"Loaded data: {self.data}")

    def load_data(self):
        status, result = db.get_table_data(self.table_name)
        if status == "NOK":
            raise Exception(f"Error Condition: Load {self.table_name} table failed...")
        return result

    def select_goal_code(self, game_type, goal_code):
        selected_goal = []
        for row in self.data:
            if row['type'] == game_type and row['goal_code'] == goal_code:
                selected_goal.append(row)
        return selected_goal

    def replace_goal(self, row):
        status = "NOK"
        for goal in row:
            status = db.update_goal_by_id(goal)
        return status

    def get_goal_name(self, ggoal):
        desc = "None"
        for row in self.data:
            if row['goal_code'] == ggoal:
                desc = row['goal']
                break
        return desc

    def get_level_name(self, glevel):
        desc = "None"
        for row in self.data:
            if row['level_code'] == glevel:
                desc = row['level']
                break
        return desc

    def build_status_report(self, glevel, ggoal, username):
        goal_selected = {}
        # search and point to goal selected by captain
        for row in self.data:
            if row['level_code'] == glevel and row['goal_code'] == ggoal:
                goal_selected = row
                break
        if len(goal_selected) < 1:
            flash("Game level or goal invalid.", "error")
        trailer = " "

        goal_name = self.get_goal_name(ggoal)
        level_name = self.get_level_name(glevel)
        features = [
            "Features Legend:",
            "1) RP = Request Play",
            "2) TP = Triple Play",
            "3) IV = Invites",
            "4) SP = Single Play",
            "5) RN = Random Play"
        ]
        goals = []
        goals.append(f"Active Game Level & Goal: {level_name} | {goal_name}")

        if goal_selected['target'] > 50001:
            value = str(goal_selected['target'])
            if ggoal == "AMA":
                trailer = "Cash on Hand"
            else:
                trailer = "Monetary Value"
            goals.append(f"$ {value} {trailer}")
        else:
            trailers = {"ASC": "Stocks of any companies", "AJL": "Job Promotions", "ADL": "College Degrees",
                        "AAS": "Stocks or more from each available stock company"}
            trailer = trailers[ggoal]
            value = str(goal_selected['target'])
            goals.append(f" {value} {trailer}")
        value = "Features Disabled:"
        trailer = goal_selected['disable']
        if trailer == " " or trailer == "" or trailer is None:
            trailer = "None"
        goals.append(f" {value} {trailer}")
        goals.append(" ")
        # Build two separate list arrays for player_status
        player_status1 = ["Player #"]
        player_status2 = ["% of Goal"]
        if goal_selected['goal_code'] != "AAS":
            player_status3 = {}
        else:
            player_status3 = {}
            player_status3["(STOCK COUNTS)->"] = []
            player_status3["oNg"] = []
            player_status3["robotics"] = []
            player_status3["gold"] = []
            player_status3["paper"] = []
            player_status3["utility"] = []
            player_status3["auto"] = []
            player_status3["airline"] = []
        plyr = Players(username)
        game_ID = plyr.game_ID
        status, players = db.get_players_game_card(game_ID, allcolumn="Y")
        for player in players:
            pn = player['player_number']
            player_status1.append(str(pn))
            player_status2, player_status3 = self.calc_percent(player, goal_selected, player_status2, player_status3)
        if len(player_status2) < len(player_status1):
            diff = len(player_status1) - len(player_status2)
            for i in range(diff):
                player_status2.append("")
        if len(player_status2) > len(player_status1):
            diff = len(player_status2) - len(player_status1)
            for i in range(diff):
                player_status1.append("")
        return features, goals, player_status1, player_status2, player_status3

    def calc_percent(self, player, goal_selected, player_status2, player_status3):
        pct = 0.00
        if goal_selected['goal_code'] == "AMA":
            cash = player['cash_on_hand']
            cash_goal = goal_selected['target']
            pct = Decimal(0.00)
            pct = round(Decimal(cash) / Decimal(cash_goal), 2) * 100
        elif goal_selected['goal_code'] == "APV":
            pv = player['property_value']
            pv_goal = goal_selected['target']
            pct = Decimal(0.00)
            pct = round(Decimal(pv) / Decimal(pv_goal), 2) * 100
        elif goal_selected['goal_code'] == "ASV":
            sv = player['stock_value']
            sv_goal = goal_selected['target']
            pct = Decimal(0.00)
            pct = round(Decimal(sv) / Decimal(sv_goal), 2) * 100
        elif goal_selected['goal_code'] == "ABV":
            bv = player['business_value']
            bv_goal = goal_selected['target']
            pct = Decimal(0.00)
            pct = round(Decimal(bv) / Decimal(bv_goal), 2) * 100
        elif goal_selected['goal_code'] == "ACV":
            cv = player['commodity_value']
            cv_goal = goal_selected['target']
            pct = Decimal(0.00)
            pct = round(Decimal(cv) / Decimal(cv_goal), 2) * 100
        elif goal_selected['goal_code'] == "AJL":
            jl = player['job_level']
            jl_goal = goal_selected['target']
            pct = Decimal(0.00)
            pct = round(Decimal(jl) / Decimal(jl_goal), 2) * 100
        elif goal_selected['goal_code'] == "ADL":
            dl = player['degree_level']
            dl_goal = goal_selected['target']
            pct = Decimal(0.00)
            pct = round(Decimal(dl) / Decimal(dl_goal), 2) * 100
        if goal_selected['goal_code'] == "AAS":
            as_goal = goal_selected['target']
            pct = Decimal(0.00)
            iv = Investment()
            pn = str(player['player_number'])
            stocks, stock_count = iv.get_stock_investments(pn)
            pct = round(Decimal(stock_count) / Decimal(as_goal*7), 2) * Decimal(100)
            player_status2.append(str(pct))
            player_status3["(STOCK COUNTS)->"].append(" ")
            for i, key in enumerate(stocks):
                player_status3[key].append(stocks[key])
        else:
            player_status2.append(str(pct))
        ic(player_status2, player_status3)
        return player_status2, player_status3