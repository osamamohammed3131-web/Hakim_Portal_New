import os

from flask import Flask, render_template, session, redirect, url_for
from sqlalchemy import inspect, text

from extensions import db
from api import api
from auth import auth
from dashboard import dashboard


app = Flask(__name__)


# =========================================================
# إعدادات التطبيق
# =========================================================

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "change-this-secret-key"
)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///hakim.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# =========================================================
# ربط قاعدة البيانات
# =========================================================

db.init_app(app)


# =========================================================
# استيراد الموديلات
# =========================================================

from models import (
    User,
    StudyPlan,
    Subject,
    Lecture,
    ScheduleItem
)


# =========================================================
# إنشاء الجداول وترقية قاعدة البيانات
# =========================================================

with app.app_context():

    # إنشاء الجداول إذا لم تكن موجودة
    db.create_all()

    # فحص أعمدة جدول users
    inspector = inspect(db.engine)

    columns = inspector.get_columns("users")

    column_names = {
        column["name"]
        for column in columns
    }

    # إضافة status إذا لم يكن موجودًا
    if "status" not in column_names:

        db.session.execute(
            text("""
                ALTER TABLE users
                ADD COLUMN status VARCHAR(30)
                NOT NULL
                DEFAULT 'active'
            """)
        )

        db.session.commit()


# =========================================================
# تسجيل الـ Blueprints
# =========================================================

app.register_blueprint(api)
app.register_blueprint(auth)
app.register_blueprint(dashboard)


# =========================================================
# الصفحة الرئيسية
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# صفحة تسجيل الدخول
# =========================================================

@app.route("/login")
def login_page():

    return render_template(
        "login.html"
    )


# =========================================================
# صفحة إنشاء الحساب
# =========================================================

@app.route("/register")
def register_page():

    return render_template(
        "register.html"
    )


# =========================================================
# صفحة الطالب
# =========================================================

@app.route("/student")
def student_page():

    if not session.get("user_id"):

        return redirect(
            url_for("login_page")
        )


    user = db.session.get(
        User,
        session["user_id"]
    )


    if not user or not user.is_active:

        session.clear()

        return redirect(
            url_for("login_page")
        )


    if user.role != "student":

        return redirect(
            url_for("admin_page")
        )


    return render_template(
        "student.html",
        user=user
    )


# =========================================================
# صفحة المشرف
# =========================================================

@app.route("/admin")
def admin_page():

    if not session.get("user_id"):

        return redirect(
            url_for("login_page")
        )


    user = db.session.get(
        User,
        session["user_id"]
    )


    if not user or not user.is_active:

        session.clear()

        return redirect(
            url_for("login_page")
        )


    if user.role not in (
        "admin",
        "superadmin"
    ):

        return redirect(
            url_for("student_page")
        )


    return render_template(
        "admin.html",
        user=user
    )


# =========================================================
# فحص حالة السيرفر
# =========================================================

@app.route("/health")
def health():

    return "OK"


# =========================================================
# تشغيل التطبيق
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(
            os.getenv(
                "PORT",
                5000
            )
        )
    )
