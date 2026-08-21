from datetime import date
from pydantic import BaseModel, Field
class LeaveCreate(BaseModel):
    student_name: str = Field(min_length=1, max_length=255)
    national_id: str = Field(min_length=1, max_length=50)
    university_id: int
    absence_date: date
    start_date: date
    end_date: date
    request_type: str = "إجازة"
    notes: str | None = None
