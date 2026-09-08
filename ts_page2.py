import decimal

from ts_database import *
from ts_game import *
from ts_cycle import *
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from datetime import datetime, date
from wtforms import Form
from app_factory import create_app, mysql
from functools import wraps
from ts_page3 import *
from index_mgr import get_im
import re

def render_rp_options():
    print("Session RP data: ", session)
    data = session['data']
    # INDEX MANAGER: Set opportunities table row for opportunity offering
    im = get_im()
    select = im.get_table_pointer("opportunities")
    stat = im.reset_table_pointer("opportunities")
    # ga = Game_Assets("opportunities")
    # select = ga.get_new_position()
    # ******************************************
    print(f"OPP row Selection: {select}")

    options = []
    ctgy = ['MESSAGE', 'OPPORTUNITY', 'WANT', 'NEED', 'COUNT']
    desc = []
    value = " "
    # The opportunity selection selected for this random play move
    stat, result, column_names = db.get_table_row("opportunities", select)
    if stat == "OK":
        # Check if the variable is a tuple and its first element is a dictionary
        if isinstance(result, tuple) and len(result) > 0 and isinstance(result[0], dict):
            # Access an item from the dictionary
            result = result[0]
            if "long_description" in result:
                value = result["long_description"]
            else:
                value = "Unknown Desc"
        session['result'] = result
        desc.append(value)
        for i in range(3):
            desc.append(' ')
        if result['OWN_code'] == "opp":
            desc[1] = "$  " + str(result['amount'])
        elif result['OWN_code'] == "want":
            desc[2] = "$  " + str(result['amount'])
        else:
            desc[3] = "$  " + str(result['amount'])
        desc.append(result['count'])

    o = Options(ctgy=ctgy, type=None, desc=desc, invest=None)

    options = o.get_options()

    return options

def render_rpbuy_options():
    user = session['user']
    options = session['options']
    result = session['result'] # The opportunity selection selected for this random play move
    ctgy = ['MESSAGE', 'TRANSACTION', 'Transaction COST', 'INVITE?']
    desc = []
    desc.append(result['long_description'])
    desc.append(result['short_description'])
    for option in options:
        if option['opt_ctgy'] == "WANT" and option['opt_desc'] != " ":
            desc.append(option['opt_desc'])
        if option['opt_ctgy'] == "NEED" and option['opt_desc'] != " ":
            desc.append(option['opt_desc'])
        if option['opt_ctgy'] == "OPPORTUNITY" and option['opt_desc'] != " ":
            desc.append(option['opt_desc'])
    if result['INVITES'] != "No":
        desc.append(result['INVITES'])
    else:
        desc.append(None)

    o = Options(ctgy=ctgy, type=None, desc=desc, invest=None)

    options = o.get_options()


def render_rp_sale_options(data):
    user = session['user']
    options = session['options']
    result = session['result'] # The opportunity selection selected for this random play move
    ctgy = ['MESSAGE', 'TRANSACTION', 'Transaction COST', 'INVITE?']
    desc = ['Your purchase is complete for this transaction.  '
            'This is a cash sale from your cash-on-hand. There may be an invite. If so, its travel time!']
    desc.append(result['short_description'])
    for option in options:
        if option['opt_ctgy'] == "WANT" and option['opt_desc'] != " ":
            desc.append(option['opt_desc'])
        if option['opt_ctgy'] == "NEED" and option['opt_desc'] != " ":
            desc.append(option['opt_desc'])
        if option['opt_ctgy'] == "OPPORTUNITY" and option['opt_desc'] != " ":
            desc.append(option['opt_desc'])
    if result['INVITES'] != "No":
        desc.append(result['INVITES'])
        session['INVITES'] = result['INVITES']
    else:
        desc.append("  No")
        session['INVITES'] = "No"

    o = Options(ctgy=ctgy, type=None, desc=desc, invest=None)

    options = o.get_options()

    dataopt = {
            'data': data,
            'user': user,
            'options': options
        }
    print("RPSale Options DATAOPT = ", dataopt)
    print("Session Dictionary: ", session)
    update_rp_player_game(dataopt)
    return dataopt

