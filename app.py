import datetime
import flask
from flask import render_template, send_file, request, redirect, url_for
from dotenv import load_dotenv
from customer_functions import add_new_customer
from forms.customer_form import CustomerForm
from forms.invoice_form import InvoiceForm
from forms.service_form import ServiceForm
from invoice_functions import generate_pdf
from service_functions import add_new_service
from models import Customer, Service, db
import os
import shutil
import time

# Load environment variables
load_dotenv()

app = flask.Flask(__name__)
app.secret_key = 'VS6HZ25p6X39vfHid6K5GT8IfOEgJ7KT'
app.config['TEMPLATES_AUTO_RELOAD'] = True

# ----------------------------------------
# DATABASE PAD (WERKT IN EXE + LOKAAL)
# ----------------------------------------
import sys
    
# Voor PyInstaller compatibiliteit
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_DIR = os.path.join(BASE_DIR, "data")
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, "database.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
db.init_app(app)

# Maak database indien nodig
with app.app_context():
    db.create_all()


# ----------------------------------------
# AUTOMATISCHE BACKUP (1x per 24 uur)
# ----------------------------------------
def backup_database():
    backup_dir = os.path.join(BASE_DIR, "backups")
    os.makedirs(backup_dir, exist_ok=True)

    latest_backup = os.path.join(backup_dir, "database_latest.db")

    # Eerste keer → meteen backup
    if not os.path.exists(latest_backup):
        shutil.copy(DB_PATH, latest_backup)
        return

    # 24 uur = 86400 seconden
    if time.time() - os.path.getmtime(latest_backup) > 86400:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        shutil.copy(DB_PATH, os.path.join(backup_dir, f"database_{timestamp}.db"))
        shutil.copy(DB_PATH, latest_backup)
        
        # Maximaal 30 backups behouden (excl. database_latest.db)
        backup_files = sorted([
            f for f in os.listdir(backup_dir) 
            if f.startswith("database_") and f.endswith(".db") and f != "database_latest.db"
        ])
        
        # Verwijder oudste backup(s) als er meer dan 30 zijn
        while len(backup_files) > 30:
            oldest = backup_files.pop(0)
            os.remove(os.path.join(backup_dir, oldest))
            print(f"Oude backup verwijderd: {oldest}")


# BACKUP UITVOEREN BIJ STARTEN APP
backup_database()


# ----------------------------------------
# ROUTES
# ----------------------------------------

@app.route("/", methods=['GET'])
def index():
    page = request.args.get("page", 1, type=int)
    customers = Customer.query.paginate(page=page, per_page=10)
    return render_template("index.html", customers=customers)


@app.route("/new_invoice", methods=['GET', 'POST'])
def new_invoice():
    form = InvoiceForm()
    form.customer.choices = [(c.id, c.full_name) for c in Customer.query.all()]
    form.service.choices = [(s.id, f"{s.name} (€{s.price})") for s in Service.query.all()]

    if form.validate_on_submit():
        customer_id = form.customer.data
        service_id = form.service.data
        vat_rate = form.vat_rate.data

        selected_customer = Customer.query.get(customer_id)
        selected_service = Service.query.get(service_id)

        price = selected_service.price
        service_name = selected_service.name
        service_description = selected_service.description
        customer_name = selected_customer.full_name
        customer_adress = selected_customer.adress

        sender = {
            "name": os.getenv('OWNER_NAME', 'Teun Elburg'),
            "address": os.getenv('OWNER_ADDRESS', 'Maurits prins straat 7'),
            "country": "Nederland",
            "logo_path": "static/logo/logo.png"
        }

        items = [{
            'title': service_name,
            "description": service_description,
            "amount": 1,
            "price": price,
            "tax": vat_rate
        }]

        buffer = generate_pdf(
            doc_type="invoice",
            customer_name=customer_name,
            customer_address=customer_adress,
            customer_country="NL",
            items=items,
            sender_info=sender
        )

        filename = f"factuur_{customer_name.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"
        return send_file(buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")

    return render_template("invoice.html", form=form, type='Factuur')


@app.route("/new_quote", methods=['GET', 'POST'])
def new_quote():
    form = InvoiceForm()
    form.customer.choices = [(c.id, c.full_name) for c in Customer.query.all()]
    form.service.choices = [(s.id, f"{s.name} (€{s.price})") for s in Service.query.all()]

    if form.validate_on_submit():
        service_id = form.service.data
        customer_id = form.customer.data
        vat_rate = form.vat_rate.data

        selected_customer = Customer.query.get(customer_id)
        selected_service = Service.query.get(service_id)

        customer_name = selected_customer.full_name
        customer_adress = selected_customer.adress
        price = selected_service.price

        items = [{
            "description": selected_service.name,
            "amount": 1,
            "price": price,
            "tax": vat_rate
        }]

        sender = {
            "name": os.getenv('OWNER_NAME', 'Teun Elburg'),
            "address": os.getenv('OWNER_ADDRESS', 'Maurits prins straat 7'),
            "country": "Nederland"
        }

        buffer = generate_pdf(
            doc_type="quote",
            customer_name=customer_name,
            customer_address=customer_adress,
            customer_country="NL",
            items=items,
            sender_info=sender
        )

        filename = f"offerte_{customer_name.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"
        return send_file(buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")

    return render_template("invoice.html", form=form, type='Offerte')


@app.route("/add_customer", methods=['GET', 'POST'])
def add_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        add_new_customer(
            form.full_name.data,
            form.email.data,
            form.phone_number.data,
            form.adress.data
        )
        return redirect(url_for('index'))

    return render_template('new_customer.html', form=form)


@app.route("/customers/<int:id>/edit", methods=['GET', 'POST'])
def edit_customer(id):
    customer = Customer.query.get(id)
    customer_form = CustomerForm(obj=customer)

    if customer_form.validate_on_submit():
        customer.full_name = customer_form.full_name.data
        customer.email = customer_form.email.data
        customer.phone_number = customer_form.phone_number.data
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('new_customer.html', form=customer_form)


@app.route("/customers/<int:id>", methods=["POST"])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/services", methods=['GET'])
def services():
    page = request.args.get("page", 1, type=int)
    services = Service.query.paginate(page=page, per_page=10)
    return render_template('services.html', services=services)


@app.route("/add_service", methods=['GET', 'POST'])
def add_service_route():
    form = ServiceForm()
    if form.validate_on_submit():
        add_new_service(form.name.data, form.price.data, form.description.data)
        return redirect(url_for('services'))

    return render_template('new_service.html', form=form)


@app.route("/service/<int:id>/edit", methods=['GET', 'POST'])
def edit_service(id):
    service = Service.query.get(id)
    service_form = ServiceForm(obj=service)

    if service_form.validate_on_submit():
        service.name = service_form.name.data
        service.price = service_form.price.data
        service.description = service_form.description.data
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('new_service.html', form=service_form)


@app.route("/service/<int:id>", methods=["POST"])
def delete_service(id):
    service = Service.query.get_or_404(id)
    db.session.delete(service)
    db.session.commit()
    return redirect(url_for("services"))


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )

