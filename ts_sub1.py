import decimal
from random import randint
import json
from flask import Flask, Blueprint, render_template, redirect, url_for, session
from ts_validation import *
from ts_page import *
from ts_page2 import *
from ts_game import *
from ts_events import *
from ts_database import *
import pandas as pd
from flask_mysqldb import MySQL
from app_factory import create_app, mysql
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField
from functools import wraps
from icecream import ic


ts_sub1_bp = Blueprint('ts_sub1_bp', __name__, template_folder="templates")
db = DB_Mgr(mysql)

def is_logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('You need to be logged in to view this page', 'error')
            return redirect(url_for('login'))  # Ensure 'login' route is defined in ts_main.py
        return f(*args, **kwargs)
    return decorated_function

@ts_sub1_bp.route('/game_pass', methods=['GET', 'POST'])
@is_logged_in
def game_pass():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))  # Ensure 'login' route is defined in ts_main.py
    return gamePass(username)

@ts_sub1_bp.route('/gamepass/<username>', methods=['GET', 'POST'])
@is_logged_in
def gamePass(username):
    page_name = "Game Action Page"
    if username != session.get('username'):
        flash('You aren\'t authorised to view this page', 'error')
        return redirect(url_for('login'))  # Ensure 'login' route is defined in ts_main.py
    if session.get('role') != "Host":
        flash('You aren\'t authorised to access this page', 'error')
        return redirect(url_for('login'))  # Ensure 'login' route is defined in ts_main.py
    print_data(session=session)
    pn = session.get('player_number')
    pc = session.get('player_count')
    print(f"passed data: {pn} and {pc}")
    if 'data' in session:
        data = session.get('data')
        gac = Game_Action()
        ga = gac.get_action_items()
        data['ga'] = ga
        data['ga']['position_id'] = gac.get_new_position()
        session['data'] = data
    else:
        data = {}
    if str(pn) < str(pc):
        session['player_move'] += 1
        # ******************************************
        # First Play
        # ******************************************
        if session['player_move'] == 1:
            #  Check for BILL investment cards
            #  Generate BILL investment cards
            plyr = Players(username)
            game_ID = plyr.game_ID
            gb = GameBoard(game_ID)
            status = gb.get_status()
            if status != "Ready":
                flash("The game status must be Ready or Active to start the game.", "danger")
                return redirect(url_for('game_dash'))
            session['player_round'] = 1
            stat = process_first_move(session['game_ID'], data)
            if stat == "NOK":
                raise Exception("Process First Move failed...")

        session['player_number'] += 1
        # ******************************************
        # End of Play
        # ******************************************
    elif str(pn) == str(pc) and str(pc) > '1':
        session['player_move'] += 1
        session['player_round'] += 1
        # ******************************************
        # End of Round actions
        # ******************************************
        # Reset Stock Index
        # Check the round for Salary Pay every 3rd round
        # Check for 10th round to collect taxes
        # Check every 5th round to collect insurance
        # Population growth, total spending and earnings
        status = process_end_of_round(session)
        session['player_number'] = 1
    db.pickle_save(session['game_ID'], "session", session, "cookie")
    event_number = randint(1, 50)
    return gameAction(username)

@ts_sub1_bp.route('/game_action', methods=['GET', 'POST'])
@is_logged_in
def game_action():
    # Retrieve the username from the session
    username = session.get('username')
    if not username:
        # Handle the case where the username is not in the session
        return redirect(url_for('login'))
    return gameAction(username)

