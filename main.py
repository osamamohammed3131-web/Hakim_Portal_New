from flask import Flask, redirect, url_for
from extensions import db, login_manager

# استدعاء ملفات الـ Blueprints
from admin import admin_bp
from auth import auth_bp
from dashboard import dashboard_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hakim_secure_secret_key_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hakim.db'

# ربط الإضافات بتطبيق الـ Flask
db.init_app(app)
login_manager.init_app(app)

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
    app.run(debug=True)