def update_rp_player_game(dataopt):
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
    # Unload data dictionary from the dataopt nested dictionary - current random play data
    data1 = dataopt['data']
    # Unload options dictionary from dataopt nested dictionary
    options1 = dataopt['options']
    # Unload data dictionary from the sessions nested dictionary - first random play data
    data2 = session['data']
    result = session['result'] # The opportunity selection selected for this random play move
    # recreate game card and player card from tables
    pc, q = db.get_player_record(session['user'])
    stat, gc = db.get_game_card(pc['game_ID'])
    # Unload options from the session nested dictionary
    options2 = session['options']
    # Array of values that represent investment items to generate investment rows
    inv_list = ["Car Purchase", "oNg Stock", "Rest & Recreation Park: Tickets",
                "Vacation Resort: Tickets", "TV 80inch"
                ]
    if result['short_description'] in inv_list:
        invest_data['player_number'] = data1['player_number']
        invest_data['invest_amount'] = decimal.Decimal(result['amount']) * decimal.Decimal(-1)
        invest_data['invest_type'] = "OTHR"
        invest_data['invest_count'] = int(result['count'])
        if int(result['count']) == 0:
            invest_data['invest_count'] = 1
        invest_data['invest_description'] = result['short_description']
        if result['short_description'] == "oNg Stock":
            invest_data['invest_type'] = "STCK"
            invest_data['invest_value'] = float(1000.00)
        else:
            invest_data['invest_value'] = abs(float(result['amount'])) * 1.25
        status = db.insert_investments_from_sale(invest_data)
        if status == "OK":
            flash("Random Play Investment successful!", "success")
    result = session['result']
    opp = Opportunity(result)
    print("Result in RP_PLAYER: ", result)

    dataopt = opp.set_buy_type(dataopt, result['short_description'])
    data1 = opp.set_buy_type(data1, result['short_description'])
    data1['pc'] = pc
    dataopt['data'] = data1
    if result['type'] == "exp":
        if int(result['amount']) < 0:
            pass
        else:
            result['amount'] = int(result['amount']) * -1
    # This function addresses both game and player card
    status = db.update_game_player(result['amount'], gc, dataopt)
    if status == "OK":
        flash("Game and Play status is good!", "success")
    bkgd_process = ["Stock Sell", "Cash OUT", "Property Insurance", "Property Sell", "Promotion", "Salary increase"]
    if result['short_description'] in bkgd_process:
        x = opp.stock_check_removal(data2['player_number'])
        print(f"Stock Check status: {x}")
        x = opp.cash_out(data2['player_number'])
        x = opp.set_player_flags(data2['player_number'])

def render_inplay_options():
    options = []
    cycle_round = session['cycle_round']
    cycle_round += 1
    session['cycle_round'] = cycle_round

    ctgy = ['GEN Message', 'CYCLE Message', 'PRODUCT', 'AMOUNT', 'COUNT']
    desc = build_inplay_options(cycle_round)

    o = Options(ctgy=ctgy, type=None, desc=desc, invest=None)

    options = o.get_options()

    return options