@ts_sub1_bp.route('/gameAction/<username>', methods=['GET', 'POST'])
@is_logged_in
def gameAction(username):
    page_name = "Game Action"
    # form = GameActionForm(request.form)
    # print("Player Number: ", session['player_number'])
    data = {
        'player_number': 0,
        'player_move': 0,
        'player_round': 0,
        'message1': "single play message",
        'message2': "random play message",
        'message3': "triple play message"
    }
    user = None
    glevel = session['glevel']
    ggoal = session['ggoal']
    result, q = db.get_player_record(username)
    inh = 0.00
    if q>0:
        status, players = db.get_players_game_card(result["game_ID"], allcolumn="Y")
        print("Action Players: ", players)
        session['game_ID'] = result["game_ID"]
        data['player_number'] = session['player_number']
        for player in players:
            if player['player_number'] == session['player_number']:
                cash = player['cash_on_hand']
                if float(cash) <= float(0.00):
                    bnkr = banker()
                    sal = bnkr.calc_salary()
                    player['salary'] = sal
                    inh = bnkr.calc_inheritance()
                    player['cash_on_hand'] = inh
                    stat = db.update_player2(player)
        if status == "OK":
            gc = GameBoard(result["game_ID"])
            game_card = gc.get_game_data()
            game_card['total_earnings'] += decimal.Decimal(inh)
            if decimal.Decimal(inh) != decimal.Decimal(0):
                stat = gc.put_game_data(game_card)

            data = render_game_card(session, result["game_ID"])
            print("Game card: ", data)
            print("Game Action Session: ", session)
            pc = render_player_card(players, session['player_number'])
            print("Player card: ", pc)
            user = pc['username']
            session['user'] = pc['username']
            data['pc'] = pc
            data['gc'] = game_card
            session['data'] = data
        else:
            flash("Failed to retrieve player details", "error")
            return redirect(url_for('gameAction', data=data, page_name=page_name, user=user))
    db.pickle_save(session['game_ID'], "session", session, "cookie")
    print_data(data=data, session=session)
    gg = GameGoals()
    glevel_name = gg.get_level_name(glevel)
    ggoal_name = gg.get_goal_name(ggoal)
    flash(f"GAME SELECTIONS: Game Level is - {glevel_name} and Game Goal is - {ggoal_name}", "success")
    return render_template('gameAction.html', data=data, page_name=page_name, user=user)

@ts_sub1_bp.route('/game_s_play', methods=['GET', 'POST'])
# @is_logged_in
def game_SPlay():
    page_name = "Single Play Page"
    data = {}
    data['player_number'] = session.get('player_number')
    data['player_move'] = session.get('player_move')
    data['player_round'] = session.get('player_round')
    # Get the Single Play Generated Options to Display on the Single Play Page
    options = render_sp_options()
    session['options'] = options
    user = session['user']
    db.pickle_save("SinglePlay", "session", session, "cookie")
    return render_template('game_SPlay.html', data=data, page_name=page_name, options=options, user=user)


@ts_sub1_bp.route('/game_buyprod', methods=['GET', 'POST'])
def game_BuyProd():
    dataopt = {}  # Initialize dataopt early
    #print_data(session=session)

    if request.method == 'GET':
        # First Access: Handle `buy_type` from the URL parameter
        #form = GameBuyForm(request.args)
        buy_type = request.args.get('product')
        if not buy_type:
            return "Error: 'buy_type' is missing", 400  # Ensure buy_type is always provided

        # Populate `data` dictionary
        if "data" not in session:
            if 'player_number' in session:
                data = {
                    'player_number': session.get('player_number'),
                    'player_move': session.get('player_move'),
                    'player_round': session.get('player_round'),
                    'buy_type': buy_type
                }
        else:
            data = session['data']
            data['buy_type'] = buy_type
        if 'player_number' in data:
            print(f"Check DATA: {data}")
        # Determine which options to render based on buy_type
        options = []
        page_name = "Page "
        if buy_type == 'bs':
            page_name = "Buy Stock Page"
            options = render_bs_options(session)
        elif buy_type == 'bp':
            page_name = "Buy Property Page"
            options = render_bp_options(session)
        elif buy_type == 'bb':
            page_name = "Buy Business Page"
            options = render_bb_options(session)
        elif buy_type == 'bc':
            page_name = "Buy Commodity Page"
            options = render_bc_options(session)
        session['options'] = options
        print_data(options=options, session=session)
        user = session['user']
        db.pickle_save("SinglePlay", "session", session, "cookie")
        return render_template('game_BuyProd.html', data=data, user=user, page_name=page_name, options=options)

    elif request.method == 'POST':
        # Process the POST request
        print(f"SESSION at beginning of POST: {session}")
        data_json = request.form.get('data')
        options_json = request.form.get('options')

        # Log the received data
        print("Received data_json:", data_json)
        print("Received options_json:", options_json)

        # Ensure the JSON strings are properly formatted
        if not data_json or not options_json:
            return "Error: Missing data in POST request", 400

        try:
            print("Before loading data_json:", data_json)
            data = json.loads(data_json.replace("'", "\""))
            print("Before loading options_json:", options_json)
            options = json.loads(options_json.replace("'", "\""))
        except json.JSONDecodeError as e:
            return f"JSON decode error: {str(e)}", 400

        form = GameBuyForm(request.form)
        buy_type = request.form.get('buy_type')  # Ensure buy_type persists
        if buy_type == "bb":
            data['choice'] = form.choice.data
        data['buy_type'] = buy_type

        print("DATA:", data)
        print("OPTIONS:", options)
        session['options'] = options
        # Populate `dataopt` using the data from the POST request
        dataopt = render_sale_options(data)
        print("DATAOPT:", dataopt)

        page_name = "Product Sale Page"
        dataopt['page_name'] = page_name
        dataopt['errors'] = form.errors
        session['dataopt'] = dataopt
        db.pickle_save("SinglePlay", "session", session, "cookie")
        print_data(dataopt=dataopt, session=session)
        return render_template('game_Sale.html', **dataopt)

    #return render_template('game_BuyProd.html', data=data, user=user, page_name=page_name, options=options)

