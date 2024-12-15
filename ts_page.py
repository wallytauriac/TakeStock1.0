import decimal
from flask import current_app
from ts_database import *
from ts_game import *
from ts_events import *
from ts_page2 import *
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from datetime import datetime, date
from wtforms import Form
from app_factory import create_app, mysql
from functools import wraps
import re

ts_page_bp = Blueprint('ts_page_bp', __name__, template_folder="templates")
db = DB_Mgr(mysql)

def is_logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('You need to be logged in to view this page', 'error')
            return redirect(url_for('login'))  # Ensure 'login' route is defined in ts_main.py
        return f(*args, **kwargs)
    return decorated_function

def render_game_card(session, game_id):
    # Set game card settings

    if 'data' in session:
        data = session['data']
    else:
        data = {}

    # Build the game card data dictionary
    try:
        data['player_number'] = session.get('player_number')
        data['player_move'] = session.get('player_move')
        data['player_round'] = session.get('player_round')
        data['player_message1'] = "Buy or sell business, property, stock, or commodity."
        data['player_message2'] = "Auto-select of an opportunity, want, or need."
        data['player_message3'] = ("Up to three options to select. "
                                   "The first is a business opportunity.  "
                                   "The second is a property purchase opportunity.  "
                                   "The third is a stock deal. If all are declined, then you lose money, "
                                   "a consultant fee of $3,000.")
        if data['player_number'] == 1 and data['player_round'] == 1:

            ga = Game_Action()

            data['ga'] = ga.get_action_items()

            print("GA ", data['ga'])
        else:
            # Set indexes
            ga = Game_Action()
            data['ga'] = ga.get_action_items()
            print("GA ", data['ga'])
    except Exception as e:
        return f"An error occurred in render game card build: {e}"
    return data

def process_first_move(game_ID, data):
    gb = GameBoard(game_ID)
    # Population growth, GDP & CPI management
    gb.update_gdp()
    gb.update_cpi()
    gc = gb.get_game_data()
    print("First Move GC", gc)

    # Do not setup BILL type Investment cards
    # status = setup_bill_investment_cards(game_ID)

    status = gb.put_game_data(gc)
    if status == "OK":
        data['gc'] = gc
        session['data'] = data
    return status

def setup_bill_investment_cards(game_ID):

    status, players = db.get_players_game_card(game_ID, allcolumn="Y")
    for player in players:
        pc = Players(player['username'])
        iv = Investment()
        invest_data = iv.get_player_investments_by_type(player['player_number'], "BILL")
        stat = iv.remove_player_investments_by_type(player['player_number'], "BILL")
        if len(invest_data) >= 5:
            pass
        elif len(invest_data) == 0:
            bill_type = {"pi": "Property Insurance", "ci": "Car Insurance", "pt": "Property Tax", "ft": "Federal Tax",
                         "ut": "Utilities"
                         }
            d = {}
            invest_data = []
            for key, value in (bill_type.items()):
                d = {'invest_description': value}
                invest_data.append(d)
            stat = iv.build_bill_investments(player, invest_data)
        else:
            stat = iv.build_bill_investments(player, invest_data)
    status = stat
    return status


