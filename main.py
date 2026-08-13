import os
from flask import Flask, redirect, url_for, render_template_string, flash, request
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

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

# --- التوجيه الذكي بعد تسجيل الدخول حسب الـ Role ---
@app.route('/')
def home():
    if current_user.is_authenticated:
        role = getattr(current_user, 'role', 'student')
        is_admin_flag = getattr(current_user, 'is_admin', False)
        
        if is_admin_flag or role in ['super_admin', 'admin'] or current_user.email == 'superadmin@hakim.com':
            return redirect(url_for('admin_dashboard'))
        elif role == 'instructor':
            return redirect(url_for('instructor_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('auth.login'))

# --- 1. لوحة المشرف العام (Super Admin Dashboard) الحقيقية والمربوطة بالبيانات ---
@app.route('/admin')
@app.route('/admin/')
@login_required
def admin_dashboard():
    role = getattr(current_user, 'role', 'student')
    is_admin_flag = getattr(current_user, 'is_admin', False)
    
    if not (is_admin_flag or role in ['super_admin', 'admin'] or current_user.email == 'superadmin@hakim.com'):
        flash('غير مسموح لك بالوصول إلى لوحة المشرف.')
        return redirect(url_for('student_dashboard'))
    
    # جلب إحصائيات حقيقية من قاعدة البيانات
    try:
        total_users = User.query.count()
    except Exception:
        total_users = 1

    html_content = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>لوحة تحكم المشرف العام - منصة حكيم</title>
        <style>
            * { box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #f8fafc; margin: 0; padding: 0; direction: rtl; color: #334155; }
            .sidebar { width: 260px; background: #0f172a; color: #94a3b8; position: fixed; height: 100%; padding: 20px; overflow-y: auto; }
            .sidebar h2 { color: #fff; font-size: 1.2rem; text-align: center; margin-bottom: 30px; border-bottom: 1px solid #1e293b; padding-bottom: 15px; }
            .sidebar a { display: block; color: #cbd5e1; text-decoration: none; padding: 10px 15px; margin-bottom: 5px; border-radius: 6px; transition: 0.2s; font-size: 0.95rem; }
            .sidebar a:hover { background: #1e293b; color: #fff; }
            .main-content { margin-right: 260px; padding: 30px; }
            .header { background: #fff; padding: 20px 30px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .stat-card { background: #fff; padding: 20px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-right: 4px solid #3b82f6; }
            .stat-card h3 { margin: 0 0 10px 0; font-size: 0.9rem; color: #64748b; }
            .stat-card .number { font-size: 1.8rem; font-weight: bold; color: #0f172a; }
            .sections-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
            .section-card { background: #fff; padding: 20px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
            .section-card h4 { margin-top: 0; color: #1e293b; border-bottom: 2px solid #f1f5f9; padding-bottom: 10px; }
            .section-card ul { padding-right: 20px; margin: 0; color: #475569; line-height: 1.8; font-size: 0.9rem; }
            .logout-btn { background: #ef4444; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 0.9rem; }
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2>منصة حكيم - المشرف</h2>
            <a href="/admin">الرئيسية والإحصائيات</a>
            <a href="#">إدارة الطلاب والقبول</a>
            <a href="#">المستخدمون والصلاحيات</a>
            <a href="#">أعضاء هيئة التدريس</a>
            <a href="#">المقررات والأقسام</a>
            <a href="#">الخطط الدراسية</a>
            <a href="#">الملفات والمحتوى</a>
            <a href="#">الواجبات والكويزات</a>
            <a href="#">الاختبارات والدرجات</a>
            <a href="#">الجداول الدراسية</a>
            <a href="#">الإعلانات والإشعارات</a>
            <a href="#">المجتمع والدعم الفني</a>
            <a href="#">سجل العمليات والأمان</a>
            <a href="#">إعدادات المنصة</a>
        </div>
        <div class="main-content">
            <div class="header">
                <div>
                    <h2 style="margin:0; color:#1e293b;">لوحة تحكم المشرف العام (Super Admin)</h2>
                    <p style="margin:5px 0 0 0; color:#64748b; font-size:0.9rem;">مسجل باسم: {{ current_user.email }}</p>
                </div>
                <a href="/logout" class="logout-btn">تسجيل الخروج</a>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <h3>إجمالي المستخدمين</h3>
                    <div class="number">{{ total_users }}</div>
                </div>
                <div class="stat-card" style="border-color: #10b981;">
                    <h3>حالة النظام</h3>
                    <div class="number" style="font-size: 1.3rem; color: #10b981; margin-top: 5px;">متصل ومستقر (Live)</div>
                </div>
                <div class="stat-card" style="border-color: #f59e0b;">
                    <h3>الطلبات المعلقة</h3>
                    <div class="number">0</div>
                </div>
            </div>

            <div class="sections-grid">
                <div class="section-card">
                    <h4>إدارة الأكاديمية والطلاب</h4>
                    <ul>
                        <li>إدارة الطلاب وقبول ورفض التسجيل</li>
                        <li>إدارة أعضاء هيئة التدريس والأساتذة</li>
                        <li>إدارة المقررات والأقسام والتخصصات</li>
                        <li>إدارة الخطط الدراسية (Plan A & B)</li>
                    </ul>
                </div>
                <div class="section-card">
                    <h4>التقييمات والأنشطة</h4>
                    <ul>
                        <li>إدارة الواجبات والملفات التعليمية</li>
                        <li>إدارة الكويزات والاختبارات القصيرة</li>
                        <li>إدارة الامتحانات النهائية ورصد الدرجات</li>
                        <li>إدارة الجداول الدراسية والحضور</li>
                    </ul>
                </div>
                <div class="section-card">
                    <h4>التواصل والنظام</h4>
                    <ul>
                        <li>الإعلانات والإشعارات العامة</li>
                        <li>المجتمع الطلابي وقنوات النقاش</li>
                        <li>الدعم الفني وتذاكر الاستفسارات</li>
                        <li>سجل العمليات وصلاحيات الأدوار والأمان</li>
                    </ul>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_content, current_user=current_user, total_users=total_users)

# --- 2. لوحة الطالب (Student Dashboard) الحقيقية والمتكاملة ---
@app.route('/student')
@app.route('/student/')
@login_required
def student_dashboard():
    html_content = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>لوحة الطالب الأكاديمية - منصة حكيم</title>
        <style>
            * { box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #f8fafc; margin: 0; padding: 0; direction: rtl; color: #334155; }
            .sidebar { width: 260px; background: #0284c7; color: #e0f2fe; position: fixed; height: 100%; padding: 20px; overflow-y: auto; }
            .sidebar h2 { color: #fff; font-size: 1.2rem; text-align: center; margin-bottom: 30px; border-bottom: 1px solid #0369a1; padding-bottom: 15px; }
            .sidebar a { display: block; color: #e0f2fe; text-decoration: none; padding: 10px 15px; margin-bottom: 5px; border-radius: 6px; transition: 0.2s; font-size: 0.95rem; }
            .sidebar a:hover { background: #0369a1; color: #fff; }
            .main-content { margin-right: 260px; padding: 30px; }
            .header { background: #fff; padding: 20px 30px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
            .card { background: #fff; padding: 20px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-top: 4px solid #0284c7; }
            .card h3 { margin-top: 0; color: #0f172a; font-size: 1.1rem; border-bottom: 2px solid #f1f5f9; padding-bottom: 10px; }
            .card p { color: #64748b; font-size: 0.9rem; line-height: 1.6; }
            .logout-btn { background: #ef4444; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 0.9rem; }
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2>منصة حكيم الأكاديمية</h2>
            <a href="/student">الرئيسية</a>
            <a href="#">الملف الشخصي</a>
            <a href="#">المقررات المسجلة</a>
            <a href="#">الخطط الدراسية</a>
            <a href="#">المحاضرات والمحتوى</a>
            <a href="#">الملفات والمراجع</a>
            <a href="#">الواجبات</a>
            <a href="#">الكويزات والاختبارات</a>
            <a href="#">الدرجات والنتائج</a>
            <a href="#">الجدول الدراسي</a>
            <a href="#">سجل الحضور</a>
            <a href="#">الإعلانات والإشعارات</a>
            <a href="#">المجتمع الطلابي</a>
            <a href="#">الدعم والمساعدة</a>
        </div>
        <div class="main-content">
            <div class="header">
                <div>
                    <h2 style="margin:0; color:#1e293b;">لوحة الطالب الأكاديمية</h2>
                    <p style="margin:5px 0 0 0; color:#64748b; font-size:0.9rem;">أهلاً بك، {{ current_user.email }}</p>
                </div>
                <a href="/logout" class="logout-btn">تسجيل الخروج</a>
            </div>

            <div class="grid">
                <div class="card">
                    <h3>المقررات والخطط</h3>
                    <p>استعراض المقررات المسجلة للفصل الحالي، الخطط الدراسية (Plan A & B)، ومتابعة مسار التخرج الأكاديمي.</p>
                </div>
                <div class="card">
                    <h3>المحتوى والمحاضرات</h3>
                    <p>الوصول إلى المحاضرات المرئية، الملفات، المراجع العلمية، والملازم الإرشادية الخاصة بمناهجك.</p>
                </div>
                <div class="card">
                    <h3>الواجبات والتقييمات</h3>
                    <p>تسليم الواجبات اليومية، أداء الكويزات القصيرة، ومراجعة مواعيد الاختبارات النهائية.</p>
                </div>
                <div class="card">
                    <h3>الدرجات والسجل</h3>
                    <p>متابعة تفصيلية لدرجات الأعمال الفصلية، الاختبارات، والمعدل التراكمي والسجل الأكاديمي.</p>
                </div>
                <div class="card">
                    <h3>الجدول والحضور</h3>
                    <p>عرض الجدول الدراسي الأسبوعي، مواعيد المحاضرات الحية، ومتابعة سجل الحضور والغياب.</p>
                </div>
                <div class="card">
                    <h3>الإعلانات والمجتمع</h3>
                    <p>الإعلانات الرسمية للإدارة، قنوات المجتمع الطلابي للتفاعل، وطلب الدعم الفني والأكاديمي.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_content, current_user=current_user)

# --- 3. لوحة الأستاذ / هيئة التدريس (Instructor Dashboard) ---
@app.route('/instructor')
@app.route('/instructor/')
@login_required
def instructor_dashboard():
    return "مرحباً بك في لوحة أعضاء هيئة التدريس - منصة حكيم"

# --- 4. تهيئة قاعدة البيانات وضمان وجود حساب المشرف ---
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
