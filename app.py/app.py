import os

from flask import Flask, render_template

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


@app.route("/health")
def health():
    return "OK"


with app.app_context():
    db.create_all()

    admin_username = os.getenv(
        "ADMIN_USERNAME",
        "admin"
    )

    admin_email = os.getenv(
        "ADMIN_EMAIL",
        "admin@hakim.academy"
    )

    admin_password = os.getenv(
        "ADMIN_PASSWORD"
    )

    if admin_password:
        admin = User.query.filter_by(
            username=admin_username
        ).first()

        if not admin:
            admin = User(
                username=admin_username,
                email=admin_email,
                role="admin"
            )

            admin.set_password(admin_password)

            db.session.add(admin)

        else:
            admin.role = "admin"
            admin.email = admin_email
            admin.set_password(admin_password)

        db.session.commit()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000))
    )
