from ts_database import *
from ts_game import *
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from datetime import datetime, date
from wtforms import Form
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
    data = session['data']
    if 'data' in locals():
            pass
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
            gc = GameBoard(game_id)
            ga = Game_Action()
            data['gc'] = gc.get_game_data()
            data['ga'] = ga.get_action_items()
            print("GC ", data['gc'])
            print("GA ", data['ga'])
        else:
            # Set indexes
            ga = Game_Action()
            data['ga'] = ga.get_action_items()
            print("GA ", data['ga'])
        return data

    except Exception as e:
        return f"An error occurred in render game card build: {e}"

def process_end_of_round(session):
    """
        # Reset Stock Index
        # Check the round for Salary Pay every 3rd round
        salary + (salary * degree_level * 0.5) + (salary * job_level * 0.7
        # Check for 10th round to collect taxes
        COH = COH - (COH * 0.01)
        # Check every 5th round to collect insurance
        COH = COH - (PPTY VALUE * 0.01)
        # Population growth, total spending and earnings

    """
    data = session.get('data')
    gc = data['gc']
    game_id = gc['game_ID']
    gb = GameBoard(game_id)
    # Population growth, GDP & CPI management
    gb.update_gdp()
    gb.update_population()
    gb.update_cpi()
    gc = gb.get_game_data()
    gc.update(session['gc'])
    status = gb.put_game_data(gc)
    if status == "OK":
        data['gc'] = gc
        session['data'] = data
    # Rest Stock Index and Position pointer
    g = Game_Action()
    ga = g.get_action_items()
    data['ga'] = ga
    session['data'] = data
    # Get the player cards for update
    # Salary Pay
    if data['player_round'] % 3 == 0:
        # Pay salaries to players
        pass
    if data['player_round'] % 5 == 0:
        # Assess Insurance
        pass
    if data['player_round'] % 10 == 0:
        # Assess Taxes
        pass

    return status



def render_player_card(players, player_number):
    # Process Players card
    for player in players:
        if player['player_number'] == player_number:
            return player

def render_edit_profile(form, result):
    form.name.data = result['name']
    form.email.data = result['Email']
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
    form.glevel.data = "EASY"
    form.ggoal.data = "MA"
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
    return form

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
    # Stock Offer
    stocks = ["oNg", "robotics", "gold", "paper", "utility", "auto", "airline"]
    comm = ["Mutual", "Diamonds", "Grain", "Security", "Silver", "Certificates", "Money"]
    count = [100, 50, 10, 25]
    sc = random.choice(stocks)
    cc = random.choice(count)
    pi_stck = PriceIndex("stocks")
    row = pi_stck.get_starting_position()
    row1 = pi_stck.get_new_position()
    row1['sc'] = sc
    row1['cc'] = cc
    session['bs'] = row1
    value = row1[sc]
    sc = sc.capitalize()
    desc.append(sc + " Stocks Count=" + str(cc))
    invest.append("$   " + str(value * cc))
    # Property Offer
    pi_ppty = PriceIndex("address")
    row2 = pi_ppty.get_new_position()
    session['bp'] = row2
    b_type = row2['BLDG_type']
    p_type = row2['PPTY_type']
    desc.append(b_type + " for " + p_type)
    price = round(row2['Price'], 0)
    invest.append("$  " + str(price))
    # Business Offer
    pi_bus = PriceIndex("business")
    row3 = pi_bus.get_new_position()
    session['bb'] = row3
    desc.append(row3['business'])
    invest.append("$  " + str(row3['buy']))
    # Commodity Offer
    pi_comm = PriceIndex("commodities")
    commc = random.choice(comm)
    row4 = pi_comm.get_new_position()
    row4['commc'] = commc
    cc = random.choice(count)
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

