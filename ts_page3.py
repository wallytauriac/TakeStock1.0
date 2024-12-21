import decimal

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

def render_request_play_options():
    """
    ○ TRAVEL REQUESTS
        § Cab – one of three travel modes to arrive at a location (inexpensive cost)
        § Portal – one of three travel modes to arrive at a location (expensive cost)
        § Train – one of three travel modes to arrive at a location  (moderate cost)
        + Plane travel is an option under consideration
        + The travel considerations are listed under TRAVEL DESTINATIONS
    ○ EVENT REQUESTS
        § (Life) – if decision is to start a life adventure
        § (College) – if decision is to start a college semester
        § (Job) – if decision is to start a job career
        + (Move) - select another house to buy and change address
        + Loan Pay - Multi-Payment Request to pay down outstanding loan amount
        + Loan Request - apply for a loan for a specified amount
    ○ INVESTMENT REQUESTS
        § Buy – chosen by player to buy stock, commodity, business, or property from a list
        § Sell – chosen by player to sell stock, commodity, business, or property from a list
    ○ TRAVEL DESTINATIONS FOR TRAVEL REQUESTS
        § Start a life adventure – supports 3 rounds for a player
        § Start a college semester – supports 2 rounds for a player
        § Start a job career – supports 4 rounds for a player
        § Start a stock trade adventure - supports 2 for a player
        § Vacation spots
        § Family outing
        § Meeting event
        § Shopping
        § Investment
        § Entertainment

    """

    options = []

    ctgy = ['STOCKS', 'PROPERTY', 'BUSINESS', 'COMMODITY']
    type = ['STCK', 'PPTY', 'BUS', 'COMM']
    x = build_request_play_options()

    d = {}
    for i in range(4):
        d['opt_ctgy'] = ctgy[i]
        d['opt_type'] = type[i]
        #d['opt_desc'] = desc[i]
        #d['opt_invest'] = invest[i]
        options.append(d)
        d = {}
    return options

def build_request_play_options():
    pass

def render_request_list(ctgy):
    q, d = db.get_requests_by_ctgy(ctgy)
    if q > 0:
        return d
    else:
        return []

def render_request_item(ctgy, item):
    q, requests = db.get_requests_by_ctgy(ctgy)
    if q > 0:
       request = requests[item-1]

def process_event_requests(req_id):
    session['cycle_round'] = 0
    page = "NOPAGE"
    if req_id == '1':
        session['INVITES'] = "Life Cycle"
        page = "INVITES"
    elif req_id == '2':
        session['INVITES'] = "College Cycle"
        page = "INVITES"
    elif req_id == '3':
        session['INVITES'] = "Job Cycle"
        page = "INVITES"
    elif req_id == '4' or req_id == '5':  # Move Address
        gat = Game_Assets("address")
        if req_id == '4':
            addr2 = gat.adjust_object_scope("PPTY_type", "House")
        else:
            addr2 = gat.adjust_object_scope("PPTY_type", "Rent")
        session['PPTY_type'] = addr2[0]['PPTY_type']
        print(f"PPTY_type in process_event_requests: {addr2[0]['PPTY_type']} ")
        pl = PageLayout()
        addresses = pl.load_address_data(addr2)
        print(f"Move to addresses: {addresses}")
        session['addresses'] = addresses
        page = "ADDRESSES"
    elif req_id == '6':
        session['page'] = "Loan Payments"
        page = session['page']
        iv = Investment()
        loans_inv = iv.get_player_investments_by_type(session['player_number'], "BILL")
        loans = iv.build_loan_data(loans_inv)
        session['loans'] = loans
    elif req_id == '7':
        session['page'] = "Loan Request"
        page = session['page']
        iv = Investment()
        loans = [{"type": "Loan Request", "description": "Signature Loan", "player_number": session['player_number'],
                      "amt_desired": Decimal(25000.00), "status": "unknown"} ]
        session['loans'] = loans

    return page

