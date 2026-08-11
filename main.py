from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    # استدعاء جدول المستخدمين لضمان إنشائه تلقائياً
    from models import User

    with app.app_context():
        db.create_all()

    @app.route('/')
    def home():
        return "مرحباً بك في منصة حكيم الأكاديمية - النواة وقاعدة البيانات تعمل بنجاح تام!"

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