def process_end_of_round(session):
    """
        # Reset Stock Index
        # Check the round for Salary Pay every 3rd round
        salary + (salary * degree_level * 0.5) + (salary * job_level * 0.7
        # Check for 10th round to collect taxes (Property and Federal)
        COH = COH - (COH * 0.01)
        # Check every 5th round to collect insurances and rent and loans
        COH = COH - (PPTY VALUE * 0.01)
        # Population growth, total spending and earnings

    """
    print("End of Round Session: ", session)
    game_ID = session["game_ID"]
    data = session.get('data')

    gb = GameBoard(game_ID)
    # Population growth, GDP & CPI management
    gb.update_gdp()
    gb.update_population()
    gb.update_cpi()
    gc = gb.get_game_data()
    print("End Round GC", gc)

    # Reset Stock Index and Position pointer
    g = Game_Action()
    ga = g.get_action_items()
    data['ga'] = ga
    session['data'] = data
    # Get the player cards for update
    sal = 0.00
    status, players = db.get_players_game_card(game_ID, allcolumn="Y")
    for player in players:
        pc = Players(player['username'])
        # Salary Pay
        if data['player_round'] % 3 == 0:
            # Pay salaries to players
            sal = pc.recalc_salary()
            # Collect Rent on rental properties
            roi = ROI_Pay()
            if len(roi.roi_data) != 0:
                roi_data = roi.select_ROI_by_player(player['username'])
                if len(roi_data) != 0:
                    stat1, stat2 = roi.update_game_tables(player['username'])
        iv = Investment()
        bp = Billpay()
        if data['player_round'] % 5 == 0:
            #
            # Assess Car Insurance
            #
            bill_card1 = pc.assess_car_insurance_status()  # If true then pay insurance premium
            print(f"End of Round Build Card 1: {bill_card1} ")
            # insert billpay history
            bp.build_billpay_card(pc.data, bill_card1)
            #
            # Assess Rent, Loans
            #
            stat = iv.verify_loan(pc.data)
            stat = iv.verify_rent(pc.data)
            # Pay Utilities
            stat = iv.pay_other_bills(pc.data)
        if data['player_round'] % 10 == 0:
            #
            # Assess Property Insurance
            #
            bill_card = pc.assess_property_insurance_status()  # If true then pay insurance premium
            # insert billpay history
            bp.build_billpay_card(pc.data, bill_card)
            #
            # Assess Taxes (Federal and Property)
            #
            bill_card2, bill_card3 = pc.assess_tax_status()
            bp.build_billpay_card(pc.data, bill_card2)
            bp.build_billpay_card(pc.data, bill_card3)

        stat = pc.update_table()
    gc['total_earnings'] += decimal.Decimal(sal)
    status = gb.put_game_data(gc)
    if status == "OK":
        data['gc'] = gc
        session['data'] = data
        stat = check_game_status()

    return status

def check_game_status():
    glevel = session['glevel']
    ggoal = session['ggoal']
    data = session['data']
    data['user_captain'] = session['username']
    result, q = db.get_player_record(session['username'])
    data['game_ID'] = result['game_ID']
    gg = GameGoals()
    features, goals, player_status1, player_status2, player_status3 = gg.build_status_report(glevel, ggoal, session['username'])
    ic(features, goals, player_status1, player_status2, player_status3)
    go = "Nogo"
    i = 0
    for i in range(len(player_status2)):
        if i > 0:
            if Decimal(player_status2[i]) >= Decimal(90):
                flash(f"Player {i} is approaching a WIN status.", "success")
                go = "Go"

    if go == "Go":
        redirect("ts_sub1_bp.game_status")
    stat = "OK"




def render_player_card(players, player_number):
    # Process Players card
    for player in players:
        if player['player_number'] == player_number:
            return player

def render_edit_profile(form, result):
    form.name.data = result['name']
    form.email.data = result['email']
    form.player_number.data = result['player_number']
    form.status.data = result['status']
    form.role.data = result['role']
    return form

def render_game_settings(form):
    form.status.data = "New"
    form.player_count.data = 0
    form.start_date.data = date.today()
    form.game_ID.data = "TS" + date.today().strftime("YYYY-MM-DD")
    form.population.data = 500000
    form.population_chg.data = 0.06
    form.glevel.data = "Easy Play"
    form.ggoal.data = "AMA"
    return form

def render_gametable_settings(form, result):
    form.status.data = result['status']
    form.player_count.data = result['player_count']
    form.start_date.data = result['start_date']
    form.game_ID.data = result['game_ID']
    if result['population'] == 0:
        form.population.data = 500000
    else:
        form.population.data = result['population']
    if result['population_chg'] == 0:
        form.population_chg.data = 0.06
    else:
        form.population_chg.data = result['population_chg']
    form.glevel.data = result['game_level']
    form.ggoal.data = result['game_goal']
    #form.process()  # Apply the defaults
    return form

def format_game_settings():
    gg = GameGoals()
    data = gg.data
    levels_goals = {}

    for row in data:
        level_code = row['level_code']
        level_name = row['level']
        goal_code = row['goal_code']
        goal_name = row['goal']
        goal_desc = row['goal_desc']

        if level_code not in levels_goals:
            levels_goals[level_code] = {'name': level_name, 'goals': {}, 'desc': row['level_desc']}

        levels_goals[level_code]['goals'][goal_code] = {'name': goal_name, 'desc': goal_desc}

    return levels_goals
tasks = [
        {"name": "Clear Investment tables", "status": "Pending"},
        {"name": "Empty Ancillary tables", "status": "Pending"},
        {"name": "Remove Game table", "status": "Pending"},
        {"name": "Clear Positions table", "status": "Pending"},
        {"name": "Refresh each player table", "status": "Pending"}
    ]
