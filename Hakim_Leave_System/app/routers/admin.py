from datetime import date
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import University, LeaveRequest
from app.schemas import LeaveCreate
from app.services.request_service import create_request
from app.services.request_service import next_request_number
from app.services.university_service import active_universities
from app.services.pdf_service import build_pdf
router=APIRouter(prefix="/admin")

@router.get("/dashboard",response_class=HTMLResponse)
async def dashboard(request:Request,db:Session=Depends(get_db)):
    from app.main import templates
    return templates.TemplateResponse("admin/dashboard.html",{"request":request,"count":db.query(LeaveRequest).count(),"universities":db.query(University).count()})

@router.get("/requests/new",response_class=HTMLResponse)
async def new_request(request:Request,db:Session=Depends(get_db)):
    from app.main import templates
    return templates.TemplateResponse("admin/request_form.html",{"request":request,"universities":active_universities(db)})

@router.post("/requests/new")
async def create_route(request:Request,student_name:str=Form(...),national_id:str=Form(...),university_id:int=Form(...),absence_date:str=Form(...),start_date:str=Form(...),end_date:str=Form(...),request_type:str=Form("إجازة"),notes:str=Form(""),db:Session=Depends(get_db)):
    data=LeaveCreate(student_name=student_name,national_id=national_id,university_id=university_id,absence_date=date.fromisoformat(absence_date),start_date=date.fromisoformat(start_date),end_date=date.fromisoformat(end_date),request_type=request_type,notes=notes or None)
    obj=create_request(db,data); return RedirectResponse(f"/admin/requests/{obj.id}",status_code=303)

@router.get("/requests/{request_id}",response_class=HTMLResponse)
async def details(request:Request,request_id:int,db:Session=Depends(get_db)):
    from app.main import templates
    obj=db.query(LeaveRequest).filter(LeaveRequest.id==request_id).first()
    uni=db.query(University).filter(University.id==obj.university_id).first() if obj else None
    return templates.TemplateResponse("admin/request_details.html",{"request":request,"data":{"request":obj,"university":uni}})

@router.get("/requests/{request_id}/pdf")
async def pdf(request_id:int,db:Session=Depends(get_db)):
    obj=db.query(LeaveRequest).filter(LeaveRequest.id==request_id).first()
    if not obj: return HTMLResponse("Not found",status_code=404)
    uni=db.query(University).filter(University.id==obj.university_id).first()
    data=build_pdf(obj,uni.name if uni else "")
    return StreamingResponse(iter([data]),media_type="application/pdf",headers={"Content-Disposition":f'attachment; filename="{obj.request_number}.pdf"'})
