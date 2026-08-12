from flask import Flask, redirect, url_for, Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user, LoginManager
from extensions import db
from models import User
from auth import auth_bp
from dashboard import dashboard_bp
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hakim_secure_secret_key_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hakim.db'

# ربط الإضافات
db.init_app(app)

# إعداد Flask-Login إذا لم يكن معرفاً في ملفات أخرى
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# تعريف الـ Blueprint الخاص بالإدارة مباشرة هنا لضمان عدم ضياع المسار
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
def admin_dashboard():
    is_authorized = False
    if hasattr(current_user, 'role') and current_user.role in ['super_admin', 'admin']:
        is_authorized = True
    elif hasattr(current_user, 'is_admin') and current_user.is_admin:
        is_authorized = True
        
    if not is_authorized:
        flash('غير مسموح لك بالوصول إلى لوحة المشرف.')
        return redirect(url_for('auth.login'))
        
    return "مرحباً بك في لوحة تحكم المشرف العام - المنصة تعمل بكامل الصلاحيات."

# تسجيل الـ Blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

@app.route('/')
def home():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(email='superadmin@hakim.com').first()
        if not admin:
            hashed_password = generate_password_hash('Admin@Hakim2026!', method='pbkdf2:sha256')
            new_admin = User(
                username='SuperAdmin', 
                email='superadmin@hakim.com', 
                password=hashed_password, 
                is_admin=True,
                role='super_admin'
            )
            db.session.add(new_admin)
            db.session.commit()
    app.run(debug=True)