def build_inplay_options(cycle_round):
    desc = []
    desc.append(" This opportunity invitation may take you shopping, to college, on a job, buying stocks, "
                "or other life opportunities. Take the journey. It will result in two products or adventures, "
                "or a refusal can cost you a consulting fee.")
    invite_cycle = session['INVITES']
    if invite_cycle == "Sell Cycle":
        player_number = session['player_number']
        sc3 = Sellcycle(player_number)
        desc, iv_data = sc3.build_investment_for_sellcycle(desc)
        ga_sel = iv_data
        print(f"INPLAY IV Data: {ga_sel}")
    else:
        c = CycleExt()
        desc.append(c.get_cycle_message(invite_cycle))
        table = c.get_cycle_table_name(invite_cycle)
        # INDEX MANAGER: Based on one of the secondary tables referenced get table current pointer & reset
        im = get_im()
        pos = im.get_table_pointer(table)
        stat = im.reset_table_pointer(table)
        gat = Game_Assets(table)
        #pos = gat.get_new_position()
        print(f"Cycle row Selection: {pos}")

        ga_sel = gat.get_row(pos)
        print(f"INPLAY ga_sel: {ga_sel}")
        if ga_sel['code'] == "SC2":
            desc.append(ga_sel['INVITES'] + ": " + ga_sel['long_description'])
        else:
            desc.append(ga_sel['long_description'])
        desc.append("$  " + str(ga_sel['amount']))
        no_count_table = [
            "Job Cycle", "Life Cycle", "College Cycle"
        ]
        if invite_cycle in no_count_table:
            desc.append("  1")
        else:
            desc.append("  " + str(ga_sel['count']))
    if cycle_round == 1:
        session['cycle1'] = ga_sel
    else:
        session['cycle2'] = ga_sel
    print("IN OPT SESSION 2: ", session)
    return desc

def render_insale_options():
    # This routine has two purposes:
    # Briefly render the INSALE page and
    # update game & player tables
    data = session['data']
    options = session['options']
    user = session['user']
    amount_str = options[3]['opt_desc']
    count_str = options[4]['opt_desc']
    print(f"amount_str: {amount_str}")
    amount = extract_numeric_value(amount_str)
    count = extract_numeric_value(count_str)
    data['amount'] = amount
    data['count'] = count
    cycle_round = session['cycle_round']
    if cycle_round == 1:
        cycle = session['cycle1']
    else:
        cycle = session['cycle2']
    if "invest_description" in cycle:
        short_desc = cycle['invest_description']
        if "TRIP" in cycle['own_code']:
            short_desc = short_desc + " " + cycle['own_code']
        data['short_description'] = short_desc
    else:
        short_desc = cycle['short_description']
        data['short_description'] = short_desc
    if cycle['code'] == "SC2":
        INVITES = cycle['INVITES']
    else:
        INVITES = "Unknown"

    desc = []
    ctgy = ['CYCLE Message', 'PRODUCT', 'AMOUNT', 'COUNT']
    desc.append(" Hopefully, this cycle opportunity invitation was good for you. Whether it is cycle round 1 or 2, "
                "have a happy journey.")
    if cycle['code'] == "SC2":
        desc.append(short_desc + " at " + INVITES)
    else:
        desc.append(short_desc)
    desc.append(amount_str)
    desc.append(count_str)
    o = Options(ctgy=ctgy, type=None, desc=desc, invest=None)

    options = o.get_options()

    dataopt = {
        'data': data,  # player related information - amount, count, short desc added
        'user': user,   # user name of current player
        'cycle': cycle,   # current accepted cycle selected for player
        'options': options # latest web page data related to selected cycle
    }
    resp = update_insale_options(dataopt)
    if resp != "nomsg":
        # Add another option row
        o.add_row(ctgy=ctgy, type=None, desc=desc, invest=None)

    return options

