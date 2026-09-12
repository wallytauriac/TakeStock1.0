import decimal
from random import randint
import json
from flask import Flask, Blueprint, render_template, redirect, url_for, session, current_app
from ts_validation import *
from ts_page import *
from ts_page3 import *
from ts_game import *
from ts_events import *
from ts_database import *
from flask_mysqldb import MySQL
from app_factory import create_app, mysql
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField
from functools import wraps
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request
import pickle
from flask import request

ts_sub2_bp = Blueprint('ts_sub2_bp', __name__, template_folder="templates")
db = DB_Mgr(mysql)

@ts_sub2_bp.route('/game_request_play', methods=['GET', 'POST'])
# @is_logged_in
def game_RequestPlay():
    if session['glevel'] == "EP" or session['glevel'] == "CP":
        flash("Request Play only available for Guru Play", "error")
        return redirect(url_for('ts_sub1_bp.game_action'))
    page_name = "Request Play Page"
    data = {}
    data['player_number'] = session.get('player_number')
    data['player_move'] = session.get('player_move')
    data['player_round'] = session.get('player_round')
    session['data'] = data
    user = session['user']
    db.pickle_save("RequestPlay", "session", session, "cookie")
    if request.method == "GET":
        return render_template('game_RequestPlay.html', data=data, page_name=page_name, user=user)
    else:
        if 'travel_mode' in request.form:
            session['travel_mode'] = request.form['travel_mode']
        else:
            flash("Please select both a travel mode and request. ", "error")
            return render_template('game_RequestPlay.html', data=data, page_name=page_name, user=user)
        if 'request_category' in request.form:
            pass
        else:
            flash("Please select both a travel mode and request type. ", "error")
            return render_template('game_RequestPlay.html', data=data, page_name=page_name, user=user)
        if request.form['request_category'] == "Event":
            return redirect(url_for('ts_sub2_bp.event_requests'))
        elif request.form['request_category'] == "Investment":
            return redirect(url_for('ts_sub2_bp.investment_requests'))
        elif request.form['request_category'] == "Travel":
            return redirect(url_for('ts_sub2_bp.travel_requests'))

@ts_sub2_bp.route('/event_requests')
def event_requests():
    if request.method == "GET":
        page_name = "Request Event Page"
        data = session['data']
        user = session['user']
        requests = render_request_list("Event")
        return render_template('event_requests.html', data=data, page_name=page_name, user=user, requests=requests)
    else:
        pass

    return render_template('event_requests.html')

@ts_sub2_bp.route('/investment_requests')
def investment_requests():
    if request.method == "GET":
        page_name = "Investment Event Page"
        data = session['data']
        user = session['user']
        requests = render_request_list("Investment")
        return render_template('investment_requests.html', data=data, page_name=page_name, user=user, requests=requests)
    else:
        pass

    return render_template('investment_requests.html')

@ts_sub2_bp.route('/travel_requests')
def travel_requests():
    if request.method == "GET":
        page_name = "Travel Event Page"
        data = session['data']
        user = session['user']
        requests = render_request_list("Travel")
        return render_template('travel_requests.html', data=data, page_name=page_name, user=user, requests=requests)
    else:
        pass

    return render_template('travel_requests.html')

@ts_sub2_bp.route('/request_handler', methods=['GET', 'POST'])
def request_handler():
    data = session['data']
    page_name = " "
    requests = []
    user = session['user']
    if request.method == "GET":
        req_type = request.args.get('request')
        req_id = request.args.get('request_id')
        session['request_id'] = req_id
        session['request_type'] = req_type
        db.pickle_save("RequestPlay", "session", session, "cookie")
        print(f"Request type and id: {req_type} - {req_id} ")
        if not req_type:
            return "Error: 'request' is missing", 400  # Ensure keyword is always provided
        if not req_id:
            return "Error: 'request_id' is missing", 400  # Ensure keyword is always provided
        if req_type == "Event":
            return redirect(url_for('ts_sub2_bp.event_handler'))
        elif req_type == "Investment":
            return redirect(url_for('ts_sub2_bp.investment_handler'))

        elif req_type == "Travel":
            return redirect(url_for('ts_sub2_bp.travel_handler'))


    return render_template('review_requests.html', data=data, page_name=page_name, user=user)

