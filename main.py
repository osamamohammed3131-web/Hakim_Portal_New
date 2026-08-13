import os

from flask import Flask, render_template, session, redirect, url_for

from extensions import db
from api import api
from auth import auth
from dashboard import dashboard


app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "change-this-secret-key"
)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///hakim.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)

app.register_blueprint(api)
app.register_blueprint(auth)
app.register_blueprint(dashboard)


from models import User, StudyPlan, Subject, Lecture, ScheduleItem


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/register")
def register_page():
    return render_template("register.html")


@app.route("/student")
def student_page():
    if not session.get("user_id"):
        return redirect(url_for("login_page"))

    user = db.session.get(User, session["user_id"])

    if not user or not user.is_active:
        session.clear()
        return redirect(url_for("login_page"))

    if user.role != "student":
        return redirect(url_for("admin_page"))

    return render_template(
        "student.html",
        user=user
    )


@app.route("/admin")
def admin_page():
    if not session.get("user_id"):
        return redirect(url_for("login_page"))

    user = db.session.get(User, session["user_id"])

    if not user or not user.is_active:
        session.clear()
        return redirect(url_for("login_page"))

    if user.role not in ("admin", "superadmin"):
        return redirect(url_for("student_page"))

    return render_template(
        "admin.html",
        user=user
    )


@app.route("/health")
def health():
    return "OK"


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000))
    )