def process_end_of_game(username, task):
    status = "Failed"
    gb = GameBoard(username)
    game_ID = gb.game_ID
    if task['name'] == "Clear Investment tables":
        stat = db.delete_table_data("investments")
        stat = db.delete_table_data("investment_return")
        stat = db.delete_table_data("billpay")
    elif task['name'] == "Empty Ancillary tables":
        stat = db.delete_table_data("sessions")
    elif task['name'] == "Clear Positions table":
        stat = db.delete_table_data("positions")
    elif task['name'] == "Refresh each player table":
        plyr = Players(username)
        stat = db.clear_players_card(game_ID)
    elif task['name'] == "Remove Game table":
        stat = db.delete_table_data("game")
    status = "Completed"
    return status


def render_sp_options():
    """
    Get SPBC Selections
    'STOCKS', 'PROPERTY', 'BUSINESS', 'COMMODITY' Tables & Objects
    """
    options = []

    ctgy = ['STOCKS', 'PROPERTY', 'BUSINESS', 'COMMODITY']
    type = ['STCK', 'PPTY', 'BUS', 'COMM']
    desc, invest = build_sp_options()

    d = {}
    for i in range(4):
        d['opt_ctgy'] = ctgy[i]
        d['opt_type'] = type[i]
        d['opt_desc'] = desc[i]
        d['opt_invest'] = invest[i]
        options.append(d)
        d = {}
    return options

def build_sp_options():
    desc = []
    invest = []
    pi_stck = PriceIndex("stocks")
    # Build Stock Selected
    sc, cc = pi_stck.choose_stock_brand("STCK")  # SC=Stock Choice and CC=Count Choice
    pos = pi_stck.get_new_position()
    row1 = pi_stck.get_new_row()
    row1['sc'] = sc
    row1['cc'] = cc
    session['bs'] = row1  # store the stock row in session
    value = row1[sc]  # get the stock value
    sc = sc.capitalize()
    desc.append(sc + " Stocks Count=" + str(cc))
    invest.append("$   " + str(value * cc))  # Calculate stock value and store for display
    # Build Property Selected
    pi_ppty = PriceIndex("address")
    pos = pi_ppty.get_new_position()
    row2 = pi_ppty.get_new_row()
    session['bp'] = row2
    b_type = row2['BLDG_type']
    p_type = row2['PPTY_type']
    desc.append(b_type + " for " + p_type)
    price = round(row2['Price'], 0)
    invest.append("$  " + str(price))
    # Build Business Selected
    pi_bus = PriceIndex("business")
    pos = pi_bus.get_new_position()
    row3 = pi_bus.get_new_row()
    session['bb'] = row3
    desc.append(row3['business'])
    invest.append("$  " + str(row3['buy']))
    # Build Commodity Selected
    pi_comm = PriceIndex("commodities")
    commc, cc = pi_comm.choose_stock_brand("COMM")  # COMMC=COMM Choice and CC=Count Choice
    pos = pi_comm.get_new_position()
    row4 = pi_comm.get_new_row()
    row4['commc'] = commc
    row4['cc'] = cc
    session['bc'] = row4
    if commc == "Certificates" or commc == "Money":
        value = row4[commc] * 1000000
    else:
        value = row4[commc]
    desc.append(commc + " Mkt Share Count=" + str(cc))
    iv = value * int(cc)
    iv = round(int(iv), 0)
    invest.append("$   " + str(iv))
    return desc, invest

def render_bs_options(session, splay="Y"):
    options = []
    if splay == "Y":
        ctgy = ['MESSAGE', 'SALES OFFER', 'COST PER SHARE', 'SHARE COUNT', 'TOTAL COST']
        desc = ['This stock is available for your purchase at the current cost per share.  '
                'Remember, a refusal can cost you a consulting fee.)'
                ]
    else:
        ctgy = ['STOCK MESSAGE', 'SALES OFFER', 'SHARE COUNT', 'TOTAL COST']
        desc = ['This stock is available for your purchase at the current cost.  ']

    # Build BS Options Data
    bs = session['bs']
    sc_name = bs['sc']
    desc.append(bs['sc'].capitalize() + " Stock")
    cps = bs[sc_name]
    if splay == "Y":
        desc.append("$  " + str(cps))  # Cost per Share
    cnt = bs['cc']
    desc.append(str(cnt) + " Share(s)")
    tc = int(cnt) * int(cps)
    desc.append("$  " + str(tc))
    o = Options(ctgy=ctgy, type=None, desc=desc, invest=None)

    options = o.get_options()
    return options

