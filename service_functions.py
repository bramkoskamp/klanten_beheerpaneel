from models import Service, db


def add_new_service(name, price, description):
    service = Service()
    service.name = name
    service.price = price
    service.description = description
    
    db.session.add(service)
    db.session.commit()
