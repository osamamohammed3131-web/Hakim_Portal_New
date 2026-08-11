from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    # استدعاء جدول المستخدمين
    from models import User
    
    # تسجيل المسارات والBlueprints
    from auth import auth_bp
    app.register_blueprint(auth_bp)

    from dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    from announcements import announcements_bp
    app.register_blueprint(announcements_bp)

    from resources import resources_bp
    app.register_blueprint(resources_bp)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def home():
        return '''
            <div style="text-align: center; font-family: Tahoma; margin-top: 30px;">
                <h1>مرحباً بك في منصة حكيم الأكاديمية</h1>
                <p>جميع أقسام المنصة (النواة، المصادقة، لوحة التحكم، الإعلانات، وبنك الملفات) تعمل بنجاح تام!</p>
                <br>
                <div style="margin-top: 20px;">
                    <a href="/register" style="padding: 10px 16px; background: #007bff; color: white; text-decoration: none; margin: 4px; border-radius: 5px; display: inline-block;">إنشاء حساب</a>
                    <a href="/login" style="padding: 10px 16px; background: #28a745; color: white; text-decoration: none; margin: 4px; border-radius: 5px; display: inline-block;">تسجيل الدخول</a>
                    <a href="/dashboard" style="padding: 10px 16px; background: #17a2b8; color: white; text-decoration: none; margin: 4px; border-radius: 5px; display: inline-block;">لوحة التحكم</a>
                    <a href="/announcements" style="padding: 10px 16px; background: #ffc107; color: #333; text-decoration: none; margin: 4px; border-radius: 5px; display: inline-block; font-weight: bold;">الإعلانات</a>
                    <a href="/resources" style="padding: 10px 16px; background: #6f42c1; color: white; text-decoration: none; margin: 4px; border-radius: 5px; display: inline-block;">بنك الملفات</a>
                </div>
            </div>
        '''

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
