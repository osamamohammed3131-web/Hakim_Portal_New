import os
from flask import Flask, redirect, url_for, render_template_string, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from extensions import db
from models import User, Material, Lecture, StudentSchedule, KnowledgeFile, SupportKnowledge
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hakim_secure_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hakim.db'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- مسارات المصادقة والتسجيل ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('home'))
        flash('خطأ في البيانات المدخلة')
    return render_template_string('''
        <div style="text-align:center; margin-top:50px; font-family:Tahoma; direction:rtl;">
            <h2>تسجيل الدخول - منصة حكيم الأكاديمية</h2>
            <form method="POST">
                <input type="email" name="email" placeholder="البريد الإلكتروني" style="padding:10px; margin:5px; width:280px;" required><br>
                <input type="password" name="password" placeholder="كلمة المرور" style="padding:10px; margin:5px; width:280px;" required><br>
                <button type="submit" style="padding:10px 20px; background:#0284c7; color:white; border:none; border-radius:5px; cursor:pointer;">دخول</button>
            </form>
            <p style="margin-top:15px;"><a href="/register" style="color:#0284c7;">تسجيل طالب جديد</a> | <a href="/support" style="color:#10b981;">بوابة الدعم المباشر</a></p>
        </div>''')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        plan_type = request.form.get('plan_type', 'A')
        if User.query.filter_by(email=email).first():
            return "البريد مسجل مسبقاً! <a href='/register'>رجوع</a>"
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='student',
            is_admin=False,
            plan_type=plan_type
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template_string('''
        <div style="text-align:center; margin-top:50px; font-family:Tahoma; direction:rtl;">
            <h2>تسجيل طالب جديد - منصة حكيم</h2>
            <form method="POST">
                <input type="text" name="username" placeholder="اسم المستخدم" style="padding:10px; margin:5px; width:280px;" required><br>
                <input type="email" name="email" placeholder="البريد الإلكتروني" style="padding:10px; margin:5px; width:280px;" required><br>
                <input type="password" name="password" placeholder="كلمة المرور" style="padding:10px; margin:5px; width:280px;" required><br>
                <label>اختر الخطة التمهيدية:</label><br>
                <select name="plan_type" style="padding:10px; margin:5px; width:280px;">
                    <option value="A">خطة A (المهارات الأكاديمية، الحاسب، الإنجليزية)</option>
                    <option value="B">خطة B (مهارات الاتصال، الرياضيات، الإنجليزية)</option>
                </select><br>
                <button type="submit" style="padding:10px 20px; background:#10b981; color:white; border:none; border-radius:5px; cursor:pointer;">إتمام التسجيل</button>
            </form>
            <p style="margin-top:15px;"><a href="/login" style="color:#0284c7;">العودة لتسجيل الدخول</a></p>
        </div>''')

@app.route('/')
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if getattr(current_user, 'is_admin', False) or current_user.email == 'superadmin@hakim.com':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('student_dashboard'))

# --- لوحة الطالب والبيئات الفعلية ---
@app.route('/student')
@login_required
def student_dashboard():
    materials = Material.query.filter_by(plan_type=current_user.plan_type).all()
    return render_template_string('''
        <div style="font-family:Tahoma; direction:rtl; padding:20px; background:#f0f9ff;">
            <h1 style="color:#0369a1;">لوحة الطالب الأكاديمية - خطة ({{ current_user.plan_type }})</h1>
            <p>أهلاً بك: <b>{{ current_user.email }}</b></p>
            <hr>
            <h3>المقررات والبيئة الدراسية:</h3>
            <ul>
                {% for mat in materials %}
                    <li><b>{{ mat.name }}</b>: {{ mat.description }} | <a href="/material/{{ mat.id }}">استعراض المحتوى والمحاضرات</a></li>
                {% endfor %}
            </ul>
            <hr>
            <h3>أقسام النظام الذكي:</h3>
            <ul>
                <li><a href="/schedule">الجدول الذكي وإدارة المهام</a></li>
                <li><a href="/ai-assistant">المساعد الأكاديمي (AI)</a></li>
                <li><a href="/training">التدريب والتجارب العملية</a></li>
                <li><a href="/support">بوابة الدعم المباشر «حكيم»</a></li>
            </ul>
            <br><a href="/logout" style="background:#ef4444; color:white; padding:8px 15px; text-decoration:none; border-radius:5px;">تسجيل الخروج</a>
        </div>''', current_user=current_user, materials=materials)

