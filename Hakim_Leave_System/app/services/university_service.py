from app.models import University
def active_universities(db):
    return db.query(University).filter(University.is_active==1).order_by(University.name).all()