def render_bs_options(session):
    options = []
    ctgy = ['MESSAGE', 'SALES OFFER', 'COST PER SHARE', 'SHARE COUNT', 'TOTAL COST']
    desc = ['This stock is available for your purchase at the current cost per share.  '
            'Remember, a refusal can cost you a consulting fee.)'
            ]
    # Build BS Options Data
    bs = session['bs']
    sc_name = bs['sc']
    desc.append(bs['sc'].capitalize() + " Stock")
    cps = bs[sc_name]
    desc.append("$  " + str(cps))  # Cost per Share
    cnt = bs['cc']
    desc.append(str(cnt) + " Share(s)")
    tc = int(cnt) * int(cps)
    desc.append("$  " + str(tc))

    d = {}
    i = 0
    for i in range(5):
        d['opt_ctgy'] = ctgy[i]
        d['opt_desc'] = desc[i]
        options.append(d)
        d = {}

    return options

def render_bp_options(session):
    options = []
    ctgy = ['MESSAGE', 'SALES OFFER', 'PROPERTY TYPE', 'ASKING PRICE', 'FEES', 'TOTAL COST']
    desc = ['Here is an opportunity for you to accept or refuse a property for sale. '
            'Remember, a refusal can cost you a consulting fee.)'
            ]
    bp = session['bp']
    desc.append(bp['Property'])
    type = bp['BLDG_type'] + " for " + bp['PPTY_type']
    desc.append(type)
    price = bp['Price']
    desc.append("  $  " + str(price))
    calc = float(price) * 0.06
    fees = int(round(calc, 2))
    desc.append("  $  " + str(fees))
    tc = int(float(bp['Price'])) + int(fees)
    desc.append("  $  " + str(tc))

    d = {}
    i = 0
    for i in range(6):
        d['opt_ctgy'] = ctgy[i]
        d['opt_desc'] = desc[i]
        options.append(d)
        d = {}

    return options

def render_bb_options(session):
    options = []
    ctgy = ['MESSAGE', 'BUSINESS NAME', 'SALE PRICE', 'PARTNERSHIP', 'CLUB PRICE', 'RENT/TICKET VALUE']
    desc = ['Here is an opportunity for you. Consider this business for sale. '
            'Remember, a refusal can cost you a consulting fee.)'
           ]
    bb = session['bb']
    desc.append(bb['business'])
    desc.append('$  ' + str(bb['buy']))
    desc.append('$  ' + str(bb['partner']))
    desc.append('$  ' + str(bb['club']))
    desc.append('$  ' + str(bb['value']))


    d = {}
    i = 0
    for i in range(6):
        d['opt_ctgy'] = ctgy[i]
        d['opt_desc'] = desc[i]
        options.append(d)
        d = {}

    return options

def render_bc_options(session):
    options = []
    ctgy = ['MESSAGE', 'SALE OFFER', 'COST PER SHARE', 'SHARE COUNT', 'TOTAL COST']
    desc = ['This commodity is available for your purchase at the current cost per share.  '
            ]
    # Build BC Options Data
    bc = session['bc']
    cc_name = bc['cc']
    desc.append(bc['commc'] + " Stock")
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


    d = {}
    i = 0
    for i in range(5):
        d['opt_ctgy'] = ctgy[i]
        d['opt_desc'] = desc[i]
        options.append(d)
        d = {}

    return options