@app.route('/material/<int:mat_id>')
@login_required
def material_detail(mat_id):
    material = Material.query.get_or_404(mat_id)
    lectures = Lecture.query.filter_by(material_id=mat_id).all()
    files = KnowledgeFile.query.filter_by(material_id=mat_id).all()
    return render_template_string('''
        <div style="font-family:Tahoma; direction:rtl; padding:20px;">
            <h2>مقرر: {{ material.name }}</h2>
            <p>{{ material.description }}</p>
            <hr>
            <h3>المحاضرات المرتبطة:</h3>
            <ul>
                {% for lec in lectures %}
                    <li>الأسبوع {{ lec.week_number }}: {{ lec.title }} ({{ lec.date_time }})</li>
                {% endfor %}
            </ul>
            <h3>الكتب والملفات والمراجع:</h3>
            <ul>
                {% for f in files %}
                    <li><a href="{{ f.file_path }}" target="_blank">{{ f.filename }}</a> ({{ f.category }})</li>
                {% endfor %}
            </ul>
            <br><a href="/student">العودة للوحة الطالب</a>
        </div>''', material=material, lectures=lectures, files=files)

@app.route('/schedule')
@login_required
def schedule():
    schedules = StudentSchedule.query.filter_by(user_id=current_user.id).all()
    return render_template_string('''
        <div style="font-family:Tahoma; direction:rtl; padding:20px;">
            <h2>الجدول الذكي وإدارة المهام</h2>
            <p>ماذا أفعل الآن؟ النظام يدير مواعيدك ومحاضراتك تلقائياً.</p>
            <hr>
            <h3>محاضراتك المجدولة:</h3>
            <ul>
                {% for s in schedules %}
                    <li>{{ s.day_of_week }} - {{ s.time_slot }} | الحالة: <b>{{ s.status }}</b></li>
                {% endfor %}
            </ul>
            <br><a href="/student">العودة للوحة الطالب</a>
        </div>''', schedules=schedules)

@app.route('/ai-assistant')
@login_required
def ai_assistant():
    return render_template_string('''
        <div style="font-family:Tahoma; direction:rtl; padding:20px;">
            <h2>المساعد الأكاديمي للذكاء الاصطناعي (RAG)</h2>
            <p>مساعد يعتمد حصرياً على الكتب والمراجع المعتمدة للمادة لشرح الدروس والتلخيص وإنشاء التدريبات.</p>
            <textarea placeholder="اطرح سؤالك الأكاديمي هنا..." style="width:100%; height:100px; padding:10px;"></textarea><br>
            <button style="padding:10px 20px; background:#0284c7; color:white; border:none; border-radius:5px; margin-top:10px;">إرسال السؤال للمساعد</button>
            <br><br><a href="/student">العودة للوحة الطالب</a>
        </div>''')

@app.route('/training')
@login_required
def training():
    return render_template_string('''
        <div style="font-family:Tahoma; direction:rtl; padding:20px;">
            <h2>قسم التدريب والتجارب العملية</h2>
            <p>الانتقال من مستخدم للذكاء الاصطناعي إلى صانع أدوات ومشاريع ذكية.</p>
            <ul>
                <li>التجربة 1: التعامل المتقدم مع ملفات المعرفة واستخراج البيانات.</li>
                <li>التجربة 2: بناء مساعد ذكي محلي وبسيطة.</li>
                <li>التجربة 3: تنفيذ مشروع عملي باستخدام وكلاء AI.</li>
            </ul>
            <br><a href="/student">العودة للوحة الطالب</a>
        </div>''')

# --- بوابة الدعم المباشر (بدون تسجيل دخول) ---
@app.route('/support', methods=['GET', 'POST'])
def support():
    answer = None
    query = ""
    if request.method == 'POST':
        query = request.form.get('query')
        kb_item = SupportKnowledge.query.filter(SupportKnowledge.question.like(f"%{query}%")).first()
        if kb_item:
            answer = kb_item.answer
        else:
            answer = "عذراً، لم نجد مصدراً موثوقاً في قاعدة المعرفة للإجابة عن هذا الاستفسار حالياً، وتم إحالة السؤال للدعم البشري المعتمد."
    return render_template_string('''
        <div style="font-family:Tahoma; direction:rtl; padding:20px; max-width:600px; margin:auto;">
            <h2>بوابة الدعم المباشر «حكيم»</h2>
            <p>استعلم عن القبول، التسجيل، التحويل، المواعيد واللوائح بدقة موثوقة.</p>
            <form method="POST">
                <input type="text" name="query" placeholder="اكتب سؤالك هنا..." value="{{ query }}" style="width:70%; padding:10px;" required>
                <button type="submit" style="padding:10px 20px; background:#10b981; color:white; border:none; border-radius:5px;">بحث / إجابة</button>
            </form>
            {% if answer %}
                <div style="margin-top:20px; padding:15px; background:#f1f5f9; border-right:4px solid #10b981;">
                    <b>الإجابة المعتمدة:</b><br>{{ answer }}
                </div>
            {% endif %}
            <br><hr><a href="/login">تسجيل الدخول للمنصة</a>
        </div>''', answer=answer, query=query)

