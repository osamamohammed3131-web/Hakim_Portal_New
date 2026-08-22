from __future__ import annotations

import os
import secrets
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import (
    FastAPI,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
    File,
)
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from jinja2 import Environment, FileSystemLoader, select_autoescape


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
IMAGES_DIR = STATIC_DIR / "images"

TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. APPLICATION
# ============================================================

app = FastAPI(
    title="Hakim Leave System",
    description="Hakim Platform Leave / Request System",
    version="1.0.0",
)


# ============================================================
# 3. SECURITY / SESSION
# ============================================================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "CHANGE_THIS_SECRET_KEY_IN_RENDER"
)

ADMIN_USERNAME = os.getenv(
    "ADMIN_USERNAME",
    "admin"
)

ADMIN_PASSWORD = os.getenv(
    "ADMIN_PASSWORD",
    "CHANGE_THIS_PASSWORD"
)


app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="hakim_session",
    same_site="lax",
    https_only=False,
)


# ============================================================
# 4. STATIC FILES
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)


# ============================================================
# 5. JINJA2
# ============================================================

templates = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(
        enabled_extensions=("html", "xml")
    ),
)


# ============================================================
# 6. DATABASE
# ============================================================

DATABASE_PATH = BASE_DIR / "hakim.db"


def get_db():
    connection = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    return connection


def init_database():
    db = get_db()

    cursor = db.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS universities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            logo_path TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_number TEXT UNIQUE NOT NULL,
            student_name TEXT NOT NULL,
            national_id TEXT NOT NULL,
            university_id INTEGER,
            absence_date TEXT,
            start_date TEXT,
            end_date TEXT,
            days_count INTEGER DEFAULT 1,
            request_type TEXT,
            notes TEXT,
            status TEXT DEFAULT 'registered',
            verification_token TEXT UNIQUE NOT NULL,
            created_by TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (university_id)
                REFERENCES universities(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            entity_type TEXT,
            entity_id INTEGER,
            ip_address TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    db.commit()
    db.close()


init_database()


# ============================================================
# 7. HELPERS
# ============================================================

def now():
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def render_template(
    template_name: str,
    request: Request,
    **context
):
    template = templates.get_template(template_name)

    context["request"] = request

    html = template.render(**context)

    return HTMLResponse(content=html)


def is_admin(request: Request) -> bool:
    return bool(
        request.session.get("admin_authenticated")
    )


def require_admin(request: Request):
    if not is_admin(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=303
        )

    return None


def generate_request_number():
    year = datetime.now().year

    db = get_db()

    cursor = db.cursor()

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM leave_requests
        WHERE request_number LIKE ?
        """,
        (f"HL-{year}-%",)
    )

    total = cursor.fetchone()["total"] + 1

    db.close()

    return f"HL-{year}-{total:06d}"


def calculate_days(
    start_date: str,
    end_date: str
) -> int:

    start = datetime.strptime(
        start_date,
        "%Y-%m-%d"
    )

    end = datetime.strptime(
        end_date,
        "%Y-%m-%d"
    )

    if end < start:
        raise ValueError(
            "تاريخ النهاية لا يمكن أن يكون قبل تاريخ البداية."
        )

    return (end - start).days + 1


def write_audit(
    request: Request,
    action: str,
    entity_type: str,
    entity_id: Optional[int] = None
):
    db = get_db()

    cursor = db.cursor()

    client_ip = None

    if request.client:
        client_ip = request.client.host

    cursor.execute(
        """
        INSERT INTO audit_logs
        (
            username,
            action,
            entity_type,
            entity_id,
            ip_address,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            request.session.get(
                "admin_username",
                "anonymous"
            ),
            action,
            entity_type,
            entity_id,
            client_ip,
            now(),
        )
    )

    db.commit()
    db.close()


# ============================================================
# 8. HOME
# ============================================================

@app.get(
    "/",
    response_class=HTMLResponse
)
async def home(request: Request):

    template_path = (
        TEMPLATES_DIR
        / "public"
        / "index.html"
    )

    if template_path.exists():

        return render_template(
            "public/index.html",
            request
        )

    return HTMLResponse(
        """
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>منصة حكيم</title>
        </head>
        <body>
            <h1>منصة حكيم</h1>
            <p>نظام الإجازات والطلبات.</p>
            <a href="/lookup">الاستعلام عن طلب</a>
        </body>
        </html>
        """
    )


# ============================================================
# 9. PUBLIC LOOKUP
# ============================================================

