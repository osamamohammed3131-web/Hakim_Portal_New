from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import LeaveRequest, University
from app.security import mask_id
router=APIRouter()

@router.get("/lookup",response_class=HTMLResponse)
async def lookup_page(request:Request):
    from app.main import templates
    return templates.TemplateResponse("public/lookup.html",{"request":request})

@router.post("/lookup",response_class=HTMLResponse)
async def lookup(request:Request,request_number:str=Form(...),national_id:str=Form(...),db:Session=Depends(get_db)):
    from app.main import templates
    obj=db.query(LeaveRequest).filter(LeaveRequest.request_number==request_number.strip(),LeaveRequest.national_id==national_id.strip()).first()
    uni=db.query(University).filter(University.id==obj.university_id).first() if obj else None
    return templates.TemplateResponse("public/lookup.html",{"request":request,"data":{"request":obj,"university":uni,"masked_id":mask_id(obj.national_id)} if obj else None})

@router.get("/verify/{token}",response_class=HTMLResponse)
async def verify(request:Request,token:str,db:Session=Depends(get_db)):
    from app.main import templates
    obj=db.query(LeaveRequest).filter(LeaveRequest.verification_token==token).first()
    uni=db.query(University).filter(University.id==obj.university_id).first() if obj else None
    return templates.TemplateResponse("public/verify.html",{"request":request,"data":{"request":obj,"university":uni} if obj else None})