def render_sale_options(data):
    user = session['user']
    options = session['options']
    ctgy = ['MESSAGE', 'TRANSACTION', 'TOTAL COST']
    desc = ['Your purchase is complete.  This is a cash sale from your cash-on-hand.']
    if data['buy_type'] == "bs":
        desc.append('STOCK PURCHASE')
        desc.append(options[0]['opt_invest'])
    if data['buy_type'] == "bp":
        desc.append('PROPERTY PURCHASE')
        desc.append(options[1]['opt_invest'])
    if data['buy_type'] == "bb":
        desc.append('BUSINESS PURCHASE')
        desc.append(options[2]['opt_invest'])
    if data['buy_type'] == "bc":
        desc.append('COMMODITY PURCHASE')
        desc.append(options[3]['opt_invest'])

    d = {}
    i = 0
    options = []
    for i in range(3):
        d['opt_ctgy'] = ctgy[i]
        d['opt_desc'] = desc[i]
        options.append(d)
        d = {}
    dataopt = {
        'data': data,
        'user': user,
        'options': options
    }
    print("Sale Options DATAOPT = ", dataopt)
    print("Session Dictionary: ", session)
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
    buy_type = data1['buy_type']
    # Unload options dictionary from dataopt nested dictionary
    options1 = dataopt['options']
    # Unload product type from the sessions nested dictionary
    product_data = session[buy_type]
    # Unload data dictionary from the sessions nested dictionary
    data2 = session['data']
    # Unload game card from the data nested dictionary
    gc = data2['gc']
    # Unload options from the session nested dictionary
    options2 = session['options']
    invest_data['player_number'] = data1['player_number']
    if buy_type == "bs":
        invest_card = build_invest_card(invest_data, product_data['sc'], options2[0]['opt_desc'], options2[0]['opt_invest'])
        invest_card['invest_type'] = "STCK"
    if buy_type == "bp":
        invest_card = build_invest_card(invest_data, product_data['Property'], options2[1]['opt_desc'], options2[1]['opt_invest'])
        invest_card['invest_type'] = "PPTY"
    if buy_type == "bb":
        invest_card = build_invest_card(invest_data, product_data['business'], options2[2]['opt_desc'], options2[2]['opt_invest'])
        invest_card['invest_type'] = "BUS"
    if buy_type == "bc":
        invest_card = build_invest_card(invest_data, product_data['commc'], options2[3]['opt_desc'], options2[3]['opt_invest'])
        invest_card['invest_type'] = "COMM"

    status = db.insert_investments_from_sale(invest_card)
    if status == "OK":
        flash("Investment saved successfully", "success")

    status = db.update_game_player(invest_card['invest_amount'], gc, dataopt)
    if status == "OK":
        flash("Game/Player saved successfully", "success")

def build_invest_card(invest_data, product, opt1, opt2):
    invest_data['invest_description'] = product
    n = opt1
    a = opt2
    invest_data['invest_count'] = int(re.sub(r'\D', '', n))
    invest_data['invest_amount'] = float(re.sub(r'\D', '', a))
    invest_data['invest_value'] = round(float(invest_data['invest_amount']) * 1.12, 0)
    print("INVEST DATA= ", invest_data)
    return invest_data

"""
    # Assigning each nested dictionary to a separate variable
        bb_dict = session_dict.get('bb', {})
        bc_dict = session_dict.get('bc', {})
        bp_dict = session_dict.get('bp', {})
        bs_dict = session_dict.get('bs', {})
        data_dict = session_dict.get('data', {})
        options_list = session_dict.get('options', [])
"""

def render_rp_options():
    options = []
    ctgy = ['MESSAGE', 'OPPORTUNITY', 'WANT', 'NEED']
    desc = ['Travel with your family of five to the resort. Spend a week',
            ' ',
            '$   4,800.00',
            ' '
            ]

    d = {}
    for i in range(4):
        d['opt_ctgy'] = ctgy[i]
        d['opt_desc'] = desc[i]
        options.append(d)
        d = {}
        if i == 0 or i==1 or i==2:
            d['opt_ctgy'] = " "
            d['opt_desc'] = " * "
            options.append(d)
            d = {}

    return options

def render_tp_options():
    options = []
    ctgy = ['STOCKS', 'PROPERTY', 'BUSINESS']
    type = ['STCK', 'PPTY', 'BUS']
    desc, invest = build_tp_options()

    d = {}
    for i in range(3):
        d['opt_ctgy'] = ctgy[i]
        d['opt_type'] = type[i]
        d['opt_desc'] = desc[i]
        d['opt_invest'] = invest[i]
        options.append(d)
        d = {}

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
    row = pi_stck.get_starting_position()
    row1 = pi_stck.get_new_position()
    row1['sc'] = sc
    row1['cc'] = cc
    session['bs'] = row1
    value = row1[sc]
    sc = sc.capitalize()
    desc.append(sc + " Stocks Count=" + str(cc))
    invest.append("$   " + str(value * cc))
    # Property Offer
    pi_ppty = PriceIndex("address")
    row2 = pi_ppty.get_new_position()
    session['bp'] = row2
    b_type = row2['BLDG_type']
    p_type = row2['PPTY_type']
    desc.append(b_type + " for " + p_type)
    price = round(row2['Price'], 0)
    invest.append("$  " + str(price))
    # Business Offer
    pi_bus = PriceIndex("business")
    row3 = pi_bus.get_new_position()
    session['bb'] = row3
    desc.append(row3['business'])
    invest.append("$  " + str(row3['buy']))

    return desc, invest