def update_insale_options(dataopt):
    # Depending on the cycle data in play perform actions to update player and game data
    # CYCLE code, short_description, INVITES define a row
    # Short description and IMVITES can be combined with AT to define action
    # Code is two are three character mnemonic for cycle type
    msg = " "
    player_number = session['player_number']
    data = dataopt['data']
    user = dataopt['user']
    cycle = dataopt['cycle']
    options = dataopt['options']
    resp = "nomsg"
    if "invest_id" in cycle:
        id = cycle['invest_id']
    else:
        id = cycle['id']
    code = cycle['code']
    ce = CycleExt()
    table_name = ce.get_cycle_table_by_code(code)
    # Process Player data
    iv = Investment()
    pc = Players(user)
    ce = CycleExt()
    if code == "SC3":
        pc.update_data('cash_on_hand', cycle['invest_value'], action="A")
        sc3 = Sellcycle(player_number)
        iv_sold = sc3.get_row(cycle['rnum'])
        invest_id = cycle['invest_id']
        stat = sc3.delete_row(iv_sold)
    else:
        pc.update_data('cash_on_hand', cycle['COH'], action="A")
    if code == "SC" and cycle['investment_type'] == "STCK":
        if cycle['investment_adjust'] == "insert":
            pc.update_data('stock_value', cycle['stock_value'], action="A")
            stat = iv.parse_row_data(cycle, player_number)
            if stat == "OK":
                msg = ce.get_info_message("insert", code, cycle['investment_type'])
        elif cycle['investment_adjust'] == "remove":
            stat = db.delete_investments_by_code(cycle['investment_type'], player_number)
            if stat == "OK":
                msg = ce.get_info_message("remove", code, cycle['investment_type'])
        elif cycle['investment_adjust'] == "double":
            stat = iv.double_stock_investment(cycle['investment_type'], player_number)
            if stat == "OK":
                msg = ce.get_info_message("double", code, cycle['investment_type'])
    if code == "SC" and cycle['investment_type'] == "COMM":
        if cycle['investment_adjust'] == "insert":
            stat = pc.update_data('comm_value', cycle['comm_value'], action="A")
            stat = iv.parse_row_data(cycle, player_number)
        elif cycle['investment_adjust'] == "remove":
            stat = db.delete_investments_by_code(cycle['investment_type'], player_number)
            if stat == "OK":
                msg = ce.get_info_message("remove", code, cycle['investment_type'])
    if code == "LC2" and ("Tax" in cycle['short_description'] or "tax" in cycle['short_description']):
        col_name, col_value = ce.get_cycle_tax_code(cycle['tax_check'])
        stat = pc.update_data(col_name, col_value)
        stat = iv.parse_row_data(cycle, player_number)
        stat = pc.update_data('other_investment', abs(cycle['amount']), action="A")
        if stat == "OK":
            msg = ce.get_info_message("flag", code, cycle['tax_check'])
    if code == "SC2" and "Y" in cycle['investment_insert']:
        stat = iv.parse_row_data(cycle, player_number)
        if stat == "OK":
            msg = ce.get_info_message("insert", code, "OTHR")
    if code == "JC":
        msg = ce.get_info_message(cycle['amount'], code, cycle['salary'])
        if int(cycle['job_level']) > 0:
            msg = msg + "Congratulations on your promotion!"
        if cycle['job_level'] != "0":
            jl = int(cycle['job_level'])
            stat = pc.update_data('job_level', jl, action="A")
        pc.adjust_salary_amount(cycle['salary'])
    if code == "LC":
        if cycle['degree_level'] != "0":
            stat = pc.update_data('degree_level', cycle['degree_level'], action="A")
            if stat == "OK":
                msg = ce.get_info_message("degree", code, cycle['degree_level'])
        if cycle['investment'] == "LOAN":
            stat = iv.parse_row_data(cycle, player_number)
            loan_status = iv.verify_loan(pc.data)
        if cycle['investment'] == "RENT":
            stat = pc.update_data('other_investments', abs(cycle['amount']), action="A")
            pc_lstat = pc.verify_living_status()  # un-housed or housed based on player city_addr column
            iv_lstat = iv.verify_living_status(player_number)  # Home Owner, un-housed, Renter statuses
            if pc_lstat == "unhoused" or iv_lstat == "unhoused":
                stat = iv.parse_row_data(cycle, player_number)
                rent_status = iv.verify_rent(pc.data)
                stat = pc.update_data('city_addr', "1248.70", action="U")
    if code == "BC":
        if cycle['insurance_flag'] == "OFF":
            stat = pc.update_data('ins_assess', 0, action="U")
            if stat == "OK":
                msg = ce.get_info_message("insurance", code, cycle['insurance_flag'])
        if cycle['investment_insert'] == "Y":
            stat = iv.parse_row_data(cycle, player_number)
            stat = pc.update_data('other_investments', abs(decimal.Decimal(cycle['amount'])), action="A")
        if cycle['investment_insert'] == "remove":
            stat = db.delete_investments_by_code(cycle['product'], player_number)
    if msg != " ":
        resp = msg

    return resp

