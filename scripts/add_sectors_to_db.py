from models import db, connect_db, Sector
from app import app

connect_db(app)

SECTORS = ["Education", "Transport", "Health", "Finance", "Social", "Entertainment", "Media", "Religion", "Culture", "Telecommunication", "Agriculture", "Construction", "Food", "Energy Industry"]

def add_to_db():
    sectors = [Sector(name=sector) for sector in SECTORS]
    db.session.add_all(sectors)
    db.session.commit()

# uncomment the following to run the function
add_to_db()
