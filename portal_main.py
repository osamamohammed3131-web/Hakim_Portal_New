import os
from flask import Flask, render_template_string, request, redirect, url_for, session, send_from_directory

app = Flask(__name__)
app.secret_key = 'hakim_elite_university_portal_2026'

# إعداد مستودع التخزين الحقيقي للملفات والتجميعات
UPLOAD_FOLDER = 'server_storage'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# قاعدة بيانات الطلاب والمشرفين
students_database = [
    {'name': 'حكيم (المشرف العام)', 'phone': '0500000000', 'student_id': 'admin777', 'status': 'مقبول'}
]
ADMIN_PIN = "999"

# 1. الواجهة الرئيسية المطلوبة (نفس التصميم الفاخر مع تفعيل كافة الأزرار)
student_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>منصة حكيم الأكاديمية التفاعلية</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #0f1016; color: #fff; margin: 0; padding: 0; }
        .header { background: #1a1c29; padding: 25px; text-align: center; border-bottom: 2px solid #00f2c3; }
        .header h1 { color: #00f2c3; margin: 0; font-size: 28px; }
        .header p { color: #a0a0a0; margin: 5px 0 0 0; }
        .main-container { max-width: 950px; margin: 30px auto; padding: 20px; }
        .card { background: #1a1c29; padding: 30px; border-radius: 12px; box-shadow: 0 8px 25px rgba(0,0,0,0.6); margin-bottom: 20px; border: 1px solid #22253a; }
        input { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #333; background: #11121a; color: #fff; box-sizing: border-box; }
        button { background: #00f2c3; color: #0f1016; border: none; padding: 12px 25px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; width: 100%; margin-top: 10px; transition: 0.3s; }
        button:hover { background: #00c8a0; }
        .alert-pending { background: #f39c12; color: #0f1016; padding: 15px; border-radius: 8px; font-weight: bold; text-align: center; }
        .alert-accepted { background: #27ae60; color: #fff; padding: 15px; border-radius: 8px; font-weight: bold; text-align: center; margin-bottom: 20px; }
        .grid-sections { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; margin-top: 25px; }
        .sec-box { background: #11121a; padding: 20px; border-radius: 10px; border: 1px solid #00f2c3; text-align: right; }
        .sec-box h3 { color: #00f2c3; margin-top: 0; }
        .sec-box p { color: #b0b0b0; font-size: 14px; line-height: 1.5; }
        .sec-box a { color: #0f1016; text-decoration: none; background: #00f2c3; padding: 8px 15px; border-radius: 5px; display: inline-block; margin-top: 10px; font-weight: bold; font-size: 14px; }
        .admin-link { display: block; text-align: center; margin-top: 20px; color: #e74c3c; text-decoration: none; font-weight: bold; font-size: 14px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>منصة حكيم الأكاديمية التفاعلية</h1>
        <p>البوابة الرسمية المتقدمة للتحضير والاختبارات الذكية (منافسة النخبة)</p>
    </div>

    <div class="main-container">
        <div class="card">
            <div style="text-align: center; margin-bottom: 20px;">
                <h3 style="color: #fff;">استعلام عن حالة الحساب برقم الجلوس:</h3>
                <form method="GET" action="/">
                    <input type="text" name="check_id" placeholder="أدخل رقم الجلوس الخاص بك هنا" value="{{ searched_id or '' }}" style="max-width: 450px; display: inline-block;">
                    <button type="submit" style="max-width: 150px; display: inline-block; padding: 10px;">تحقق</button>
                </form>
            </div>

            {% if student_status == 'مقبول' %}
                <div class="alert-accepted">أهلاً بك في بيئة التعلم المتقدمة. تم تفعيل حسابك بنجاح وجاهز لاستعراض المنظومة!</div>
                <div class="grid-sections">
                    <div class="sec-box">
                        <h3>📚 اختبارات الميد (Midterms)</h3>
                        <p>ملخصات معتمدة، بنوك أسئلة، ومراجعات النصف الدراسي الأول والثاني.</p>
                        <a href="/section/midterms">استعرض المحتوى</a>
                    </div>
                    <div class="sec-box">
                        <h3>🎓 اختبارات الفاينل (Finals)</h3>
                        <p>التجميعات الشاملة، الاختبارات السابقة، ونماذج الإجابة النموذجية.</p>
                        <a href="/section/finals">استعرض التجميعات</a>
                    </div>
                    <div class="sec-box">
                        <h3>📝 الواجبات والكويزات الذكية</h3>
                        <p>تدريبات تفاعلية واختبارات قصيرة تصحح آلياً لتقييم مستواك.</p>
                        <a href="/section/quizzes">ابدأ التدريب</a>
                    </div>
                </div>
            {% elif student_status == 'قيد الانتظار' %}
                <div class="alert-pending">طلبك مسجل بنجاح وقيد المراجعة الإدارية من قبل المشرف.</div>
            {% else %}
                <h3 style="text-align: center; color: #00f2c3; border-top: 1px solid #333; padding-top: 20px;">التسجيل الأكاديمي للانضمام للمنصة</h3>
                <form method="POST">
                    <label>الاسم الثلاثي:</label>
                    <input type="text" name="name" required placeholder="أدخل اسمك الكامل">
                    <label>رقم التواصل (واتساب):</label>
                    <input type="text" name="phone" required placeholder="05xxxxxxxx">
                    <label>رقم الجلوس أو التخصص:</label>
                    <input type="text" name="student_id" required placeholder="أدخل رقم جلوسك الفريد">
                    <button type="submit">إرسال طلب الانضمام الأكاديمي</button>
                </form>
            {% endif %}

            <a href="/hakim-secure-command-room-999" class="admin-link">🔒 بوابة الإدارة والتحكم السيادية</a>
        </div>
    </div>
</body>
</html>
"""

# 2. صفحة استعراض الملفات والأقسام (مربوطة بلوحة التحكم)
section_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>{{ title }} - منصة حكيم</title>
    <style>
        body { font-family: Tahoma; background: #0f1016; color: #fff; padding: 20px; margin: 0; }
        .box { max-width: 850px; margin: auto; background: #1a1c29; padding: 30px; border-radius: 12px; border: 1px solid #00f2c3; }
        h2 { color: #00f2c3; text-align: center; }
        ul { list-style: none; padding: 0; margin-top: 20px; }
        li { background: #11121a; margin: 12px 0; padding: 15px 20px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #333; }
        a.btn { background: #00f2c3; color: #0f1016; padding: 8px 18px; border-radius: 6px; text-decoration: none; font-weight: bold; }
        a.btn:hover { background: #00c8a0; }
        .back { display: inline-block; margin-bottom: 20px; color: #00f2c3; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="box">
        <a href="/" class="back">← العودة للرئيسية</a>
        <h2>{{ title }}</h2>
        <p style="color: #aaa; text-align: center;">جميع الملفات والمراجع المرفوعة بواسطة الإدارة متوفرة للتحميل المباشر:</p>
        <ul>
            {% for file in files %}
                <li>
                    <span style="font-size: 16px;">📄 {{ file }}</span>
                    <a href="/download/{{ file }}" class="btn">تحميل الملف</a>
                </li>
            {% else %}
                <li style="color: #777; justify-content: center; padding: 30px;">لا توجد ملفات مرفوعة في هذا القسم حالياً. انتظر إضافتها من المشرف.</li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

# 3. صفحة الكويزات الذكية والتفاعلية
quiz_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>الكويزات التفاعلية - منصة حكيم</title>
    <style>
        body { font-family: Tahoma; background: #0f1016; color: #fff; padding: 20px; margin: 0; }
        .box { max-width: 850px; margin: auto; background: #1a1c29; padding: 30px; border-radius: 12px; border: 1px solid #00f2c3; }
        h2 { color: #00f2c3; text-align: center; }
        .q-card { background: #11121a; padding: 25px; border-radius: 10px; margin-top: 20px; border: 1px solid #333; }
        label { display: block; margin: 15px 0; cursor: pointer; font-size: 16px; }
        button { background: #00f2c3; color: #0f1016; border: none; padding: 12px 25px; font-weight: bold; border-radius: 8px; cursor: pointer; margin-top: 20px; width: 100%; font-size: 16px; }
        .back { display: inline-block; margin-bottom: 20px; color: #00f2c3; text-decoration: none; font-weight: bold; }
        .result-box { background: #27ae60; color: #fff; padding: 15px; border-radius: 8px; text-align: center; margin-top: 20px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="box">
        <a href="/" class="back">← العودة للرئيسية</a>
        <h2>الكويزات والتدريبات الأكاديمية الفورية</h2>
        <form method="POST">
            <div class="q-card">
                <p style="font-size: 18px; color: #00f2c3;"><b>السؤال الأول:</b> أي من الأقسام التالية يختص بالمراجعات واختبارات الميد؟</p>
                <label><input type="radio" name="q1" value="wrong"> أرشيف الفاينل والتجميعات الكبرى</label>
                <label><input type="radio" name="q1" value="right"> قسم اختبارات الميد (Midterms)</label>
                <label><input type="radio" name="q1" value="wrong"> لوحة تحكم المشرف العام</label>
            </div>
            <button type="submit">إرسال الإجابة وتقييم المستوى الفوري</button>
        </form>
        {% if result %}
            <div class="result-box">{{ result }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

# 4. لوحة تحكم المشرف الشاملة
admin_dashboard_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>غرفة القيادة السيادية - منصة حكيم</title>
    <style>
        body { font-family: Tahoma; background: #0f1016; color: #fff; padding: 20px; margin: 0; }
        .container { max-width: 950px; margin: auto; background: #1a1c29; padding: 30px; border-radius: 12px; border: 1px solid #e74c3c; }
        h1 { color: #e74c3c; text-align: center; }
        .section-box { background: #11121a; padding: 20px; border-radius: 8px; margin-top: 25px; border: 1px solid #333; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; text-align: center; border-bottom: 1px solid #222; }
        th { background: #e74c3c; color: #fff; }
        .btn-act { padding: 6px 12px; border-radius: 5px; text-decoration: none; font-weight: bold; font-size: 13px; display: inline-block; margin: 2px; }
        .accept { background: #27ae60; color: #fff; }
        .reject { background: #c0392b; color: #fff; }
        .logout { float: left; color: #e74c3c; text-decoration: none; font-weight: bold; }
        input[type="file"] { background: #1a1c29; padding: 12px; border: 1px dashed #00f2c3; width: 100%; box-sizing: border-box; color: #fff; margin-top: 10px; border-radius: 6px; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/admin/logout" class="logout">تسجيل الخروج 🚪</a>
        <a href="/" style="color: #00f2c3; text-decoration: none; font-weight: bold; margin-left: 20px;">← زيارة المنصة</a>
        <h1>غرفة القيادة والتحكم المطلق للمشرف</h1>

        <div class="section-box">
            <h3 style="color: #00f2c3;">📁 مستودع الكتب والتجميعات (الرفع الفعلي للسيرفر)</h3>
            <form method="POST" action="/admin/upload" enctype="multipart/form-data">
                <input type="file" name="study_file" required>
                <button type="submit" style="background: #00f2c3; color: #0f1016; border: none; padding: 12px 20px; margin-top: 12px; font-weight: bold; border-radius: 6px; cursor: pointer; width: 100%;">رفع الملف وحفظه فوراً ليظهر للطلاب</button>
            </form>
            <p style="margin-top: 15px; color: #00f2c3; font-weight: bold;">الملفات المخزنة حالياً:</p>
            <ul>
                {% for f in files_list %}
                    <li style="padding: 8px; border-bottom: 1px solid #222;">📄 {{ f }}</li>
                {% else %}
                    <li style="color: #777;">لم يتم رفع أي ملفات حتى الآن.</li>
                {% endfor %}
            </ul>
        </div>

        <div class="section-box">
            <h3 style="color: #00f2c3;">👥 إدارة شؤون الطلاب المسجلين</h3>
            <table>
                <tr>
                    <th>اسم الطالب</th>
                    <th>رقم التواصل</th>
                    <th>رقم الجلوس</th>
                    <th>الحالة الأكاديمية</th>
                    <th>الإجراءات السيادية</th>
                </tr>
                {% for s in students %}
                <tr>
                    <td>{{ s.name }}</td>
                    <td>{{ s.phone }}</td>
                    <td>{{ s.student_id }}</td>
                    <td style="font-weight: bold; color: {% if s.status == 'مقبول' %}#27ae60{% elif s.status == 'مرفوض' %}#c0392b{% else %}#f39c12{% endif %};">{{ s.status }}</td>
                    <td>
                        <a href="/admin/action/{{ loop.index0 }}/accept" class="btn-act accept">قبول</a>
                        <a href="/admin/action/{{ loop.index0 }}/reject" class="btn-act reject">رفض</a>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>
</body>
</html>
"""

# مسارات التطبيق البرمجية
@app.route('/', methods=['GET', 'POST'])
def student_portal():
    student_status = None
    searched_id = request.args.get('check_id')
    
    if searched_id:
        found = next((s for s in students_database if s['student_id'] == searched_id), None)
        if found:
            student_status = found['status']
        else:
            student_status = 'قيد الانتظار'

    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        student_id = request.form.get('student_id')
        if name and phone and student_id:
            exists = next((s for s in students_database if s['student_id'] == student_id), None)
            if not exists:
                students_database.append({'name': name, 'phone': phone, 'student_id': student_id, 'status': 'قيد الانتظار'})
            student_status = 'قيد الانتظار'
            searched_id = student_id

    return render_template_string(student_template, student_status=student_status, searched_id=searched_id)

@app.route('/section/<sec_name>')
def open_section(sec_name):
    files = os.listdir(UPLOAD_FOLDER)
    if sec_name == 'midterms':
        title = "بنك أسئلة ومراجعات اختبارات الميد (Midterms)"
    elif sec_name == 'finals':
        title = "أرشيف اختبارات الفاينل والتجميعات الشاملة"
    elif sec_name == 'quizzes':
        return render_template_string(quiz_template)
    else:
        title = "محتوى المنصة الأكاديمي"
    return render_template_string(section_template, title=title, files=files)

@app.route('/section/quizzes', methods=['POST'])
def submit_quiz():
    ans = request.form.get('q1')
    result = "نتيجة ممتازة ورائعة! إجابتك صحيحة وتم تسجيل تفاعلك بنجاح." if ans == 'right' else "إجابة خاطئة، حاول مراجعة المحاضرات والملخصات المرفوعة."
    return render_template_string(quiz_template, result=result)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/hakim-secure-command-room-999', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_auth'):
        return redirect(url_for('admin_dashboard'))
    error = False
    if request.method == 'POST':
        if request.form.get('pin') == ADMIN_PIN:
            session['admin_auth'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = True
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head><meta charset="UTF-8"><title>دخول المشرف</title></head>
    <body style="font-family:Tahoma; background:#0f1016; color:#fff; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
        <div style="background:#1a1c29; padding:40px; border-radius:12px; width:350px; text-align:center; border:1px solid #e74c3c;">
            <h2 style="color:#e74c3c;">غرفة القيادة السيادية</h2>
            <form method="POST">
                <input type="password" name="pin" required placeholder="أدخل الرمز السري (999)" style="width:100%; padding:12px; margin:15px 0; background:#11121a; border:1px solid #333; color:#fff; border-radius:6px; box-sizing:border-box; text-align:center; font-size:18px;">
                <button type="submit" style="background:#e74c3c; color:#fff; border:none; padding:12px; width:100%; font-weight:bold; border-radius:6px; cursor:pointer;">دخول النظام</button>
            </form>
            {% if error %}<p style="color:#e74c3c; margin-top:10px;">الرمز غير صحيح!</p>{% endif %}
            <a href="/" style="display:block; margin-top:15px; color:#00f2c3; text-decoration:none;">← العودة للمنصة الرئيسية</a>
        </div>
    </body></html>
    """, error=error)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_auth'):
        return redirect(url_for('admin_login'))
    files_list = os.listdir(UPLOAD_FOLDER)
    return render_template_string(admin_dashboard_template, students=students_database, files_list=files_list)

@app.route('/admin/action/<int:idx>/<action_type>')
def admin_action(idx, action_type):
    if not session.get('admin_auth'):
        return redirect(url_for('admin_login'))
    if 0 <= idx < len(students_database):
        if action_type == 'accept':
            students_database[idx]['status'] = 'مقبول'
        elif action_type == 'reject':
            students_database[idx]['status'] = 'مرفوض'
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/upload', methods=['POST'])
def admin_upload():
    if not session.get('admin_auth'):
        return redirect(url_for('admin_login'))
    f = request.files.get('study_file')
    if f and f.filename != '':
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_auth', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
