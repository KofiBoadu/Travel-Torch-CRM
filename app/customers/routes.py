from flask import render_template, request, redirect, url_for, flash, session
from app.models import get_all_contacts_information, get_all_upcoming_travel_packages, add_new_contact, \
    get_destination_id
from app.models import get_travel_package_id, get_contact_id, book_a_tour_for_a_contact, get_all_destinations, \
    create_new_tour_packages
from app.models import check_contact_exists, all_states
from app.customers import customers_bp
import datetime
import math
from flask_login import login_required, current_user
from app.extension import cache
from app.models import format_phone_number, remove_a_paid_contact, get_total_num_of_contacts
from app.customer_models import fetch_customer_details, update_full_contact_details, update_tour_bookings
from flask import jsonify
import logging


@customers_bp.route('/', methods=['GET', 'POST'])
@login_required
# @cache.cached(timeout=240)
def home_page():
    if request.method == 'GET' or request.method == "POST":
        login_user = current_user
        login_user_email = login_user.email_address
        page = request.args.get('page', 1, type=int)
        search = request.form.get('search_query')
        items_per_page = request.args.get('items_per_page', default=50, type=int)
        username = session.get('username', 'Guest')
        year = datetime.datetime.now().year
        customers = get_all_contacts_information(page, items_per_page, search)
        # available_dates= get_all_upcoming_travel_packages()
        destinations = get_all_destinations()
        states = all_states()

        customers_total = get_total_num_of_contacts()
        total_pages = math.ceil(customers_total / items_per_page)
        return render_template("homepage.html", items_per_page=items_per_page, states=states,
                               login_user_email=login_user_email, customers=customers, destinations=destinations,
                               username=username, customers_total=customers_total, page=page, total_pages=total_pages)


@customers_bp.route('/details', methods=['GET'])
@login_required
def get_customer_details():
    customer_id = request.args.get('customer_id')
    print("Requested Customer ID:", customer_id)
    # Fetching customer details from the database
    the_details = fetch_customer_details(customer_id)
    # Assuming the_details is a list of tuples and we're interested in the first tuple
    if the_details:
        customer = the_details[0]  # Extract the first tuple
        # Convert tuple to dictionary for JSON response
        customer_dict = {
            "customer_id": customer[0],
            "first_name": customer[1],
            "last_name": customer[2],
            "state_address": customer[3] if customer[3] is not None else "",
            "email_address": customer[4],
            "phone_number": customer[5]
        }
        return jsonify(customer_dict)
    else:
        return jsonify({"error": "Customer not found"}), 404


@customers_bp.route('/update_details', methods=['POST'])
@login_required
def send_update():
    customer_id = request.form.get('updatecustomer_id')
    first_name = request.form.get('updatefirst_name')
    last_name = request.form.get('updatelast_name')
    state = request.form.get('updatestate')
    email = request.form.get('updateemail')
    phone = request.form.get('updatephone')
    gender = request.form.get('updategender')

    update_full_contact_details(customer_id, first_name, last_name, email, phone, gender, state)

    return redirect(url_for("customers.home_page"))


@customers_bp.context_processor
@login_required
def context_processor():
    return dict(format_phone_number=format_phone_number)


@customers_bp.route('/delete_customer', methods=['POST'])
@login_required
def delete_customer():
    customer_id = request.form.get("customer_id")
    if not customer_id:
        return redirect(url_for("customers.home_page"))
    else:
        remove_a_paid_contact(customer_id)
        return redirect(url_for("customers.home_page"))


@customers_bp.route('/add_customer', methods=['POST'])
@login_required
def adding_new_contact():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        state = request.form.get('state')
        email = request.form.get('email')
        phone = request.form.get('phone')
        gender = request.form.get('gender')
        lead_status = request.form.get("lead_status")

        customer_exist = check_contact_exists(email)
        if not customer_exist:
            add_new_contact(first_name, last_name, email, phone, gender, state, lead_status)
            contact_id = get_contact_id(email)
            if contact_id:
                return redirect(url_for("profiles.customer_profile", contact_id=contact_id))


@customers_bp.route('/add_new_tours', methods=['POST'])
@login_required
def add_new_tours():
    if request.method == 'POST':
        tour_name = request.form.get('name')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        tour_price = request.form.get('price')
        destination = request.form.get('destination')
        tour_type = request.form.get('tour_type')
        destination_id = get_destination_id(destination)
        create_new_tour_packages(tour_name, start_date, end_date, tour_price, destination_id, tour_type)

    return redirect(url_for("customers.home_page"))


@customers_bp.route('/check-email/contact-existance', methods=['POST'])
def validate_contact_existance():
    data = request.get_json()
    email = data.get('email')
    contact_id = check_contact_exists(email)  # This function should return None if contact does not exist
    if contact_id:
        # Return JSON indicating the contact exists along with the contact_id
        return jsonify({'exists': True, 'contact_id': contact_id})
    else:
        # Return JSON indicating the contact does not exist
        return jsonify({'exists': False})
