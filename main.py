import os

from flask import Flask, render_template, session, redirect, url_for
from sqlalchemy import text, inspect

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
# إنشاء الجداول وتحديث قاعدة البيانات
# =========================================================

with app.app_context():

    # إنشاء الجداول الجديدة إذا لم تكن موجودة
    db.create_all()


    # -----------------------------------------------------
    # معرفة نوع قاعدة البيانات
    # -----------------------------------------------------

    engine = db.engine
    inspector = inspect(engine)


    # -----------------------------------------------------
    # جدول users
    # -----------------------------------------------------

    if inspector.has_table("users"):

        user_columns = {
            column["name"]
            for column in inspector.get_columns("users")
        }


        # -------------------------------------------------
        # إضافة status إذا كان غير موجود
        # -------------------------------------------------

        if "status" not in user_columns:

            if engine.dialect.name == "postgresql":

                db.session.execute(
                    text("""
                        ALTER TABLE users
                        ADD COLUMN status VARCHAR(30)
                        NOT NULL DEFAULT 'active'
                    """)
                )

            else:

                db.session.execute(
                    text("""
                        ALTER TABLE users
                        ADD COLUMN status VARCHAR(30)
                        NOT NULL DEFAULT 'active'
                    """)
                )


        # -------------------------------------------------
        # إضافة study_plan_id إذا كان غير موجود
        # -------------------------------------------------

        if "study_plan_id" not in user_columns:

            db.session.execute(
                text("""
                    ALTER TABLE users
                    ADD COLUMN study_plan_id INTEGER
                """)
            )


        db.session.commit()


# =========================================================
# تسجيل الـ Blueprints
# =========================================================

app.register_blueprint(api)

app.register_blueprint(auth)

app.register_blueprint(dashboard)# =========================================================
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

    return "OK"# =========================================================
# API لفحص حالة التطبيق وقاعدة البيانات
# =========================================================

@app.route("/database-health")
def database_health():

    try:

        db.session.execute(
            text("SELECT 1")
        )

        return {
            "status": "ok",
            "database": "connected"
        }


    except Exception as error:

        db.session.rollback()

        return {
            "status": "error",
            "database": "disconnected",
            "error": str(error)
        }, 500


# =========================================================
# معالجة أخطاء قاعدة البيانات أثناء الطلبات
# =========================================================

@app.errorhandler(500)
def internal_server_error(error):

    try:
        db.session.rollback()
    except Exception:
        pass

    return {
        "error": "حدث خطأ داخلي في الخادم"
    }, 500


# =========================================================
# تنظيف جلسة قاعدة البيانات بعد الطلب
# =========================================================

@app.teardown_appcontext
def shutdown_session(exception=None):

    if exception:

        try:
            db.session.rollback()
        except Exception:
            pass


# =========================================================
# معلومات التطبيق
# =========================================================

@app.route("/app-info")
def app_info():

    return {
        "name": "Hakim Academy",
        "status": "running",
        "features": [
            "students",
            "study_plans",
            "subjects",
            "lectures",
            "smart_schedule"
        ]
    }# =========================================================
# تشغيل التطبيق
# =========================================================

if __name__ == "__main__":

    port = int(
        os.getenv(
            "PORT",
            5000
        )
    )


    app.run(
        host="0.0.0.0",
        port=port
    )