def render_bp_options(session, pplay="Y"):
    if pplay == "Y":
        options = []
        ctgy = ['MESSAGE', 'SALES OFFER', 'PROPERTY TYPE', 'ASKING PRICE', 'FEES', 'TOTAL COST']
        desc = ['Here is an opportunity for you to accept or refuse a property for sale. '
                'Remember, a refusal can cost you a consulting fee.)'
                ]
    else:
        options = session['options']
        ctgy = ['PROPERTY MESSAGE', 'SALES OFFER', 'PROPERTY TYPE', 'TOTAL COST']
        desc = ['Here is an opportunity for you to accept a property for sale. '
                'Some stock, a property, and a business. Wow!)'
                ]
    bp = session['bp']
    desc.append(bp['Property'])
    type = bp['BLDG_type'] + " for " + bp['PPTY_type']
    desc.append(type)
    if pplay == "Y":
        price = bp['Price']
        desc.append("  $  " + str(price))
        calc = float(price) * 0.06
        fees = int(round(calc, 2))
        desc.append("  $  " + str(fees))
    else:
        price = bp['Price']
        calc = float(price) * 0.06
        fees = int(round(calc, 2))
    tc = int(float(bp['Price'])) + int(fees)
    desc.append("  $  " + str(tc))
    session['PPTY_cost'] = desc[len(desc)-1]

    print(f"session in render_bp_options: {session}")
    if pplay == "Y":
        o = Options(ctgy=ctgy, type=None, desc=desc, invest=None, options=None)
    else:
        o = Options(ctgy=ctgy, type=None, desc=desc, invest=None, options=options)

    options = o.get_options()

    return options

def render_bb_options(session, bplay="Y"):
    if bplay == "Y":
        options = []
        ctgy = ['MESSAGE', 'BUSINESS NAME', 'SALE PRICE', 'PARTNERSHIP', 'CLUB PRICE', 'RENT/TICKET VALUE']
        desc = ['Here is an opportunity for you. Consider this business for sale. '
                'Remember, a refusal can cost you a consulting fee.)'
               ]
    else:
        options = session['options']
        ctgy = ['MESSAGE', 'BUSINESS NAME', 'SALE PRICE']
        desc = ['Here is an opportunity for you. Consider this business for sale. '
                'Remember, a refusal can cost you a consulting fee.)'
                ]

    bb = session['bb']
    desc.append(bb['business'])
    desc.append('$  ' + str(bb['buy']))
    if bplay == "Y":
        desc.append('$  ' + str(bb['partner']))
        desc.append('$  ' + str(bb['club']))
        desc.append('$  ' + str(bb['value']))
    if bplay == "Y":
        o = Options(ctgy=ctgy, type=None, desc=desc, invest=None, options=None)
    else:
        o = Options(ctgy=ctgy, type=None, desc=desc, invest=None, options=options)

    options = o.get_options()

    return options

def render_bc_options(session):
    options = []
    ctgy = ['MESSAGE', 'SALE OFFER', 'COST PER SHARE', 'SHARE COUNT', 'TOTAL COST']
    desc = ['This commodity is available for your purchase at the current cost per share.  '
            ]
    # Build BC Options Data
    bc = session['bc']
    cc_name = bc['cc']
    desc.append(bc['commc'] + " Shares")
    bcv = bc['commc']
    cps = bc[bcv]
    desc.append("$  " + str(cps))  # Cost per Share
    cnt = bc['cc']
    desc.append(str(cnt) + " Share(s)")
    if bc['commc'] == "Certificates" or bc['commc'] == "Money":
        value = float(cps) * 1000000
    else:
        value = float(cps)
    tc = int(cnt) * int(float(value))
    desc.append("$  " + str(tc))

    o = Options(ctgy=ctgy, type=None, desc=desc, invest=None)

    options = o.get_options()

    return options

