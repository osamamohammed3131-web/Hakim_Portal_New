from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# استدعاء ملفات الـ Blueprints الخاصة بالمشروع
from admin import admin_bp
from auth import auth_bp
from dashboard import dashboard_bp
# (إذا كان لديك ملفات أخرى مثل announcements أو community يمكنك تركها كما هي أو إضافتها هنا)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hakim_secure_secret_key_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hakim.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

# تسجيل الـ Blueprints لتشغيل جميع الأقسام ولوحة الإدارة
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

@app.route('/')
def home():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