def process_loan_payments(req_id):
    """
    # Find the BILL investment card with the LOAN ID
    # Update the BILL card
    # Create and insert a BILLPAY card to document payment
    # return to the Action page
    """
    user = session['user']
    loans = session['loans']
    loan = loans[int(req_id)-1]
    loan_id = loan['id']
    pn = loan['player_number']
    pay_count = request.form.get('pay_count_' + req_id)
    payment = loan['payment']
    iv = Investment()

    owed_amt = loan['amount']
    total_payment = Decimal(payment) * Decimal(pay_count)
    new_amt = Decimal(owed_amt) - Decimal(total_payment)
    bill = iv.get_investment_by_id(loan_id)
    bill['invest_value'] = Decimal(new_amt)
    x = iv.update_bill_investment(bill)
    # Update the Cash on Hand
    p = Players(user)
    p.cash_on_hand = Decimal(p.cash_on_hand) - Decimal(total_payment)
    stat = p.update_table()
    if stat == "OK":
        flash("Loan Payment Received!", "success")
        b = Billpay()
        s = b.add_data_by_key("bill_type", "LOAN")
        s = b.add_data_by_key("bill_round", session['player_round'])
        s = b.add_data_by_key("bill_amount", total_payment)
        s = b.add_data_by_key("bill_description", "Loan Req Pay")
        s = b.add_data_by_key("player_number", pn)
        s = b.add_data_by_key("bill_value", new_amt)
        s = b.add_data_by_key("invest_id", bill['invest_count'])
        s = b.insert_billpay_card()
    else:
        flash("Loan Payment NOT processed!", "error")
        return "NOK"
    return "OK"


def process_loan_request(req_id):
    user = session['user']
    loans = session['loans']
    loan = loans[int(req_id) - 1]
    pn = loan['player_number']
    loan_amt = request.form.get('amt_desired_1')
    loan_desc = loan['description']
    bnkr = banker()
    stat = bnkr.apply_for_loan(user, loan_amt)
    loans[0]['amt_desired'] = loan_amt
    if stat == "OK":
        loan['status'] = "Approved"
    else:
        loan['status'] = "Rejected"
    session['loans'] = list(loans)


def process_event_property_request(req_id, req_type):
    if req_type == "House" or req_type == "Rent":
        session['req_type'] = req_type
        addresses = session['addresses']
        req = int(req_id)
        addr = addresses[req-1]
        id = addr['id']
        stat, result, column_names = db.get_table_row("address", id)
        if stat == "OK":
            # Check if the variable is a tuple and its first element is a dictionary
            if isinstance(result, tuple) and len(result) > 0 and isinstance(result[0], dict):
                # Access an item from the dictionary
                result = result[0]
                if "Address" in result:
                    if 'player_number' in session:
                        player = db.get_player_by_number(session['player_number'])
                        player['city_addr'] = result['Address']  # Reset players address
                        if req_id == "House":
                            player['rent_assess'] = 0  # Confirm player is not a renter
                        else:
                            player['rent_assess'] = 1  # Confirm player is a renter
                        player['ptax_assess'] = 1  # Confirm player pays taxes
                        stat = db.update_player3(player)
                if "Property" in result:
                    session['bp'] = result
        page = "BuyProd"
        return page