def render_sale_options(data):
    user = session['user']
    print(f"Render Sale DATA: {data}")
    bnkr = banker()
    options = session['options']
    print(f"Render Sale Options: {options}")
    ctgy = ['MESSAGE', 'TRANSACTION', 'TOTAL COST']
    desc = ['Your purchase is complete.  Cash sales are final.']
    if data['buy_type'] == "bs":
        desc.append('STOCK PURCHASE')
        desc.append(options[4]['opt_desc'])
        stat = bnkr.assess_purchase_power(user, desc[len(desc) - 1])
    if data['buy_type'] == "bp":
        desc.append('PROPERTY PURCHASE')
        print(f"session in render_sale_options: {session}")
        print("Session before accessing PPTY_cost in render_sale_options:", session)
        try:
            session['PPTY_cost'] = options[5]['opt_desc']
            desc.append(session['PPTY_cost'])  # Access PPTY_cost
            print("PPTY_cost found:", session['PPTY_cost'])
        except KeyError:
            print("Error: PPTY_cost not found in session")
            raise Exception("Error: PPTY_cost not found in session")

        print("Desc after accessing PPTY_cost:", desc)

        stat = bnkr.assess_purchase_power(user, desc[len(desc) - 1])
    if data['buy_type'] == "bb":
        if data['choice'] == "1":
            desc.append(options[1]['opt_desc'])
            desc.append(options[2]['opt_desc'])
        elif data['choice'] == "2":
            desc.append(options[1]['opt_desc'])
            desc.append(options[3]['opt_desc'])
        elif data['choice'] == "3":
            desc.append(options[1]['opt_desc'])
            desc.append(options[4]['opt_desc'])
        print(f"Business for sale: {desc}")
        stat = bnkr.assess_purchase_power(user, desc[len(desc) - 1])
    if data['buy_type'] == "bc":
        desc.append('COMMODITY PURCHASE')
        desc.append(options[4]['opt_desc'])
        stat = bnkr.assess_purchase_power(user, desc[len(desc) - 1])

    session['buying_power'] = stat
    if stat == "LOAN":

        ctgy.append("Purchase Power Status")
        desc.append("The banker was able to qualify you for a loan to purchase. The loan was added to your cash on hand.")
    elif stat == "NO":

        ctgy.append("Purchase Power Status")
        desc.append("The banker was not able to qualify you for a loan to purchase. No purchase made for you.")

    o = Options(ctgy=ctgy, type=None, desc=desc, invest=None)

    options = o.get_options()

    dataopt = {
        'data': data,
        'user': user,
        'options': options
    }
    print("Sale Options DATAOPT = ", dataopt)
    print("Session Dictionary: ", session)
    if stat != "NO":
        update_player_game(dataopt)
    return dataopt

def update_player_game(dataopt):
    """
    update the game table (gc dictionary)
    -> Spending and Expenditure adjustments
    -> Update counts
    ->
    update the player's table (pc and options dictionary)
    -> Cash-on-Hand adjustments
    -> Product count adjustments
    -> Investment table insert(s)
    """
    invest_data = {
        'invest_type': " ",
        'invest_count': 0,
        'invest_amount': 0.00,
        'invest_description': " ",
        'player_number': 0,
        'invest_value': 0.00
    }
    # Unload data dictionary from the dataopt nested dictionary
    data1 = dataopt['data']
    print(f"Update Player data1: {data1}")
    buy_type = data1['buy_type']
    # Unload options dictionary from dataopt nested dictionary
    options1 = dataopt['options']
    print(f"Update Player options1: {options1}")
    # Unload product type from the sessions nested dictionary
    product_data = session[buy_type]
    # Unload data dictionary from the sessions nested dictionary
    data2 = session['data']
    print(f"Update Player data2: {data2}")
    if 'pc' not in data2:
        pc = db.get_player_by_number(data1['player_number'])
        data2['pc'] = pc
    else:
        pc = data2['pc']
    game_ID = pc['game_ID']
    # Unload options from the session nested dictionary
    options2 = session['options']
    print(f"Update Player options2: {options2}")
    invest_data['player_number'] = data1['player_number']
    invest_card = {}
    if buy_type == "bs":
        invest_card = build_invest_card(invest_data, product_data['sc'], options2[3]['opt_desc'], options2[4]['opt_desc'])
        invest_card['invest_type'] = "STCK"
    if buy_type == "bp":
        invest_card = build_invest_card(invest_data, product_data['Property'], "1", session['PPTY_cost'])
        invest_data['own_code'] = product_data['PPTY_type']
        invest_card['invest_type'] = "PPTY"
    if buy_type == "bb":
        if data1['choice'] == "1":
            invest_card = build_invest_card(invest_data, options1[1]['opt_desc'], "count=1", options1[2]['opt_desc'])
        if data1['choice'] == "2":
            invest_card = build_invest_card(invest_data, options1[1]['opt_desc'], "count=1", options2[3]['opt_desc'], own="PART")
        if data1['choice'] == "3":
            invest_card = build_invest_card(invest_data, options1[1]['opt_desc'], "count=1", options2[4]['opt_desc'], own="CLUB")
        invest_card['invest_type'] = "BUS"
    if buy_type == "bc":
        invest_card = build_invest_card(invest_data, product_data['commc'], options2[3]['opt_desc'], options2[4]['opt_desc'])
        invest_card['invest_type'] = "COMM"
    stat, gc = db.get_game_card(game_ID)
    print(f"Update Player Invest Card: {invest_card}")
    status = db.insert_investments_from_sale(invest_card)
    #
    #  Create ROI card for PPTY investment having Rent in own_code
    if status == "OK":
        flash("Good investing!", "success")
    print(f"GC before investment: {gc}")
    # Use the Player class to update
    # Add a subtract option to update method

    status = db.update_game_player(invest_card['invest_amount'], gc, dataopt)
    if status == "OK":
        flash("Good Play!", "success")