@ts_sub1_bp.route('/game_sale', methods=['GET', 'POST'])
# @is_logged_in
def game_Sale():
    product = request.args.get('product')
    username = session.get('username')
    flash("Another round of success!", "success")
    user = session['user']
    return gamePass(username)

@ts_sub1_bp.route('/game_r_play', methods=['GET', 'POST'])
# @is_logged_in
def game_RPlay():
    page_name = "Random Play Page"
    data = {}
    data['player_number'] = session.get('player_number')
    data['player_move'] = session.get('player_move')
    data['player_round'] = session.get('player_round')
    options = render_rp_options()
    user = session['user']
    session['options'] = options
    session['data'] = data
    db.pickle_save("RandomPlay", "session", session, "cookie")
    print_data(options=options, session=session, data=data)
    return render_template('game_RPlay.html', options=options, page_name=page_name, user=user, data=data)

@ts_sub1_bp.route('/game_rpbuy', methods=['GET', 'POST'])
# @is_logged_in
def game_RPBuy():
    page_name = "Random Buy Page"
    dataopt = {}  # Initialize dataopt early
    options = session['options']

    if request.method == 'GET':
        # Populate `data` dictionary
        data = {
            'player_number': session.get('player_number'),
            'player_move': session.get('player_move'),
            'player_round': session.get('player_round'),
        }
        user = session['user']
        return render_template('game_RPBuy.html', data=data, user=user, page_name=page_name, options=options)



@ts_sub1_bp.route('/game_rpsale', methods=['GET', 'POST'])
# @is_logged_in
def game_RPSale():
    page_name = "Random Sale Page"
    data = session['data']
    options = session['options']
    user = session['user']
    if request.method == 'GET':
        # Process the GET request
        # data_json = request.form.get('data')
        # options_json = request.form.get('options')
        # Ensure the JSON strings are properly formatted
        # data = json.loads(data_json.replace("'", "\""))
        # options = json.loads(options_json.replace("'", "\""))

        print_data(options=options, session=session, data=data)
        # Populate `dataopt` using the data from the POST request
        dataopt = render_rp_sale_options(data)
        data['INVITES'] = session['INVITES']
        session['cycle_round'] = 0
        data = dataopt['data']
        options = dataopt['options']
        session['dataopt'] = dataopt
        db.pickle_save("RandomPlay", "session", session, "cookie")
        print_data(dataopt=dataopt, session=session)
        return render_template('game_RPSale.html', page_name=page_name, options=options, data=data, user=user)

@ts_sub1_bp.route('/game_inplay', methods=['GET', 'POST'])
# @is_logged_in
def game_INPlay():
    page_name = "Invite Play Page"
    user = session['user']
    invites = session['INVITES']
    if session['glevel'] == "EP":
        flash("Invites not available for Easy Play", "error")
        return redirect(url_for('game_action'))
    data = {}
    data['player_number'] = session.get('player_number')
    data['player_move'] = session.get('player_move')
    data['player_round'] = session.get('player_round')
    options = render_inplay_options()
    user = session['user']
    data['cycle_round'] = session['cycle_round']
    session['options'] = options
    session['data'] = data
    db.pickle_save("RandomPlay", "session", session, "cookie")
    print_data(options=options, session=session)
    return render_template('game_INPlay.html', options=options, page_name=page_name, user=user, data=data)

@ts_sub1_bp.route('/game_inbuy', methods=['GET', 'POST'])
# @is_logged_in
def game_INBuy():
    page_name = "Random Sale Page"
    # This code manages the buy process for the random play rounds
    # Populate `data` dictionary
    data = session['data']
    options = session['options']
    user = session['user']
    options = render_insale_options()
    session['options'] = options
    db.pickle_save("RandomPlay", "session", session, "cookie")
    return render_template('game_INBuy.html', data=data, user=user, page_name=page_name, options=options)


@ts_sub1_bp.route('/game_insale', methods=['GET', 'POST'])
# @is_logged_in
def game_INSale():
    page_name = "Random Sale Page"

