from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    # استدعاء جدول المستخدمين لإنشائه تلقائياً
    from models import User
    
    # تسجيل مسارات المصادقة
    from auth import auth_bp
    app.register_blueprint(auth_bp)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def home():
        return '''
            <div style="text-align: center; font-family: Tahoma; margin-top: 50px;">
                <h1>مرحباً بك في منصة حكيم الأكاديمية</h1>
                <p>النواة وقاعدة البيانات ونظام المصادقة يعملون بنجاح تام!</p>
                <br>
                <a href="/register" style="padding: 10px 20px; background: #007bff; color: white; text-decoration: none; margin: 5px;">إنشاء حساب</a>
                <a href="/login" style="padding: 10px 20px; background: #28a745; color: white; text-decoration: none; margin: 5px;">تسجيل الدخول</a>
            </div>
        '''

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
