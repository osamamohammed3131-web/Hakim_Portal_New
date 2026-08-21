from datetime import date
from sqlalchemy.orm import Session
from app.models import LeaveRequest
from app.security import new_token

def next_request_number(db: Session):
    return f"HL-{date.today().year}-{db.query(LeaveRequest).count()+1:06d}"

def create_request(db, data, created_by="admin"):
    if data.end_date < data.start_date:
        raise ValueError("نهاية الفترة لا يمكن أن تسبق بدايتها")
    obj = LeaveRequest(
        request_number=next_request_number(db), student_name=data.student_name,
        national_id=data.national_id, university_id=data.university_id,
        absence_date=data.absence_date, start_date=data.start_date,
        end_date=data.end_date, days_count=(data.end_date-data.start_date).days+1,
        request_type=data.request_type, notes=data.notes,
        verification_token=new_token(), created_by=created_by)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj
