from random import randint
import json
from flask import Flask, Blueprint, render_template, redirect, url_for, session
from ts_validation import *
from ts_page import *
from ts_database import *
from flask_mysqldb import MySQL
from app_factory import create_app, mysql
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField
from functools import wraps

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
    pn = session.get('player_number')
    pc = session.get('player_count')
    print(f"passed data: {pn} and {pc}")
    ga = Game_Action()
    data = session.get('data')
    data['ga']['position_id'] = ga.get_new_position()
    if str(pn) < str(pc):
        session['player_move'] += 1
        session['player_number'] += 1
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
    result, q = db.get_player_record(username)

    if q>0:
        status, players = db.get_players_game_card(result["game_ID"], allcolumn="Y")
        print("Action Players: ", players)
        for player in players:
            if player['player_number'] == session['player_number']:
                if player['cash_on_hand'] == 0.00:
                    stat = db.update_player2(player)
        if status == "OK":
            session['data'] = data
            data = render_game_card(session, result["game_ID"])
            print("Game card: ", data)
            pc = render_player_card(players, session['player_number'])
            print("Player card: ", pc)
            user = pc['username']
            session['user'] = pc['username']
            data['pc'] = pc
            session['data'] = data
        else:
            flash("Failed to retrieve player details", "error")
            return redirect(url_for('gameAction', data=data, page_name=page_name, user=user))

    return render_template('gameAction.html', data=data, page_name=page_name, user=user)

@ts_sub1_bp.route('/game_s_play', methods=['GET', 'POST'])
# @is_logged_in
def game_SPlay():
    page_name = "Single Play Page"
    data = {}
    data['player_number'] = session.get('player_number')
    data['player_move'] = session.get('player_move')
    data['player_round'] = session.get('player_round')
    options = render_sp_options()
    session['options'] = options
    user = session['user']

    print("SPLAY Options: ", options)
    print("SESSION ", session)
    return render_template('game_SPlay.html', data=data, page_name=page_name, options=options, user=user)


@ts_sub1_bp.route('/game_buyprod', methods=['GET', 'POST'])
def game_BuyProd():
    dataopt = {}  # Initialize dataopt early


    if request.method == 'GET':
        # First Access: Handle `buy_type` from the URL parameter
        #form = GameBuyForm(request.args)
        buy_type = request.args.get('product')
        if not buy_type:
            return "Error: 'buy_type' is missing", 400  # Ensure buy_type is always provided

        # Populate `data` dictionary
        data = {
            'player_number': session.get('player_number'),
            'player_move': session.get('player_move'),
            'player_round': session.get('player_round'),
            'buy_type': buy_type
        }

    elif request.method == 'POST':
        # Process the POST request
        data_json = request.form.get('data')
        options_json = request.form.get('options')
        # Ensure the JSON strings are properly formatted
        data = json.loads(data_json.replace("'", "\""))
        options = json.loads(options_json.replace("'", "\""))
        form = GameBuyForm(request.form)

        buy_type = request.form.get('buy_type')  # Ensure buy_type persists
        if buy_type == "bb":
            data['choice'] = form.choice.data
        data['buy_type'] = buy_type
        print("DATA: ", data)
        print("OPTIONS: ", options)
        # Populate `dataopt` using the data from the POST request
        dataopt = render_sale_options(data)
        print("DATAOPT: ", dataopt)
        page_name = "Product Sale Page"
        dataopt['page_name'] = page_name
        dataopt['errors'] = form.errors
        return render_template('game_Sale.html', **dataopt)

    # Determine which options to render based on buy_type
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

    user = session['user']
    return render_template('game_BuyProd.html', data=data, user=user, page_name=page_name, options=options)

@ts_sub1_bp.route('/game_sale', methods=['GET', 'POST'])
# @is_logged_in
def game_Sale():
    data = request.args.get('product')
    username = session.get('username')
    flash("Your Game Card has been updated successfully!", "success")
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
    print(options)
    return render_template('game_RPlay.html', options=options, page_name=page_name, user=user, data=data)

@ts_sub1_bp.route('/game_t_play', methods=['GET', 'POST'])
# @is_logged_in
def game_TPlay():
    page_name = "Triple Play Page"
    data = {}
    data['player_number'] = session.get('player_number')
    data['player_move'] = session.get('player_move')
    data['player_round'] = session.get('player_round')
    options = render_tp_options()
    user = session['user']
    session['options'] = options
    print(session)
    return render_template('game_TPlay.html', options=options, page_name=page_name, user=user, data=data)

@ts_sub1_bp.route('/game_tpbuy', methods=['GET', 'POST'])
def game_TPBuy():
    dataopt = {}  # Initialize dataopt early

    # Populate `data` dictionary
    data = {
        'player_number': session.get('player_number'),
        'player_move': session.get('player_move'),
        'player_round': session.get('player_round'),
    }

    if request.method == 'POST':
        # Process the POST request
        data_json = request.form.get('data')
        options_json = request.form.get('options')
        # Ensure the JSON strings are properly formatted
        data = json.loads(data_json.replace("'", "\""))
        options = json.loads(options_json.replace("'", "\""))

        print("DATA: ", data)
        print("OPTIONS: ", options)
        # Populate `dataopt` using the data from the POST request
        dataopt = render_tpsale_options(data)
        print("DATAOPT: ", dataopt)
        page_name = "Triple Sale Page"
        dataopt['page_name'] = page_name

        return render_template('game_TPSale.html', **dataopt)

    # Determine which options to render based on buy_type

    options = render_bs_options(session)

    options = render_bp_options(session)

    options = render_bb_options(session)
    page_name = "Triple Sale Page"
    user = session['user']
    return render_template('game_TPBuyProd.html', data=data, user=user, page_name=page_name, options=options)

@ts_sub1_bp.route('/game_tpsale', methods=['GET', 'POST'])
# @is_logged_in
def game_TPSale():

    username = session.get('username')
    flash("Your Game and Play Card have been updated successfully!", "success")
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
    print(status)
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
    print(options)
    return render_template('game_GBoard.html', options=options, page_name=page_name, data=data)

@ts_sub1_bp.route('/game_p_board', methods=['GET', 'POST'])
# @is_logged_in
def game_PBoard():
    page_name = "Game Board Page"

    options, data = render_pb_options()
    data['player_number'] = session.get('player_number')
    data['player_name'] = session.get('user')
    return render_template('game_PBoard.html', options=options, page_name=page_name, data=data)

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