@app.get(
    "/lookup",
    response_class=HTMLResponse
)
async def lookup_page(request: Request):

    template_path = (
        TEMPLATES_DIR
        / "public"
        / "lookup.html"
    )

    if template_path.exists():

        return render_template(
            "public/lookup.html",
            request,
            result=None,
            error=None
        )

    return HTMLResponse(
        """
        <h1>الاستعلام عن طلب</h1>
        <form method="post">
            <input name="request_number"
                   placeholder="رقم الطلب"
                   required>
            <input name="national_id"
                   placeholder="رقم الهوية / الإقامة"
                   required>
            <button type="submit">
                استعلام
            </button>
        </form>
        """
    )


@app.post(
    "/lookup",
    response_class=HTMLResponse
)
async def lookup_request(
    request: Request,
    request_number: str = Form(...),
    national_id: str = Form(...)
):

    db = get_db()

    cursor = db.cursor()

    cursor.execute(
        """
        SELECT
            lr.*,
            u.name AS university_name,
            u.logo_path AS university_logo
        FROM leave_requests lr
        LEFT JOIN universities u
            ON u.id = lr.university_id
        WHERE lr.request_number = ?
          AND lr.national_id = ?
        LIMIT 1
        """,
        (
            request_number.strip(),
            national_id.strip(),
        )
    )

    result = cursor.fetchone()

    db.close()

    if not result:

        return render_template(
            "public/lookup.html",
            request,
            result=None,
            error="لم يتم العثور على طلب مطابق للبيانات المدخلة."
        )

    result = dict(result)

    return render_template(
        "public/lookup.html",
        request,
        result=result,
        error=None
    )


# ============================================================
# 10. QR VERIFICATION
# ============================================================