def render_tpsale_options(data):
    user = session['user']
    options = session['options']
    ctgy = ['MESSAGE', 'ITEM 1', 'TOTAL COST 1', 'ITEM 2', 'TOTAL COST 2', 'ITEM 3', 'TOTAL COST 3']
    desc = ['Your purchase is complete.  This is a cash sale from your cash-on-hand.']

    desc.append('STOCK PURCHASE')
    desc.append(options[0]['opt_invest'])

    desc.append('PROPERTY PURCHASE')
    desc.append(options[1]['opt_invest'])

    desc.append('BUSINESS PURCHASE')
    desc.append(options[2]['opt_invest'])

    d = {}
    i = 0
    options = []
    for i in range(7):
        d['opt_ctgy'] = ctgy[i]
        d['opt_desc'] = desc[i]
        options.append(d)
        d = {}
    dataopt = {
        'data': data,
        'user': user,
        'options': options
    }
    print("TPSale Options DATAOPT = ", dataopt)
    print("Session Dictionary: ", session)
    #update_tp_player_game(dataopt)
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
    buy_type = data1['buy_type']
    # Unload options dictionary from dataopt nested dictionary
    options1 = dataopt['options']
    # Unload product type from the sessions nested dictionary
    product_data = session[buy_type]
    # Unload data dictionary from the sessions nested dictionary
    data2 = session['data']
    # Unload game card from the data nested dictionary
    gc = data2['gc']
    # Unload options from the session nested dictionary
    options2 = session['options']
    product_data = session['bs']
    invest_card = build_invest_card(invest_data, product_data['sc'], options2[0]['opt_desc'], options2[0]['opt_invest'])
    invest_card['invest_type'] = "STCK"
    total_amount = total_amount + invest_card['invest_amount']
    status = db.insert_investments_from_sale(invest_card)
    product_data = session['bp']
    invest_card = build_invest_card(invest_data, product_data['Property'], options2[1]['opt_desc'], options2[1]['opt_invest'])
    invest_card['invest_type'] = "PPTY"
    total_amount = total_amount + invest_card['invest_amount']
    status = db.insert_investments_from_sale(invest_card)
    product_data = session['bb']
    invest_card = build_invest_card(invest_data, product_data['business'], options2[2]['opt_desc'], options2[2]['opt_invest'])
    invest_card['invest_type'] = "BUS"
    total_amount = total_amount + invest_card['invest_amount']
    status = db.insert_investments_from_sale(invest_card)
    data1['buy_type'] = "spb"
    if status == "OK":
        flash("Investment saved successfully", "success")

    status = db.update_game_player(total_amount, gc, data1)
    if status == "OK":
        flash("Game/Player saved successfully", "success")


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
    data = {}
    data['money'] = "$  12,500"
    data['property'] = "   5   "
    data['stock'] = "   1,000   "
    data['busc'] = "   3    "

    type = ['PPTY', 'STCK', 'BUS', 'WANT']
    desc = ['Personal House', 'Airline   (Count=100)', 'Partnership (Wally Mart)', 'Diamond Necklace']
    inv = ['$  100,000',
           '$    1,000',
           '$   50,000',
           '$    2,000'
            ]
    val = ['$  110,000',
            '$    2,000',
            '$   70,000',
            '$    5,000'
            ]

    d = {}
    for i in range(4):
        d['opt_type'] = type[i]
        d['opt_desc'] = desc[i]
        d['opt_inv'] = inv[i]
        d['opt_val'] = val[i]
        options.append(d)
        d = {}

    return options, data

def extract_numeric_value(value_str):
    # Find all digits (including those that might be part of a decimal number)
    match = re.search(r'[\d.]+', value_str)
    if match:
        return int(match.group())  # or float(match.group()) if you are sure it is an integer
    return None  # or handle the case where no number is found

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