def build_invest_card(invest_data, product, opt1, opt2, own="FULL"):
    invest_data['invest_description'] = product

    n = opt1
    n = extract_numeric_value(n)
    a = opt2
    if n is None or n is "None" or n == "":
        n = 1

    a = extract_numeric_value(a)
    invest_data['invest_count'] = int(n)
    invest_data['invest_amount'] = decimal.Decimal(a)
    invest_data['own_code'] = own
    data = session['data']
    pc = data['pc']
    game_ID = pc['game_ID']
    bnkr = banker()
    inv_amt = bnkr.calc_roi(invest_data['invest_amount'], game_ID)
    invest_data['invest_value'] = inv_amt
    print("INVEST DATA= ", invest_data)
    return invest_data

def render_tp_options():
    options = []
    ctgy = ['STOCKS', 'PROPERTY', 'BUSINESS']
    type = ['STCK', 'PPTY', 'BUS']
    desc, invest = build_tp_options()

    o = Options(ctgy=ctgy, type=type, desc=desc, invest=invest)

    options = o.get_options()

    return options

def build_tp_options():
    desc = []
    invest = []
    # Stock Offer
    stocks = ["oNg", "robotics", "gold", "paper", "utility", "auto", "airline"]
    count = [100, 50, 10, 25]
    sc = random.choice(stocks)
    cc = random.choice(count)
    pi_stck = PriceIndex("stocks")
    pos = pi_stck.get_new_position()
    row1 = pi_stck.get_new_row()
    row1['sc'] = sc
    row1['cc'] = cc
    session['bs'] = row1
    value = row1[sc]
    sc = sc.capitalize()
    desc.append(sc + " Stocks Count=" + str(cc))
    invest.append("$   " + str(value * cc))
    # Property Offer
    pi_ppty = PriceIndex("address")
    pos = pi_ppty.get_new_position()
    row2 = pi_ppty.get_new_row()
    session['bp'] = row2
    b_type = row2['BLDG_type']
    p_type = row2['PPTY_type']
    desc.append(b_type + " for " + p_type)
    price = round(row2['Price'], 0)
    invest.append("$  " + str(price))
    # Business Offer
    pi_bus = PriceIndex("business")
    pos = pi_bus.get_new_position()
    row3 = pi_bus.get_new_row()
    session['bb'] = row3
    desc.append(row3['business'])
    invest.append("$  " + str(row3['buy']))
    print("TP OPT SESSION 1: ", session)
    data = session['data']
    pc = data['pc']
    game_ID = pc['game_ID']
    stat, result = db.get_game_card(game_ID)
    data['gc'] = result
    session['data'] = data
    print("TP OPT SESSION 2: ", session)

    return desc, invest

