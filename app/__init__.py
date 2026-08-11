from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # تهيئة قاعدة البيانات
    db.init_app(app)

    # مسار تجريبي للتأكد من عمل النواة الأولى للمنصة
    @app.route('/')
    def home():
        return "مرحباً بك في منصة حكيم الأكاديمية - تعمل بنجاح من الصفر!"

    return app