@ts_sub2_bp.route('/event_handler', methods=['GET', 'POST'])
def event_handler():
    req_id = session['request_id']
    data = session['data']
    page_name = "Event List Page"
    user = session['user']
    print(f"Event id: {req_id}")
    requests = render_request_list("Event")
    page = process_event_requests(req_id)
    db.pickle_save("RequestPlay", "session", session, "cookie")
    addresses = []
    # Check page value to determine output
    if page == "INVITES":
        return redirect(url_for('ts_sub1_bp.game_INPlay'))
    elif page == "ADDRESSES":
        print(f"Property request type: {session['PPTY_type']}")
        if session['PPTY_type'] == "House":
            title = "Move Opportunity - Houses for Sale"
            image = "TakeStock_Residences.png"
        else:
            title = "Move Opportunity - Property for Rent"
            image = "TakeStock_Apartments.png"
        addresses = session['addresses']
        return render_template('move_address.html', data=data, page_name=page_name, user=user, addresses=addresses,
                               requests=requests, title=title, image=image)
    elif page == "Loan Payments":
        title = "Loan Opportunity - Make Loan Payments"
        loans = session['loans']
        return render_template('loan_list.html', data=data, page_name=page_name, user=user, loans=loans,
                               requests=requests, title=title)
    elif page == "Loan Request":
        title = "Loan Opportunity - Request a Loan"
        loans = session['loans']
        return render_template('loan_request.html', data=data, page_name=page_name, user=user, loans=loans,
                               requests=requests, title=title)
    return render_template('move_address.html', data=data, page_name=page_name, user=user, addresses=addresses,
                           requests=requests)

@ts_sub2_bp.route('/event_request_process', methods=['GET', 'POST'])
def event_request_process():
    req_id = request.args.get('request_id')
    req_type = request.args.get('request')

    data = session['data']
    if req_type == "House" or req_type == "Rent":
        print(f"DATA in event_request_process: {data}")
        page = process_event_property_request(req_id, req_type)
        data['buy_type'] = "bp"
        # Ensure data dictionary is populated
        session['data'] = data
        bp = session['bp']
        user = session['user']
        session.modified = True
        db.pickle_save("RequestPlay", "session", session, "cookie")
        # Create a new request context for game_BuyProd
        with current_app.test_request_context('/game_buyprod?product=bp'):
            # Manually set session data in the new context
            session['data'] = data
            session['bp'] = bp
            session.modified = True
            session['user'] = user
            response = current_app.full_dispatch_request()
        return response.get_data(as_text=True)
    if req_type == "Loan Payments":
        stat = process_loan_payments(req_id)
        if stat == "OK":
            return redirect(url_for('ts_sub1_bp.game_pass'))
        else:
            page_name = "Loan Error Page"
            user = session['user']
            loans = session['loans']
            title = "Problem accessing the BILL investment."
            requests = {}
            db.pickle_save("RequestPlay", "session", session, "cookie")
            return render_template('loan_list.html', data=data, page_name=page_name, user=user, loans=loans,
                                   requests=requests, title=title)
    if req_type == "Loan Request":
        process_loan_request(req_id)
        page_name = "Loan Request Page"
        title = "Loan Opportunity - Response to Loan Request"
        user = session['user']
        loans = session['loans']
        requests = {}
        db.pickle_save("RequestPlay", "session", session, "cookie")
        return render_template('loan_request.html', data=data, page_name=page_name, user=user, loans=loans,
                               requests=requests, title=title)

    return render_template('move_address.html', data=data)

