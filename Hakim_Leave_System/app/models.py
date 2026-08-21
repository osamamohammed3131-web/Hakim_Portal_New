from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text
from app.database import Base

class University(Base):
    __tablename__ = "universities"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    logo_path = Column(String(500))
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    id = Column(Integer, primary_key=True)
    request_number = Column(String(50), unique=True, nullable=False)
    student_name = Column(String(255), nullable=False)
    national_id = Column(String(50), nullable=False)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    absence_date = Column(Date, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days_count = Column(Integer, nullable=False)
    request_type = Column(String(50), nullable=False)
    notes = Column(Text)
    status = Column(String(30), default="registered")
    verification_token = Column(String(128), unique=True, nullable=False)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100))
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100))
    entity_id = Column(Integer)
    ip_address = Column(String(64))
    created_at = Column(DateTime, default=datetime.utcnow)