@ts_sub1_bp.route('/game_t_play', methods=['GET', 'POST'])
# @is_logged_in
def game_TPlay():
    if session['glevel'] == "EP":
        flash("Triple Play not available for Easy Play", "error")
        return redirect(url_for('ts_sub1_bp.game_action'))
    page_name = "Triple Play Page"
    data = {}
    data['player_number'] = session.get('player_number')
    data['player_move'] = session.get('player_move')
    data['player_round'] = session.get('player_round')
    options = render_tp_options()
    user = session['user']
    session['options'] = options
    db.pickle_save("RandomPlay", "session", session, "cookie")
    print_data(options=options, session=session)
    return render_template('game_TPlay.html', options=options, page_name=page_name, user=user, data=data)

@ts_sub1_bp.route('/game_tpbuy', methods=['GET', 'POST'])
def game_TPBuy():
    if request.method == 'GET':

        # Populate `data` dictionary
        data = {
            'player_number': session.get('player_number'),
            'player_move': session.get('player_move'),
            'player_round': session.get('player_round'),
        }
        # Determine which options to render based on buy_type

        options = render_bs_options(session, splay="N")
        session['options'] = options
        options = render_bp_options(session, pplay="N")
        session['options'] = options
        options = render_bb_options(session, bplay="N")
        session['options'] = options
        page_name = "Triple Sale Page"
        user = session['user']
        db.pickle_save("TriplePlay", "session", session, "cookie")
        return render_template('game_TPBuyProd.html', data=data, user=user, page_name=page_name, options=options)

    if request.method == 'POST':
        dataopt = {}  # Initialize dataopt early
        # Process the POST request
        data_json = request.form.get('data')
        options_json = request.form.get('options')
        # Ensure the JSON strings are properly formatted
        data = json.loads(data_json.replace("'", "\""))
        print("Options json: ", options_json)
        options = json.loads(options_json.replace("'", "\""))

        print("DATA: ", data)
        print("OPTIONS: ", options)
        # Populate `dataopt` using the data from the POST request
        dataopt = render_tpsale_options(data)
        print_data(dataopt=dataopt, session=session)
        page_name = "Triple Sale Page"
        dataopt['page_name'] = page_name
        session['dataopt'] = dataopt
        db.pickle_save("TriplePlay", "session", session, "cookie")
        return render_template('game_TPSale.html', **dataopt)


@ts_sub1_bp.route('/game_tpsale', methods=['GET', 'POST'])
# @is_logged_in
def game_TPSale():

    username = session.get('username')
    flash("Triple play success success!", "success")
    user = session['user']
    return gamePass(username)


@ts_sub1_bp.route('/game_g_board', methods=['GET', 'POST'])
# @is_logged_in
def game_GBoard():
    page_name = "Game Board Page"
    username = session['user']
    result, q = db.get_player_record(username)
    status, result2 = db.get_game_card(result["game_ID"])
    print("Game Card= ", result2)
    print_data(session=session)
    data = {}
    data['game_ID'] = result['game_ID']
    data['player_move'] = session.get('player_move')
    data['player_round'] = session.get('player_round')
    # get game table data to complete loading the data dictionary
    data['population'] = result2['population']
    data['pop_chg'] = result2['population_chg']
    data['total_spending'] = result2['total_spending']
    data['total_earnings'] = result2['total_earnings']
    data['user_captain'] = session.get('username')
    options = render_gb_options(data['game_ID'])
    print_data(data=data, options=options, session=session)
    return render_template('game_GBoard.html', options=options, page_name=page_name, data=data)

@ts_sub1_bp.route('/game_p_board', methods=['GET', 'POST'])
# @is_logged_in
def game_PBoard():
    page_name = "Player Board Page"

    options, data = render_pb_options()
    data['player_number'] = session.get('player_number')
    data['player_name'] = session.get('user')
    print_data(options=options, data=data, session=session)
    return render_template('game_PBoard.html', options=options, page_name=page_name, data=data)

@ts_sub1_bp.route('/game_p_review', methods=['GET', 'POST'])
# @is_logged_in
def game_PReview():
    rev_type = request.args.get('review')
    pages = {"STCK": "Stock Review Page", "BUS": "Business Review Page", "PPTY": "Property Review Page",
             "COMM": "Commodity Review Page", "LOAN": "Loan Review Page", "RENT": "Rent/ROI Review Page"}
    page_name = " "
    if not rev_type:
        return "Error: 'rev_type' is missing", 400  # Ensure rev_type is always provided
    page_name = pages[rev_type]

    options, data = render_preview_options(rev_type)

    data['player_number'] = session.get('player_number')
    data['player_name'] = session.get('user')
    print_data(options=options, data=data, session=session)
    return render_template('game_PReview.html', options=options, page_name=page_name, data=data)

