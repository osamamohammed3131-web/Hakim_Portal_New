import os

from flask import Flask
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


from models import User, StudyPlan, Subject, Lecture


@app.route("/")
def home():
    return "Hakim Academy"


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