@app.get(
    "/verify/{token}",
    response_class=HTMLResponse
)
async def verify_request(
    request: Request,
    token: str
):

    db = get_db()

    cursor = db.cursor()

    cursor.execute(
        """
        SELECT
            lr.*,
            u.name AS university_name,
            u.logo_path AS university_logo
        FROM leave_requests lr
        LEFT JOIN universities u
            ON u.id = lr.university_id
        WHERE lr.verification_token = ?
        LIMIT 1
        """,
        (token,)
    )

    result = cursor.fetchone()

    db.close()

    if not result:
        raise HTTPException(
            status_code=404,
            detail="الطلب غير موجود."
        )

    result = dict(result)

    template_path = (
        TEMPLATES_DIR
        / "public"
        / "verify.html"
    )

    if template_path.exists():

        return render_template(
            "public/verify.html",
            request,
            result=result
        )

    status_text = (
        "الطلب ملغى."
        if result["status"] == "cancelled"
        else "الطلب مسجل."
    )

    return HTMLResponse(
        f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>التحقق من الطلب</title>
        </head>
        <body>
            <h1>التحقق من الطلب</h1>
            <p>رقم الطلب: {result["request_number"]}</p>
            <p>اسم الطالب: {result["student_name"]}</p>
            <p>{status_text}</p>
        </body>
        </html>
        """
    )


# ============================================================
# 11. ADMIN LOGIN
# ============================================================

@app.get(
    "/admin/login",
    response_class=HTMLResponse
)
async def admin_login_page(
    request: Request
):

    if is_admin(request):

        return RedirectResponse(
            url="/admin/dashboard",
            status_code=303
        )

    return render_template(
        "admin/login.html",
        request,
        error=None
    )


@app.post(
    "/admin/login",
    response_class=HTMLResponse
)
async def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):

    if (
        secrets.compare_digest(
            username,
            ADMIN_USERNAME
        )
        and
        secrets.compare_digest(
            password,
            ADMIN_PASSWORD
        )
    ):

        request.session["admin_authenticated"] = True
        request.session["admin_username"] = username

        write_audit(
            request,
            "login",
            "user"
        )

        return RedirectResponse(
            url="/admin/dashboard",
            status_code=303
        )

    return render_template(
        "admin/login.html",
        request,
        error="اسم المستخدم أو كلمة المرور غير صحيحة."
    )


@app.get("/admin/logout")
async def admin_logout(
    request: Request
):

    write_audit(
        request,
        "logout",
        "user"
    )

    request.session.clear()

    return RedirectResponse(
        url="/admin/login",
        status_code=303
    )


# ============================================================
# 12. ADMIN DASHBOARD
# ============================================================

@app.get(
    "/admin/dashboard",
    response_class=HTMLResponse
)
async def admin_dashboard(
    request: Request
):

    redirect = require_admin(request)

    if redirect:
        return redirect

    db = get_db()

    cursor = db.cursor()

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM leave_requests
        """
    )

    total_requests = cursor.fetchone()["total"]

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM leave_requests
        WHERE status = 'registered'
        """
    )

    registered_requests = cursor.fetchone()["total"]

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM leave_requests
        WHERE status = 'cancelled'
        """
    )

    cancelled_requests = cursor.fetchone()["total"]

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM universities
        WHERE is_active = 1
        """
    )

    total_universities = cursor.fetchone()["total"]

    db.close()

    return render_template(
        "admin/dashboard.html",
        request,
        total_requests=total_requests,
        registered_requests=registered_requests,
        cancelled_requests=cancelled_requests,
        total_universities=total_universities,
    )


# ============================================================
# 13. ADMIN REQUESTS LIST
# ============================================================

@app.get(
    "/admin/requests",
    response_class=HTMLResponse
)
async def admin_requests(
    request: Request,
    q: str = Query(default="")
):

    redirect = require_admin(request)

    if redirect:
        return redirect

    db = get_db()

    cursor = db.cursor()

    search = q.strip()

    if search:

        pattern = f"%{search}%"

        cursor.execute(
            """
            SELECT
                lr.*,
                u.name AS university_name
            FROM leave_requests lr
            LEFT JOIN universities u
                ON u.id = lr.university_id
            WHERE
                lr.request_number LIKE ?
                OR lr.student_name LIKE ?
                OR lr.national_id LIKE ?
                OR u.name LIKE ?
            ORDER BY lr.id DESC
            """,
            (
                pattern,
                pattern,
                pattern,
                pattern,
            )
        )

    else:

        cursor.execute(
            """
            SELECT
                lr.*,
                u.name AS university_name
            FROM leave_requests lr
            LEFT JOIN universities u
                ON u.id = lr.university_id
            ORDER BY lr.id DESC
            """
        )

    rows = cursor.fetchall()

    db.close()

    requests = []

    for row in rows:

        item = dict(row)

        item["university"] = {
            "name": item.get(
                "university_name"
            )
        }

        requests.append(item)

    return render_template(
        "admin/requests.html",
        request,
        requests=requests,
        q=search
    )


# ============================================================
# 14. ADMIN REQUEST DETAILS
# ============================================================

@app.get(
    "/admin/requests/{request_id}",
    response_class=HTMLResponse
)
async def admin_request_details(
    request: Request,
    request_id: int
):

    redirect = require_admin(request)

    if redirect:
        return redirect

    db = get_db()

    cursor = db.cursor()

    cursor.execute(
        """
        SELECT
            lr.*,
            u.name AS university_name,
            u.logo_path AS university_logo
        FROM leave_requests lr
        LEFT JOIN universities u
            ON u.id = lr.university_id
        WHERE lr.id = ?
        LIMIT 1
        """,
        (request_id,)
    )

    row = cursor.fetchone()

    db.close()

    if not row:

        raise HTTPException(
            status_code=404,
            detail="الطلب غير موجود."
        )

    item = dict(row)

    item["university"] = {
        "name": item.get(
            "university_name"
        ),
        "logo_path": item.get(
            "university_logo"
        )
    }

    return render_template(
        "admin/request_details.html",
        request,
        item=item,
        request_data=item
    )


# ============================================================
# 15. CREATE REQUEST PAGE
# ============================================================

@app.get(
    "/admin/requests/new",
    response_class=HTMLResponse
)
async def new_request_page(
    request: Request
):

    redirect = require_admin(request)

    if redirect:
        return redirect

    db = get_db()

    cursor = db.cursor()

    cursor.execute(
        """
        SELECT *
        FROM universities
        WHERE is_active = 1
        ORDER BY name
        """
    )

    universities = [
        dict(row)
        for row in cursor.fetchall()
    ]

    db.close()

    return render_template(
        "admin/request_form.html",
        request,
        universities=universities,
        error=None,
        item=None
    )


# ============================================================
# 16. CREATE REQUEST
# ============================================================

@app.post(
    "/admin/requests",
    response_class=HTMLResponse
)
async def create_request(
    request: Request,
    student_name: str = Form(...),
    national_id: str = Form(...),
    university_id: int = Form(...),
    absence_date: str = Form(""),
    start_date: str = Form(...),
    end_date: str = Form(...),
    request_type: str = Form("غياب"),
    notes: str = Form("")
):

    redirect = require_admin(request)

    if redirect:
        return redirect

    try:

        days_count = calculate_days(
            start_date,
            end_date
        )

    except ValueError as exc:

        db = get_db()

        cursor = db.cursor()

        cursor.execute(
            """
            SELECT *
            FROM universities
            WHERE is_active = 1
            ORDER BY name
            """
        )

        universities = [
            dict(row)
            for row in cursor.fetchall()
        ]

        db.close()

        return render_template(
            "admin/request_form.html",
            request,
            universities=universities,
            error=str(exc),
            item=None
        )

    request_number = generate_request_number()

    verification_token = secrets.token_urlsafe(
        32
    )

    current_time = now()

    db = get_db()

    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO leave_requests
        (
            request_number,
            student_name,
            national_id,
            university_id,
            absence_date,
            start_date,
            end_date,
            days_count,
            request_type,
            notes,
            status,
            verification_token,
            created_by,
            created_at,
            updated_at