def process_investment_requests(req_id):
    page = "NOPAGE"
    inv_type = " "
    if req_id == '1' or req_id == '2':
        gat = Game_Assets("address")
        if req_id == '1':
            addr2 = gat.adjust_object_scope("District", "Residential")
            page = "Apartment Rental"
        else:
            addr2 = gat.adjust_object_scope("BLDG_type", "Building")
            page = "Building Rental"

        print(f"addr2 in process_investment_requests: {addr2} ")
        roi = ROI_Card()
        addr = roi.load_roi_from_addr(addr2, session['player_number'], 0)
        session['addr'] = addr
        print(f"addr in process_investment_requests: {addr} ")

    if req_id == '3' or req_id == '4' or req_id == '5':
        flag = 0
        if req_id == '3':
            inv_type = "PPTY"
        elif req_id == '4':
            inv_type = "STCK"
        elif req_id == '5':
            inv_type = "COMM"
        iv = Investment()
        inv_data = iv.get_player_investments_by_type(session['player_number'], inv_type)
        inv_loans = iv.get_player_investments_by_type(session['player_number'], "LOAN")
        page = inv_type
        if inv_type == "PPTY" and len(inv_loans) > 1:
            inv_data = []
            flash ("Property Sale prohibited, You possess more than 1 loan", "warning")
            flag = 1
        if len(inv_data) == 0:
            flash("Sale prohibited, You possess none of requested investment type.", "warning")
        if len(inv_data) > 0 and flag != 1:
            flash("Choose one investment to sell. A buyer may respond.", "success")
        session['inv_data'] = inv_data
    return page


def process_rental_properties(req_id, req_type):
    addr = session['addr']
    ppty = addr[int(req_id)-1]
    price = ppty['roi_price']
    user = session['user']
    p = Players(user)
    if Decimal(price) <= Decimal(p.cash_on_hand):
        # This purchase can be completed
        stat = "OK"
        debit = Decimal(price) * Decimal(-1.00)
        game_ID = p.game_ID
        p.update_data("cash_on_hand", debit, action="A")
        p.update_data("property_value", Decimal(price), action="A")
        stat = p.update_table()
        if stat == "OK":
            g = GameBoard(game_ID)
            g.update_spending(price)
            game_card = g.get_game_data()
            stat = g.put_game_data(game_card)
        else:
            stat = "NOK"
        if stat == "OK":
            # Ready to create new ROI card
            r = ROI_Card()
            stat = r.build_insert_roi(ppty)
    else:
        stat = "NOK"
    return stat

def process_sell_properties(req_id, req_type):
    inv_data = session['inv_data']
    user = session['user']
    inv_item = inv_data[int(req_id) - 1]
    price = Decimal(inv_item['invest_value'])
    buy_assess = ["Y", "N", "Y", "Y", "N", "N"]
    pc = Players(user)
    resp = random.choice(buy_assess)
    if resp == "Y":
        x = pc.update_data("cash_on_hand", price, action="A")
        x = pc.update_table()
        iv = Investment()
        x = iv.remove_player_investments_by_id(inv_item['invest_id'])
        stat = "OK"
    else:
        stat = "NOK"

def process_travel_requests(req_id):
    page = "NOPAGE"
    inv_type = "OTHR"
    if req_id == '1':
        trv = Travel()
        trav = trv.get_vacation_rows()
        travel = trv.create_sales_info(trav)
        session['travel'] = travel
        page = "Vacation"

    if req_id == '2':
        shp = Shopping("shopping")
        shop = shp.get_onsale_rows()
        retailers = shp.get_list_of_retailers(shop)
        session['retailers'] = retailers
        page = "Shopping"

    if req_id == '3':
        bus = Business()
        cmpy = bus.get_company_rows()
        companies = bus.get_company_list(cmpy)
        session['companies'] = companies
        page = "Companies"

    if req_id == '4':
        bus = Business()
        locals = bus.get_local_rows()
        session['locals'] = locals
        page = "Locals"

    if req_id == '5':
        pn = session['player_number']
        iv = Investment()
        investments = iv.get_player_investments_by_code(pn, "TRIP")
        trips = iv.update_trip_investments(investments)
        session['trips'] = trips
        page = "Trip Requests"
    return page

def process_vacation_travel(req_id, req_opt):
    # Player selected one or more vacation packages
    # Update players/game card with COH debit
    # Create investment cards (OTHR)
    # Destinations and ids in request
    # Format options display as confirmation

    travel = session['travel']
    print(f"TRAVEL from session: {travel}")
    print(f"REQ_ID: {req_id}")
    selected_data = [row for row in travel if row['id'] in map(int, req_id)]
    print(f"TRAVEL selected_data: {selected_data}")
    pn = session['player_number']
    user = session['user']
    game_ID = session['game_ID']
    selected_travel = SelectedTravel(selected_data)
    selected_travel.update_game_table(game_ID)
    selected_travel.update_player_table(user)
    selected_travel.update_investments_table(pn)
    options = selected_travel.build_page_data()
    session['options'] = options
    page = "Vacation Receipt"
    return page

