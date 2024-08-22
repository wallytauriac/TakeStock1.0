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
        else:
            # Set indexes
            ga = Game_Action()
            data['ga'] = ga.get_action_items()
        return data

    except Exception as e:
        return f"An error occurred in render game card build: {e}"

def process_end_of_round(session):
    """
        # Reset Stock Index
        # Check the round for Salary Pay every 3rd round
        # Check for 10th round to collect taxes
        # Check every 5th round to collect insurance
        # Population growth, total spending and earnings

    """
    data = session.get('data')
    ga = session.get('ga')
    gc = session.get('gc')
    print("Data=>", data)
    print("GA=>", ga)
    print("GC=>", gc)

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

def render_game_settings(form, result):
    form.status.data = result['status']
    form.player_count.data = result['player_count']
    form.start_date.data = date.today()
    form.game_ID.data = "TS" + date.today().strftime("YYYY-MM-DD")
    form.population.data = 500000
    form.pop_chg = 0.06
    form.glevel.data = result['game_level']
    form.ggoal.data = result['game_goal']
    return form

def render_sp_options():
    options = []
    ctgy = ['STOCKS', 'PROPERTY', 'BUSINESS', 'COMMODITY']
    type = ['STCK', 'PPTY', 'BUS', 'COMM']
    desc = ['Airline   (Count=100)',
            'Personal House',
            'Partnership (Wally Mart)',
            'Diamond Necklace'
            ]
    invest = ['$    100',
              '$100,000',
              '$ 50,000',
              '$  2,000']
    d = {}
    for i in range(4):
        d['opt_ctgy'] = ctgy[i]
        d['opt_type'] = type[i]
        d['opt_desc'] = desc[i]
        d['opt_invest'] = invest[i]
        options.append(d)
        d = {}
        if i == 0 or i==1 or i==2:
            d['opt_ctgy'] = " "
            d['opt_type'] = " * "
            d['opt_desc'] = " * "
            d['opt_invest'] = " * "
            options.append(d)
            d = {}

    return options

def render_bs_options():
    options = []
    ctgy = ['MESSAGE', 'COST PER SHARE', 'SHARE COUNT', 'TOTAL COST']
    desc = ['This stock is available for your purchase at the current cost per share.  '
            'Remember, a refusal can cost you a consulting fee.)',
            '$     100',
            '#     100',
            '$  10,000'
            ]
    d = {}
    i = 0
    for i in range(4):
        d['opt_ctgy'] = ctgy[i]
        d['opt_desc'] = desc[i]
        options.append(d)
        d = {}

    return options

def render_bp_options():
    options = []
    ctgy = ['MESSAGE', 'PROPERTY TYPE', 'ASKING PRICE', 'FEES', 'TOTAL COST']
    desc = ['Here is an opportunity for you to accept or refuse a property for sale. '
            'Remember, a refusal can cost you a consulting fee.)',
            'House',
            '$ 100,000',
            '$   1,500',
            '$ 101,500'
            ]
    d = {}
    i = 0
    for i in range(5):
        d['opt_ctgy'] = ctgy[i]
        d['opt_desc'] = desc[i]
        options.append(d)
        d = {}

    return options

def render_bb_options():
    options = []
    ctgy = ['MESSAGE', 'BUSINESS TYPE', 'SALE PRICE', 'PARTNERSHIP', 'CLUB PRICE', 'RENT/TICKET VALUE']
    desc = ['Here is an opportunity for you. Consider this business for sale. '
            'Remember, a refusal can cost you a consulting fee.)',
            'Entertainment',
            '$  70,000',
            '$  35,000',
            '$   7,000',
            '$     100'
            ]
    d = {}
    i = 0
    for i in range(6):
        d['opt_ctgy'] = ctgy[i]
        d['opt_desc'] = desc[i]
        options.append(d)
        d = {}

    return options

def render_bc_options():
    options = []
    ctgy = ['MESSAGE', 'COST PER SHARE', 'SHARE COUNT', 'TOTAL COST']
    desc = ['This commodity is available for your purchase at the current cost per share.  '
            'Remember, a refusal can cost you a consulting fee.)',
            '$     100',
            '#     100',
            '$  10,000'
            ]
    d = {}
    i = 0
    for i in range(4):
        d['opt_ctgy'] = ctgy[i]
        d['opt_desc'] = desc[i]
        options.append(d)
        d = {}

    return options

def render_sale_options(data, options):
    user = session['user']
    ctgy = ['MESSAGE', 'PRODUCT TYPE', 'SHARE COUNT', 'TOTAL COST']
    desc = ['Your purchase is complete.  This is a cash sale from your cash-on-hand.']
    if data['buy_type'] == "bs" or data['buy_type'] == "bc":
        if data['buy_type'] == "bp":
            desc.append('PROPERTY PURCHASE')
            rnge = 2
        else:
            rnge = 3
            if data['buy_type'] == "bs":
                desc.append('STOCK PURCHASE')
            else:
                desc.append('COMMODITY PURCHASE')
        for option in options:
            if option['opt_ctgy'] == "TOTAL COST":
                desc.append(option['opt_desc'])
            if option['opt_ctgy'] == "SHARE COUNT":
                desc.append(option['opt_desc'])
    elif data['buy_type'] == "bp":
        rnge = 2
        desc.append('STOCK PURCHASE')
        for option in options:
            if option['opt_ctgy'] == "TOTAL COST":
                desc.append(option['opt_desc'])
    d = {}
    i = 0
    options = []
    for i in range(rnge):
        d['opt_ctgy'] = ctgy[i]
        d['opt_desc'] = desc[i]
        options.append(d)
        d = {}
    dataopt = {
        'data': data,
        'user': user,
        'options': options
    }
    return dataopt


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
    desc = ['Airline   (Count=100)',
            'Personal House',
            'Partnership (Wally Mart)'
            ]
    invest = ['$    100',
              '$100,000',
              '$ 50,000'
            ]
    d = {}
    for i in range(3):
        d['opt_ctgy'] = ctgy[i]
        d['opt_type'] = type[i]
        d['opt_desc'] = desc[i]
        d['opt_invest'] = invest[i]
        options.append(d)
        d = {}
        if i == 0 or i==1:
            d['opt_ctgy'] = " "
            d['opt_type'] = " * "
            d['opt_desc'] = " * "
            d['opt_invest'] = " * "
            options.append(d)
            d = {}

    return options

def render_gb_options():
    options = []
    plyr = [' 1 ', ' 2 ', ' 3 ']
    cash = ['$ 12,500', '$ 18,500', '$121,000']
    prop = ['$   50,000',
            '$   50,000',
            '$   50,000'
            ]
    stck = ['   1,000',
              '   1,000',
              '   1,000'
            ]
    busc = ['   3',
            '   2',
            '   1'
            ]
    d = {}
    for i in range(3):
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