def render_tpsale_options(data):
    user = session['user']
    options = session['options']
    bnkr = banker()
    ctgy = ['MESSAGE', 'SALE ITEM 1', 'TOTAL COST 1', 'SALE ITEM 2', 'TOTAL COST 2', 'SALE ITEM 3',
            'TOTAL COST 3', 'TOTAL EXPENSE']
    desc = ['Your purchase is complete.  This is a cash sale from your cash-on-hand.']

    desc.append('STOCK PURCHASE')
    desc.append(options[3]['opt_desc'])

    desc.append('PROPERTY PURCHASE')
    desc.append(options[7]['opt_desc'])

    desc.append('BUSINESS PURCHASE')
    desc.append(options[10]['opt_desc'])

    stck_amt = extract_numeric_value(options[3]['opt_desc'])
    ppty_amt = extract_numeric_value(options[7]['opt_desc'])
    bus_amt = extract_numeric_value(options[10]['opt_desc'])
    te = int(stck_amt + ppty_amt + bus_amt)
    desc.append("$  " + str(te))
    stat = bnkr.assess_purchase_power(user, desc[len(desc) - 1])
    rnge = 8
    session['buying_power'] = stat
    if stat == "LOAN":
        rnge = 9
        ctgy.append("Purchase Power Status")
        desc.append(
            "The banker was able to qualify you for a loan to purchase. The loan was added to your cash on hand.")
    elif stat == "NO":
        rnge = 9
        ctgy.append("Purchase Power Status")
        desc.append("The banker was not able to qualify you for a loan to purchase. No purchase made for you.")

    o = Options(ctgy=ctgy, type=None, desc=desc, invest=None)

    options = o.get_options()

    dataopt = {
        'data': data,
        'user': user,
        'options': options
    }
    print("TPSale Options DATAOPT = ", dataopt)
    print("Session Dictionary: ", session)
    if stat != "NO":
        update_tp_player_game(dataopt)
    return dataopt

def update_tp_player_game(dataopt):
    """
    update the game table (gc dictionary)
    -> Spending and Expenditure adjustments
    -> Update counts
    ->
    update the player's table (pc and options dictionary)
    -> Cash-on-Hand adjustments
    -> Product count adjustments
    -> Investment table insert(s)
    """
    invest_data = {
        'invest_type': " ",
        'invest_count': 0,
        'invest_amount': 0.00,
        'invest_description': " ",
        'player_number': 0,
        'invest_value': 0.00
    }
    total_amount = 0
    # Unload data dictionary from the dataopt nested dictionary
    data1 = dataopt['data']

    # Unload options dictionary from dataopt nested dictionary
    options1 = dataopt['options']
    # Unload data dictionary from the sessions nested dictionary
    data2 = session['data']
    # Unload game card from the data nested dictionary
    gc = data2['gc']
    # Unload options from the session nested dictionary
    options2 = session['options']
    product_data = session['bs']
    invest_card = build_invest_card(invest_data, product_data['sc'], options2[2]['opt_desc'], options2[3]['opt_desc'])
    invest_card['invest_type'] = "STCK"
    print("DATA1: ", data1)
    print("DATAOPT= ", dataopt)
    print("INVEST CARD: ", invest_card)
    print(invest_card['player_number'])
    print(data1['player_number'])
    invest_card['player_number'] = data1['player_number']
    total_amount = total_amount + invest_card['invest_amount']
    status = db.insert_investments_from_sale(invest_card)
    data1['buy_type'] = "bs"
    data1['user'] = session['user']
    status = db.update_game_player(invest_card['invest_amount'], gc, data1)
    if status == "OK":
        flash("Good STCK investment!", "success")
    product_data = session['bp']
    invest_card = build_invest_card(invest_data, product_data['Property'], "1", options2[7]['opt_desc'])
    invest_card['invest_type'] = "PPTY"
    total_amount = total_amount + invest_card['invest_amount']
    status = db.insert_investments_from_sale(invest_card)
    data1['buy_type'] = "bp"
    status = db.update_game_player(invest_card['invest_amount'], gc, data1)
    if status == "OK":
        flash("Good PPTY investment! Real estate is valuable.", "success")
    product_data = session['bb']
    invest_card = build_invest_card(invest_data, product_data['business'], "1", options2[10]['opt_desc'])
    invest_card['invest_type'] = "BUS"
    total_amount = total_amount + invest_card['invest_amount']
    status = db.insert_investments_from_sale(invest_card)
    data1['buy_type'] = "bb"
    status = db.update_game_player(invest_card['invest_amount'], gc, data1)
    if status == "OK":
        flash("Good Business investment! You are in business.", "success")


def render_gb_options(game_ID):
    status, players = db.get_players_game_card(game_ID, allcolumn="Y")
    print("Player Cards= ", players)
    options = []
    plyr = []
    cash = []
    prop = []
    stck = []
    busc = []
    y = 0
    for player in players:
        plyr.append(str(player['player_number']))
        cash.append("$  " + str(player['cash_on_hand']))
        prop.append("$  " + str(player['property_value']))
        stck.append("$  " + str(player['stock_value']))
        busc.append("$  " + str(player['business_value']))
        y += 1

    i = 0
    d = {}
    for i in range(y):
        d['opt_plyr'] = plyr[i]
        d['opt_cash'] = cash[i]
        d['opt_prop'] = prop[i]
        d['opt_stck'] = stck[i]
        d['opt_busc'] = busc[i]
        options.append(d)
        d = {}

    return options