def process_shopping_travel(req_id, req_opt):
    # Player selected a store to do some shopping
    # Need to provide Player with shopping deals in block form
    # No actual charges for travel. Emulate online shopping with delivery
    shp = Shopping("shopping")
    sale_items = shp.select_store_items(req_opt)
    sales = shp.create_sales_info(sale_items)
    session['sales'] = sales
    page = "Store Sale Items"
    return page

def process_shopping_online(req_id, req_opt):
    # Player selected one or more shopping items
    # Tabulate and update player/game cards
    sales = session['sales']
    print(f"SALES from session: {sales}")
    print(f"REQ_ID: {req_id}")
    selected_data = [row for row in sales if row['id'] in map(int, req_id)]
    print(f"SALES selected_data: {selected_data}")
    pn = session['player_number']
    user = session['user']
    game_ID = session['game_ID']
    selected_items = SelectedItems(selected_data)
    selected_items.update_game_table(game_ID)
    selected_items.update_player_table(user)
    selected_items.update_investments_table(pn)
    options = selected_items.build_page_data()
    session['options'] = options
    page = "Shopping Receipt"
    return page

def process_business_travel(req_id, req_opt):
    # Player accepted a job offer
    # Update players/game card with salary and COH changes
    # Player next accept a contract assignment with travel
    pn = session['player_number']
    user = session['user']
    game_ID = session['game_ID']
    companies = session['companies']
    print(f"COMPANIES from session: {companies}")
    company_data = [row for row in companies if row['id'] in list(req_id)]
    bus = Business()
    cmpy = bus.get_company_rows()
    projects = bus.get_travel_list_by_company(cmpy, req_opt)
    print(f"Company Projects: {projects}")
    bp = BusinessProjects(projects)
    bp.update_game_table(game_ID)
    bp.update_player_table(user)
    bp.update_investments_table(pn)
    options = bus.build_page_data(projects)
    session['options'] = options
    page = "Company Projects"
    return page

def process_local_travel(req_id, req_opt):
    # Player selects a travel schedule
    locals = session['locals']
    selected_data = []
    print(f"LOCALS from session: {locals}")
    print(f"REQ_ID: {req_id}")
    selected = int(req_id) - 1
    selected_data.append(locals[selected])
    print(f"LOCALS selected_data: {selected_data}")
    pn = session['player_number']
    user = session['user']
    game_ID = session['game_ID']
    selected_travel = SelectedTravel(selected_data)
    selected_travel.update_game_table(game_ID)
    selected_travel.update_player_table(user)
    selected_travel.update_investments_table2(pn)
    options = selected_data.copy()
    session['options'] = options
    page = "Local Travel Receipt"
    return page

def process_scheduled_trips(req_id, req_opt):
    print(f"PST req_id and req_opt: {req_id} and {req_opt} ")
    trips = session['trips']
    trip = trips[int(req_id) - int(1)]
    id = trip['id']
    iv = Investment()
    status = iv.remove_player_investments_by_id(id)
    page = "Continue Trip"
    return page

def process_scheduled_report():
    pn = session['player_number']
    user = session['user']
    travel = session['travel']
    trips = session['trips']
    reports = {"Local Trip": "Local Report", "Business Trip": "Business Report",
             "Vacation": "Vacation Report"}
    report_name = reports[travel['req_opt']]
    req_id = int(travel['req_id']) - int(1)
    trip = trips[req_id]
    tr = TravelReport(user, report_name, trip)
    if report_name != "Business Report":
        trip = tr.select_vacation_report()
    else:
        trip = tr.select_business_report()
    session['trip'] = trip