@ts_sub2_bp.route('/investment_handler', methods=['GET', 'POST'])
def investment_handler():
    req_id = session['request_id']
    data = session['data']
    page_name = "Investment List Page"
    user = session['user']
    print(f"Investment id: {req_id}")
    requests = render_request_list("Investment")
    page = process_investment_requests(req_id)
    db.pickle_save("RequestPlay", "session", session, "cookie")
    # Check page value to determine output
    if page == "Apartment Rental":
        page_name = "Apartment List Page"
        title = "Rent Revenue Opportunity - Apartments & Condos"
        addr = session['addr']
        image = "TakeStock_Apartments.png"
        return render_template('property_rental.html', data=data, page_name=page_name, user=user, title=title, image=image, addr=addr)
    if page == "Building Rental":
        page_name = "Building List Page"
        title = "Rent Revenue Opportunity - Office & Retail"
        addr = session['addr']
        image = "TakeStock City (Main).png"
        return render_template('property_rental.html', data=data, page_name=page_name, user=user, title=title, image=image, addr=addr)
    if page in ["PPTY", "STCK", "COMM", "BUS"]:
        page_name = "Investment Sale List Page"
        title = "Sale Opportunity - Investments"
        inv_data = session['inv_data']
        image = "TakeStock City (Main).png"
        return render_template('property_sale.html', data=data, page_name=page_name, user=user, title=title, image=image, inv_data=inv_data)


    return render_template('move_address.html', data=data, page_name=page_name, user=user)

@ts_sub2_bp.route('/investment_request_process', methods=['GET', 'POST'])
def investment_request_process():
    req_id = request.args.get('request_id')
    req_type = request.args.get('request')
    data = session['data']
    user = session['user']
    addr = {}

    if req_type == "House" or req_type == "Rent":
        stat = process_rental_properties(req_id, req_type)
        if stat == "OK":
            addr1 = session['addr']
            addr = addr1[int(req_id) - 1]
            flash("Your property purchase now has an ROI card. Payments every 5th round.", "success")
        else:
            flash("Your property purchase failed approval. Insufficient funds.", "warning")
        page_name = "Apartment List Page"
        title = "Apartments, Condos, Mansion - Rent Revenue Opportunity"
        image = "TakeStock_Apartments.png"
        return render_template('property_rental.html', data=data, page_name=page_name, user=user, title=title, image=image,
                            addr=addr)
    types = ["Education", "Office", "Retail", "Amusement"]
    if req_type in types:
        stat = process_rental_properties(req_id, req_type)
        if stat == "OK":
            addr1 = session['addr']
            addr = list(addr1[int(req_id) - 1])
            flash("Your property purchase now has an ROI card. Payments every 5th round.", "success")
        else:
            flash("Your property purchase failed approval. Insufficient funds.", "warning")
        page_name = "Apartment List Page"
        title = "Office, Retail, Education, Amusement - Rent Revenue Opportunity"
        image = "TakeStock City (Main).png"
        return render_template('property_rental.html', data=data, page_name=page_name, user=user, title=title, image=image,
                        addr=addr)
    if req_type in ["PPTY", "STCK", "COMM"]:
        inv_data = []
        stat = process_sell_properties(req_id, req_type)
        if stat == "OK":
            inv_data1 = session['inv_data']
            inv_data = list(inv_data1[int(req_id) - 1])
            flash("Found a buyer for your investment. Item sold!", "success")
        else:
            flash("No buyer found. Try again later.", "warning")
        page_name = "Investment Sale Page"
        title = "Sales Opportunity Result"
        image = "TakeStock City (Main).png"
        return render_template('property_sale.html', data=data, page_name=page_name, user=user, title=title, image=image,
                        inv_data=inv_data)
    page_name = "Unknown Page"
    return render_template('move_address.html', data=data, page_name=page_name)


