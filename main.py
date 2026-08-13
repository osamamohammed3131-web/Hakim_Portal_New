import os

from flask import Flask
from extensions import db


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///hakim.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# تحميل نماذج قاعدة البيانات
from models import User, StudyPlan, Subject, Lecture


@app.route("/")
def home():
    return "Hakim Academy"


@app.route("/health")
def health():
    return "OK"