def render_pb_options():
    options = []
    data = {'player_number' : '   0   ',
            'PPTY' : '   0   ',
            'STCK' : '   0   ',
            'BUS' : '   0   ',
            'COMM' : '   0   ',
            'OTHR' : '   0   '
            }
    # Get investment counts
    status, results = db.get_player_investment_stats(session['player_number'])
    print("Investment Stats", results)
    if status == "OK":
        data['player_number'] = session['player_number']
        rnge = len(results)
        for i in range(rnge):
            if results[i]['invest_type'] == "BUSC":
                data['BUS'] = "  " + str(results[i]['inv_cnt']) + "  "
            else:
                data[results[i]['invest_type']] = "  " + str(results[i]['inv_cnt']) + "  "
    else:
        flash("DB error. Investments table read error.", "error")
    # Get player card data to display other game statistics
    result2, q = db.get_player_record(session['user'])
    if q>0:
        data['money'] = "$  " + str(result2['cash_on_hand'])
        data['salary'] = "$  " + str(result2['salary'])
        data['job_level'] = "   " + str(result2['job_level'])
        data['degree_level'] = "   " + str(result2['degree_level'])

        data['property_value'] = "$  " + str(result2['property_value'])
        data['stock_value'] = "$  " + str(result2['stock_value'])
        data['business_value'] = "$  " + str(result2['business_value'])
        data['commodity_value'] = "$  " + str(result2['commodity_value'])
        data['other_investments'] = "$  " + str(result2['other_investments'])
    else:
        flash("DB error. Players table read error.", "error")

    status, investments = db.get_player_investment_history(session['player_number'])
    if status == "OK":
        print("Investments", investments)
        print("Investments row count: ", len(investments))
        d = {}
        options = []
        rev_types = ["ALL"]
        options = create_options_list(investments, rev_types, options)

    else:
        flash("DB error. Players table read error.", "error")

    return options, data

def render_preview_options(rev_type):
    options = []
    data = {'player_number' : '   0   ',
            'PPTY' : '   0   ',
            'STCK' : '   0   ',
            'BUS' : '   0   ',
            'COMM' : '   0   ',
            'OTHR' : '   0   '
            }
    # Get investment counts
    status, results = db.get_player_investment_stats(session['player_number'])
    print("Investment Stats", results)
    if status == "OK":
        data['player_number'] = session['player_number']
        rnge = len(results)
        for i in range(rnge):
            if results[i]['invest_type'] == "BUSC":
                data['BUS'] = "  " + str(results[i]['inv_cnt']) + "  "
            else:
                data[results[i]['invest_type']] = "  " + str(results[i]['inv_cnt']) + "  "
    else:
        flash("DB error. Investments table read error.", "error")

    status, investments = db.get_player_investment_history(session['player_number'])

    if status == "OK":
        print("Investments", investments)
        print("Investments row count: ", len(investments))

        options = []
        rev_types = []
        rev_types.append(rev_type)
        if rev_type == "RENT":
            rev_types.append("ROI")
        elif rev_type == "LOAN":
            rev_types.append("BILL")
        options = create_options_list(investments, rev_types, options)
        print("Investment option Detail: ", options)
    else:
        flash("DB error. Players table read error.", "error")

    return options, data

def create_options_list(investments, rev_types, options):
    d = {}
    for item in investments:
        if item['invest_type'] in rev_types or 'ALL' in rev_types:
            d = {
                'opt_type': item['invest_type'],
                'opt_count': str(item['invest_count']),
                'opt_desc': item['invest_description'],
                'opt_amt': str(item['invest_amount']),
                'opt_val': str(item['invest_value']),
                'opt_own': str(item['own_code'])
            }
            options.append(d)
    print("Investment option list detail: ", options)
    return options


def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def unflatten_dict(d, sep='_'):
    result_dict = {}
    for key, value in d.items():
        parts = key.split(sep)
        d = result_dict
        for part in parts[:-1]:
            if part not in d:
                d[part] = {}
            d = d[part]
        d[parts[-1]] = value
    return result_dict