@ts_sub2_bp.route('/travel_handler', methods=['GET', 'POST'])
def travel_handler():
    req_id = session['request_id']
    req_type = session['request_type']
    requests = render_request_list("Travel")

    data = session['data']
    page_name = "Travel List Page"
    user = session['user']
    print(f"Event id: {req_id}")

    page = process_travel_requests(req_id)
    db.pickle_save("RequestPlay", "session", session, "cookie")
    if page == "Vacation":
        page_name = "Travel Schedule Page"
        travel = session['travel']
        title = "Vacation Travel Packages"
        flash("Select one or more packages using the checkbox, and then click the SUBMIT button.", "success")
        return render_template('travel_schedule.html', data=data, page_name=page_name, user=user, travel=travel,
                               title=title)
    if page == "Shopping":
        page_name = "Shopping List Page"
        retailers = session['retailers']
        title = "Shopping Store List"
        image = "TakeStock City (Main).png"
        return render_template('shopping_list.html', data=data, page_name=page_name, user=user, retailers=retailers, title=title, image=image)
    if page == "Companies":
        page_name = "Employer Job Page"
        companies = session['companies']
        selected_companies = random.sample(companies, 3)
        title = "Personal Job Offers"
        image = "TakeStock City (Main).png"
        return render_template('business_offer.html', data=data, page_name=page_name, user=user, selected_companies=selected_companies, title=title, image=image)
    if page == "Locals":
        page_name = "Local Travel Page"
        locals = session['locals']
        title = "Local Travel Locations"
        image = "TakeStock City (Main).png"
        return render_template('local_travel.html', data=data, page_name=page_name, user=user, locals=locals, title=title, image=image)
    if page == "Trip Requests":
        page_name = "Trip Requests Page"
        trips = session['trips']
        title = "Scheduled Trips"
        image = "vacationspots.png"
        form_action = url_for("ts_sub2_bp.travel_request_process")

        # Print the form_action value for debugging
        print(f"Form Action: {form_action}")
        button_label = "Take Trip"
        #selected_trip_index = None
        print(f"trips from session: {trips}")
        return render_template('scheduled_trips.html', data=data, page_name=page_name, user=user, trips=trips, title=title,
                               image=image, form_action=form_action, button_label=button_label)