# --- لوحة المشرف الفعلية ---
@app.route('/admin')
@login_required
def admin_dashboard():
    if not getattr(current_user, 'is_admin', False) and current_user.email != 'superadmin@hakim.com':
        return "غير مأذون لك بالدخول لهذه اللوحة!", 403
    students_count = User.query.filter_by(role='student').count()
    materials_count = Material.query.count()
    return render_template_string('''
        <div style="font-family:Tahoma; direction:rtl; padding:20px; background:#f8fafc;">
            <h1 style="color:#0f172a;">لوحة إدارة المشرف العام الفعلية</h1>
            <p>أهلاً بك: <b>{{ current_user.email }}</b></p>
            <hr>
            <div style="display:flex; gap:20px; margin-bottom:20px;">
                <div style="background:white; padding:15px; border-radius:8px; box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                    <h3>إجمالي الطلاب المسجلين</h3>
                    <p style="font-size:24px; color:#0284c7;">{{ students_count }}</p>
                </div>
                <div style="background:white; padding:15px; border-radius:8px; box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                    <h3>إجمالي المقررات (خطة A & B)</h3>
                    <p style="font-size:24px; color:#10b981;">{{ materials_count }}</p>
                </div>
            </div>
            <h3>أقسام الإدارة والتحكم:</h3>
            <ul>
                <li>إدارة الطلاب والخطم التمهيدية</li>
                <li>إدارة المواد والكتب والملفات (مركز المعرفة AI)</li>
                <li>قاعدة معرفة الدعم المباشر وتحديثاتها</li>
                <li>إدارة الجداول والمحاضرات والتقارير</li>
            </ul>
            <br><a href="/logout" style="background:#ef4444; color:white; padding:8px 15px; text-decoration:none; border-radius:5px;">تسجيل الخروج</a>
        </div>''', current_user=current_user, students_count=students_count, materials_count=materials_count)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- تهيئة البيانات الأساسية في قاعدة البيانات تلقائياً ---
with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='superadmin@hakim.com').first():
        new_admin = User(username='Admin', email='superadmin@hakim.com', 
                         password_hash=generate_password_hash('Admin@Hakim2026!'), is_admin=True, role='superadmin')
        db.session.add(new_admin)
        db.session.commit()
    
    # إضافة المواد الافتراضية لخطة A و B إن لم تكن موجودة
    if not Material.query.first():
        default_materials = [
            Material(name='المهارات الأكاديمية', plan_type='A', description='تطوير مهارات التعلم والبحث العلمي والجامعي.'),
            Material(name='الحاسب الآلي', plan_type='A', description='أساسيات البرمجة وأنظمة التشغيل وحل المشكلات.'),
            Material(name='اللغة الإنجليزية (A)', plan_type='A', description='اللغة الإنجليزية الأكاديمية للمستوى التمهيدي.'),
            Material(name='مهارات الاتصال', plan_type='B', description='فن الإلقاء والتواصل الفعال وبيئة العمل.'),
            Material(name='الرياضيات', plan_type='B', description='الرياضيات التمهيدية والتحليل الكمي.'),
            Material(name='اللغة الإنجليزية (B)', plan_type='B', description='اللغة الإنجليزية التخصصية والتفاوض.')
        ]
        db.session.add_all(default_materials)
        db.session.commit()

    if not SupportKnowledge.query.first():
        default_kb = SupportKnowledge(
            question='متى موعد بدء التسجيل في المنصة؟',
            answer='يبدأ التسجيل في الفترات التمهيدية المعلنة رسمياً عبر القنوات المعتمدة للمنصة.',
            source='الأرشيف الرسمي المعتمد',
            verified=True
        )
        db.session.add(default_kb)
        db.session.commit()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
