from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    # استدعاء الجداول والمسارات الكاملة
    from models import User
    
    from auth import auth_bp
    app.register_blueprint(auth_bp)

    from dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    from announcements import announcements_bp
    app.register_blueprint(announcements_bp)

    from resources import resources_bp
    app.register_blueprint(resources_bp)

    from community import community_bp
    app.register_blueprint(community_bp)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def home():
        return '''
            <div style="text-align: center; font-family: Tahoma; margin-top: 25px;">
                <h1>منصة حكيم الأكاديمية - النسخة المحدثة</h1>
                <p style="color: #28a745; font-weight: bold;">تم بناء كافة الأقسام والنظام الأساسي بنجاح تام!</p>
                <br>
                <div style="margin-top: 15px; line-height: 2.5;">
                    <a href="/register" style="padding: 10px 16px; background: #007bff; color: white; text-decoration: none; margin: 4px; border-radius: 5px; display: inline-block;">إنشاء حساب</a>
                    <a href="/login" style="padding: 10px 16px; background: #28a745; color: white; text-decoration: none; margin: 4px; border-radius: 5px; display: inline-block;">تسجيل الدخول</a>
                    <a href="/dashboard" style="padding: 10px 16px; background: #17a2b8; color: white; text-decoration: none; margin: 4px; border-radius: 5px; display: inline-block;">لوحة التحكم</a>
                    <a href="/announcements" style="padding: 10px 16px; background: #ffc107; color: #333; text-decoration: none; margin: 4px; border-radius: 5px; display: inline-block; font-weight: bold;">الإعلانات</a>
                    <a href="/resources" style="padding: 10px 16px; background: #6f42c1; color: white; text-decoration: none; margin: 4px; border-radius: 5px; display: inline-block;">بنك الملفات</a>
                    <a href="/community" style="padding: 10px 16px; background: #e83e8c; color: white; text-decoration: none; margin: 4px; border-radius: 5px; display: inline-block;">المجتمع الطلابي</a>
                </div>
            </div>
        '''

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