@ts_sub2_bp.route('/travel_request_process', methods=['GET', 'POST'])
def travel_request_process():
    req_type = request.form.get('titleh') or request.args.get('titleh')
    req_opt = None
    req_id = None
    data = session['data']
    user = session['user']
    print(f"titleh value: {req_type}")
    page = " "
    if req_type == "Vacation Travel Packages":
        req_id = request.form.getlist('selected_items')
        req_opt = request.form.getlist('requesth')
        print(f"Req_id and req_opt: {req_id} and {req_opt}")
        page = process_vacation_travel(req_id, req_opt)
    if req_type == "Shopping Store List":
        req_opt = request.args.get('request_opt')
        req_id = request.args.get('request_id')
        page = process_shopping_travel(req_id, req_opt)
    if req_type == "Store Sale Items":
        req_id = request.form.getlist('selected_items')
        req_opt = request.form.getlist('requesth')
        print(f"Req_id and req_opt: {req_id} and {req_opt}")
        page = process_shopping_online(req_id, req_opt)
    if req_type == "Personal Job Offers":
        req_opt = request.form.get('companyb')
        req_id = request.form.get('companyi')
        page = process_business_travel(req_id, req_opt)
    if req_type == "Local Travel Locations":
        req_opt = request.form.get('locald')
        req_id = request.form.get('locali')
        page = process_local_travel(req_id, req_opt)
    if req_type == "Scheduled Trips":
        print("In travel_request_process for Scheduled Trips.")
        req_opt = request.form.get('tript')
        req_id = request.form.get('tripi')
        print(f"request and ID: {req_opt} and {req_id}")
        page = process_scheduled_trips(req_id, req_opt)

    if page == "Vacation Receipt":
        options = session['options']
        title = "You purchased the following items. Check your Player Board."
        page_name = "Vacation Receipt Page"
        return render_template('vacation_receipt.html', data=data, page_name=page_name, user=user, options=options, title=title)
    if page == "Store Sale Items":
        sales = session['sales']
        title = "Store Sale Items"
        page_name = "Store Shopping Page"
        flash("Select one or more items by clicking checkbox below each item desired.", "success")
        return render_template('shopping_online.html', data=data, page_name=page_name, user=user, sales=sales,
                               title=title)
    if page == "Shopping Receipt":
        options = session['options']
        title = "You purchased the following items. Check your Player Board."
        page_name = "Shopping Receipt Page"
        return render_template('shopping_receipt.html', data=data, page_name=page_name, user=user, options=options, title=title)
    if page == "Company Projects":
        options = session['options']
        title = "You have the following projects to complete requiring your attention. Check your Player Board."
        subtitle = req_opt
        page_name = "Business Project Page"
        return render_template('project_voucher.html', data=data, page_name=page_name, user=user, options=options, title=title, subtitle=subtitle)
    if page == "Local Travel Receipt":
        options = session['options']
        title = "You selected for purchase the following local travel. Check your Player Board."
        subtitle = req_opt
        page_name = "Local Travel Page"
        return render_template('local_travel_receipt.html', data=data, page_name=page_name, user=user, options=options, title=title, subtitle=subtitle)
    if page == "Continue Trip":
        page_name = "Trip Requests Page"
        trips = session['trips']
        title = "Continue Trip"
        image = "vacationspots.png"
        form_action = url_for('ts_sub2_bp.travel_trip_process')
        button_label = "Continue Trip"
        print(f"TRP req_id: {req_id}")
        flash("Your selected trip is highlighted. Click the button to continue with your flight.", "success")
        return render_template('scheduled_trips.html', data=data, page_name=page_name, user=user, trips=trips,
                               title=title, image=image, form_action=form_action, button_label=button_label, selected_trip_index=req_id)

    return f"You have selected: Request:{req_type} | Request_opt:{req_opt} | Request_id:{req_id}"

@ts_sub2_bp.route('/travel_trip_process', methods=['GET', 'POST'])
def travel_trip_process():
    req_type = request.form.get('titleh') or request.args.get('titleh')
    req_opt = request.form.get('tript')
    req_id = request.form.get('tripi')
    data = session['data']
    user = session['user']
    page_name = "Flight Page"
    travel = {
        "req_type": req_type,
        "req_opt": req_opt,
        "req_id": req_id
    }
    session['travel'] = travel

    types = {"TRVL": "Local Trip", "BUS": "Business Trip", "OTHR": "Vacation"}
    if req_opt != "Local Trip":
        video = "TakeStock_Vacation.mp4"
        flash("Wherever your travel takes you, bring your best and the rewards will be great!", "success")
    else:
        video = "Takestock_Transway1.mp4"
        flash("TakeStock Village has plenty to offer whether you go there by plane, cab, train, or portal!", "success")
    return render_template('flight_departure.html', data=data, page_name=page_name, user=user, video=video)


@ts_sub2_bp.route('/travel_report_process', methods=['GET', 'POST'])
def travel_report_process():
    process_scheduled_report()
    data = session['data']
    user = session['user']
    travel = session['travel']
    trip = session['trip']
    pages = {"Local Trip": "Local Report Page", "Business Trip": "Business Report Page",
             "Vacation": "Vacation Report Page"}
    page_name = pages[travel['req_opt']]
    types = {"Local Trip": "local_report.html", "Business Trip": "business_report.html", "Vacation": "vacation_report.html"}
    web_page = types[travel['req_opt']]
    return render_template(web_page, data=data, page_name=page_name, user=user, trip=trip)
    # return f"You have selected: Request:{data} | Request_opt:{user}"