from flask import Blueprint, render_template, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
# استيراد نموذج المستخدم الخاص بك
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            return 'البريد الإلكتروني مستخدم مسبقاً، <a href="/register">حاول مرة أخرى</a>'
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))
        
    return '''
    <div style="text-align: center; font-family: Tahoma; margin-top: 50px;">
        <h2>تسجيل حساب جديد - منصة حكيم الأكاديمية</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="اسم المستخدم" required style="padding: 8px; margin: 5px;"><br>
            <input type="email" name="email" placeholder="البريد الإلكتروني" required style="padding: 8px; margin: 5px;"><br>
            <input type="password" name="password" placeholder="كلمة المرور" required style="padding: 8px; margin: 5px;"><br>
            <button type="submit" style="padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer;">تسجيل</button>
        </form>
        <br><a href="/login">لديك حساب بالفعل؟ تسجل الدخول</a>
    </div>
    '''

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            return redirect(url_for('dashboard.student_dashboard'))
        return 'بيانات الدخول غير صحيحة، <a href="/login">حاول مرة أخرى</a>'
        
    return '''
    <div style="text-align: center; font-family: Tahoma; margin-top: 50px;">
        <h2>تسجيل الدخول - منصة حكيم الأكاديمية</h2>
        <form method="POST">
            <input type="email" name="email" placeholder="البريد الإلكتروني" required style="padding: 8px; margin: 5px;"><br>
            <input type="password" name="password" placeholder="كلمة المرور" required style="padding: 8px; margin: 5px;"><br>
            <button type="submit" style="padding: 10px 20px; background: #28a745; color: white; border: none; cursor: pointer;">دخول</button>
        </form>
        <br><a href="/register">ليس لديك حساب؟ سجل الآن</a>
    </div>
    '''

@auth_bp.route('/logout')
def logout():
    return redirect(url_for('auth.login'))
