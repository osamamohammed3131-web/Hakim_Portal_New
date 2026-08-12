from flask import Flask, redirect, url_for
from extensions import db
from models import User
from admin import admin_bp
from auth import auth_bp
from dashboard import dashboard_bp
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hakim_secure_secret_key_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hakim.db'

# ربط الإضافات
db.init_app(app)

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
        # إنشاء حساب المشرف تلقائياً بأمان تام وتوافق كامل مع الصلاحيات
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
