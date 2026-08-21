from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from app.config import BASE_URL
from app.services.qr_service import make_qr_bytes

def build_pdf(obj, university_name):
    b=BytesIO(); c=canvas.Canvas(b,pagesize=A4); w,h=A4
    c.setFont("Helvetica-Bold",16); c.drawString(50,h-55,"Hakim Platform - Request Registration")
    c.setFont("Helvetica",11); y=h-95
    for label,value in [
        ("Request",obj.request_number),("Student",obj.student_name),
        ("ID",obj.national_id),("University",university_name),
        ("Absence date",str(obj.absence_date)),("From",str(obj.start_date)),
        ("To",str(obj.end_date)),("Days",str(obj.days_count)),
        ("Type",obj.request_type),("Status",obj.status)]:
        c.drawString(50,y,f"{label}: {value}"); y-=22
    url=f"{BASE_URL.rstrip('/')}/verify/{obj.verification_token}"
    c.drawImage(ImageReader(BytesIO(make_qr_bytes(url))),50,80,120,120)
    c.setFont("Helvetica",8); c.drawString(185,130,url)
    c.drawString(50,55,"Document issued by Hakim Platform to prove request registration.")
    c.save(); return b.getvalue()
