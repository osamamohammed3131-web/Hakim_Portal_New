import os
from flask import Flask, redirect, url_for, render_template, flash
from flask_login import login_required, current_user, LoginManager
from extensions import db
from models import User
from auth import auth_bp
from dashboard import dashboard_bp
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hakim_secure_secret_key_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hakim.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None

# --- مسار لوحة المشرف الآمن ---
@app.route('/admin')
@app.route('/admin/')
@login_required
def admin_dashboard():
    # التحقق الآمن بالكامل بناءً على الحقول المتاحة أو البريد الإلكتروني للمشرف
    is_admin_flag = getattr(current_user, 'is_admin', False)
    user_role = getattr(current_user, 'role', None)
    
    if is_admin_flag or user_role in ['super_admin', 'admin'] or getattr(current_user, 'email', '') == 'superadmin@hakim.com':
        return "مرحباً بك في لوحة تحكم المشرف العام - المنصة تعمل بكامل الصلاحيات والاتصال مستقر."
    
    flash('غير مسموح لك بالوصول إلى لوحة المشرف.')
    return redirect(url_for('auth.login'))

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

@app.route('/')
def home():
    return redirect(url_for('auth.login'))

# تهيئة قاعدة البيانات وإنشاء الحساب بالأعمدة الأساسية فقط لتجنب أي خطأ
with app.app_context():
    db.create_all()
    admin = User.query.filter_by(email='superadmin@hakim.com').first()
    hashed_password = generate_password_hash('Admin@Hakim2026!', method='pbkdf2:sha256')
    
    if not admin:
        new_admin = User(
            username='SuperAdmin', 
            email='superadmin@hakim.com', 
            password_hash=hashed_password
        )
        db.session.add(new_admin)
        db.session.commit()
    else:
        admin.password_hash = hashed_password
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