@ts_sub1_bp.route('/game_help', methods=['GET', 'POST'])
# @is_logged_in
def game_help():
    glevel = session['glevel']
    ggoal = session['ggoal']
    data = session['data']
    data['user_captain'] = session['username']
    result, q = db.get_player_record(session['username'])
    data['game_ID'] = result['game_ID']
    page_name = "Game Help"
    gg = GameGoals()
    glevel_name = gg.get_level_name(glevel)
    ggoal_name = gg.get_goal_name(ggoal)
    goals = gg.data
    flash("There are three game levels and different game goals per level. Get familiar with them", "success")
    return render_template('game_help.html', page_name=page_name, data=data, goals=goals)

@ts_sub1_bp.route('/game_status', methods=['GET', 'POST'])
# @is_logged_in
def game_status():
    page_name = "Game Status"
    glevel = session['glevel']
    ggoal = session['ggoal']
    data = session['data']
    data['user_captain'] = session['username']
    result, q = db.get_player_record(session['username'])
    data['game_ID'] = result['game_ID']
    flash("There are three game levels and different game goals per level. Get familiar with them", "success")
    gg = GameGoals()
    features, goals, player_status1, player_status2, player_status3 = gg.build_status_report(glevel, ggoal, session['username'])
    ic(features, goals, player_status1, player_status2, player_status3)

    rpt_features = {
        "Features": features,
    }
    rpt_goals = {
        "Goals": goals
    }
    # Convert data to DataFrame
    df1 = pd.DataFrame(rpt_features)
    df2 = pd.DataFrame(rpt_goals)
    ic(df1, df2)
    # Create Dictionary
    player_status = {
        player_status1[0]: player_status1[1:],
        player_status2[0]: player_status2[1:]
    }
    if ggoal == "AAS":
        for key, value in player_status3.items():
            player_status[key.upper()] = value
    # Convert Player Status to a transposed DataFrame for better display
    ic(player_status)
    player_status_df = pd.DataFrame(player_status)
    ic(player_status_df)
    return render_template('game_status.html', page_name=page_name, data=data, rpt_features=df1, rpt_goals=df2, player_status=player_status_df, ggoal=ggoal)

# Function to remove trailing empty elements
def remove_trailing_empty(lst):
    return [x for x in lst if x]


# Function to pad lists to the same length
def pad_list(lst, length, padding_value=None):
    """Pad a list to a specific length with a padding value."""
    return lst + [padding_value] * (length - len(lst))


@ts_sub1_bp.route('/city_tour', methods=['GET', 'POST'])
# @is_logged_in
def city_Tour():
    page_name = "City Tour Page"

    return render_template('city_Tour.html', page_name=page_name)

@ts_sub1_bp.route('/tour_bdistrict', methods=['GET', 'POST'])
# @is_logged_in
def tour_BDistrict():
    page_name = "Business District Tour"

    return render_template('tour_BDistrict.html', page_name=page_name)

@ts_sub1_bp.route('/tour_edistrict', methods=['GET', 'POST'])
# @is_logged_in
def tour_EDistrict():
    page_name = "Entertainment District Tour"

    return render_template('tour_EDistrict.html', page_name=page_name)

@ts_sub1_bp.route('/tour_sdistrict', methods=['GET', 'POST'])
# @is_logged_in
def tour_SDistrict():
    page_name = "Stock Market District Tour"

    return render_template('tour_SDistrict.html', page_name=page_name)

@ts_sub1_bp.route('/tour_odistrict', methods=['GET', 'POST'])
# @is_logged_in
def tour_ODistrict():
    page_name = "Opportunity District Tour"

    return render_template('tour_ODistrict.html', page_name=page_name)

@ts_sub1_bp.route('/tour_rdistrict', methods=['GET', 'POST'])
# @is_logged_in
def tour_RDistrict():
    page_name = "Residential District Tour"

    return render_template('tour_RDistrict.html', page_name=page_name)

def print_data(data=None, options=None, dataopt=None, gc=None, ga=None, pc=None, session=None):
    if session != None:
        print("Session: ", session)
    elif pc != None:
        print("PC: ", pc)
    elif ga != None:
        print("GA: ", ga)
    elif gc != None:
        print("GC: ", gc)
    elif dataopt != None:
        print("DATAOPT: ", dataopt)
    elif data != None:
        print("DATA: ", data)