from models import Customer, db


def add_new_customer(name, email, phone_number, adress):
    customer = Customer()
    customer.full_name = name
    customer.email = email
    customer.phone_number = phone_number
    customer.adress = adress
    
    db.session.add(customer)
    db.session.commit()
