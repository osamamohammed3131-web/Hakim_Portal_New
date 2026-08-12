from flask import Blueprint, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from main import db
from models import User

auth_bp = Blueprint('auth', __name__)

# صفحة ومسار التسجيل
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            return "البريد الإلكتروني مستخدم مسبقاً! <a href='/register'>حاول مرة أخرى</a>"
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password_hash=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))
        
    return '''
        <dir style="text-align: center; font-family: Tahoma; margin-top: 50px;">
            <h2>تسجيل حساب جديد - منصة حكيم الأكاديمية</h2>
            <form method="POST">
                <input type="text" name="username" placeholder="اسم المستخدم" required style="padding: 8px; margin: 5px;"><br>
                <input type="email" name="email" placeholder="البريد الإلكتروني" required style="padding: 8px; margin: 5px;"><br>
                <input type="password" name="password" placeholder="كلمة المرور" required style="padding: 8px; margin: 5px;"><br><br>
                <button type="submit" style="padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer;">تسجيل حساب</button>
            </form>
            <br><a href="/login">لديك حساب بالفعل؟ تسجيل الدخول</a>
        </dir>
    '''

# صفحة ومسار تسجيل الدخول
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            return f'''
                <div style="text-align: center; font-family: Tahoma; margin-top: 50px;">
                    <h1 style="color: green;">مرحباً بك مجدداً يا {user.username}!</h1>
                    <p>تم تسجيل دخولك بنجاح في منصة حكيم الأكاديمية.</p>
                    <a href="/login">تسجيل الخروج</a>
                </div>
            '''
        return "بيانات الدخول غير صحيحة! <a href='/login'>حاول مرة أخرى</a>"
        
    return '''
        <div style="text-align: center; font-family: Tahoma; margin-top: 50px;">
            <h2>تسجيل الدخول - منصة حكيم الأكاديمية</h2>
            <form method="POST">
                <input type="email" name="email" placeholder="البريد الإلكتروني" required style="padding: 8px; margin: 5px;"><br>
                <input type="password" name="password" placeholder="كلمة المرور" required style="padding: 8px; margin: 5px;"><br><br>
                <button type="submit" style="padding: 10px 20px; background: #28a745; color: white; border: none; cursor: pointer;">دخول</button>
            </form>
            <br><a href="/register">ليس لديك حساب؟ سجل الآن</a>
        </div>
    '''

from functools import wraps
from flask_login import current_user
from flask import redirect, url_for, flash

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or getattr(current_user, 'role', None) != 'admin':
            flash("غير مسموح لك بالدخول لهذه الصفحة", "danger")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def verified_student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if getattr(current_user, 'status', 'approved') == 'pending':
            flash("حسابك قيد الانتظار لم يتم تفعيله بعد", "warning")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
