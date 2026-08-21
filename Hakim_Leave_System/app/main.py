from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import Base, engine
from app.routers import public, admin

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Hakim Leave / Request System")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
app.include_router(public.router)
app.include_router(admin.router)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("public/index.html", {"request": request})
