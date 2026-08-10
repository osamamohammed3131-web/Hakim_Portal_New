import os
from flask import Flask, render_template_string, request, redirect, url_for, session, send_from_directory

app = Flask(__name__)
app.secret_key = 'hakim_elite_university_portal_2026'

# إعداد مجلدات التخزين الفعلي للملفات والكتب والتجميعات
UPLOAD_FOLDER = 'server_storage'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# قاعدة بيانات الطلاب الافتراضية
students_database = [
    {'name': 'حكيم (المشرف العام)', 'phone': '0500000000', 'student_id': 'admin777', 'status': 'مقبول'}
]

# الرمز السري لغرفة القيادة
ADMIN_PIN = "999"

# 1. واجهة الطالب الأكاديمية المتكاملة
student_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>منصة حكيم الأكاديمية</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #0f1016; color: #fff; margin: 0; padding: 0; }
        .header { background: #1a1c29; padding: 20px; text-align: center; border-bottom: 2px solid #00f2c3; }
        .header h1 { color: #00f2c3; margin: 0; }
        .main-container { max-width: 900px; margin: 30px auto; padding: 20px; }
        .card { background: #1a1c29; padding: 30px; border-radius: 12px; box-shadow: 0 8px 25px rgba(0,0,0,0.6); margin-bottom: 20px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #333; background: #11121a; color: #fff; box-sizing: border-box; }
        button { background: #00f2c3; color: #0f1016; border: none; padding: 12px 25px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; width: 100%; margin-top: 10px; }
        button:hover { background: #00c8a0; }
        .alert-pending { background: #f39c12; color: #0f1016; padding: 15px; border-radius: 8px; font-weight: bold; text-align: center; }
        .alert-accepted { background: #27ae60; color: #fff; padding: 15px; border-radius: 8px; font-weight: bold; text-align: center; }
        .alert-rejected { background: #c0392b; color: #fff; padding: 15px; border-radius: 8px; font-weight: bold; text-align: center; }
        .grid-sections { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 25px; }
        .sec-box { background: #11121a; padding: 20px; border-radius: 10px; border: 1px solid #00f2c3; text-align: right; }
        .sec-box h3 { color: #00f2c3; margin-top: 0; }
        .sec-box a { color: #fff; text-decoration: none; background: #00f2c3; color: #0f1016; padding: 6px 12px; border-radius: 5px; display: inline-block; margin-top: 10px; font-weight: bold; font-size: 14px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>منصة حكيم الأكاديمية التفاعلية</h1>
        <p>البوابة الرسمية للتحضير والاختبارات الذكية</p>
    </div>

    <div class="main-container">
        <div class="card">
            <div style="text-align: center; margin-bottom: 20px;">
                <h3>استعلام عن حالة الحساب برقم الجلوس:</h3>
                <form method="GET" action="/">
                    <input type="text" name="check_id" placeholder="أدخل رقم الجلوس الخاص بك" value="{{ searched_id or '' }}" style="max-width: 400px; display: inline-block;">
                    <button type="submit" style="max-width: 150px; display: inline-block; padding: 10px;">تحقق</button>
                </form>
            </div>

            {% if student_status == 'قيد الانتظار' %}
                <div class="alert-pending">طلبك مسجل وقيد المراجعة الإدارية من قبل المشرف.</div>
            {% elif student_status == 'مقبول' %}
                <div class="alert-accepted">أهلاً بك في بيئة التعلم المتقدمة. تم تفعيل حسابك بنجاح!</div>
                <div class="grid-sections">
                    <div class="sec-box">
                        <h3>📚 اختبارات الميد (Midterms)</h3>
                        <p>ملخصات، بنوك أسئلة، ومراجعات النصف الدراسي الأول والثاني.</p>
                        <a href="#midterm">استعرض المحتوى</a>
                    </div>
                    <div class="sec-box">
                        <h3>🎓 اختبارات الفاينل (Finals)</h3>
                        <p>التجميعات الشاملة، الاختبارات السابقة، ونماذج الإجابة.</p>
                        <a href="#final">استعرض التجميعات</a>
                    </div>
                    <div class="sec-box">
                        <h3>📝 الواجبات والكويزات الذكية</h3>
                        <p>تدريبات تفاعلية يحللها الذكاء الاصطناعي خصيصاً لمستواك.</p>
                        <a href="#quizzes">ابدأ التدريب</a>
                    </div>
                </div>
            {% elif student_status == 'مرفوض' %}
                <div class="alert-rejected">نعتذر، عذراً تم رفض الطلب أو إلغاء التصريح.</div>
            {% endif %}

            {% if not searched_id and not student_status %}
                <h3 style="text-align: center; color: #00f2c3;">التسجيل الأكاديمي للانضمام للمنصة</h3>
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
        </div>
    </div>
</body>
</html>
"""

# 2. واجهة دخول المشرف
admin_login_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>دخول غرفة القيادة - حكيم</title>
    <style>
        body { font-family: Tahoma; background: #0f1016; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-card { background: #1a1c29; padding: 40px; border-radius: 12px; width: 350px; text-align: center; border: 1px solid #e74c3c; }
        input { width: 100%; padding: 12px; margin: 15px 0; background: #11121a; border: 1px solid #333; color: #fff; border-radius: 6px; box-sizing: border-box; text-align: center; font-size: 18px; }
        button { background: #e74c3c; color: #fff; border: none; padding: 12px; width: 100%; font-weight: bold; border-radius: 6px; cursor: pointer; }
        .error { color: #e74c3c; margin-top: 10px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2 style="color: #e74c3c;">غرفة القيادة السيادية</h2>
        <form method="POST">
            <input type="password" name="pin" required placeholder="أدخل الرمز السري">
            <button type="submit">دخول النظام</button>
        </form>
        {% if error %}
            <div class="error">الرمز السري غير صحيح!</div>
        {% endif %}
    </div>
</body>
</html>
"""

# 3. لوحة تحكم المشرف الشاملة والمتقدمة
admin_dashboard_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>لوحة التحكم والتحليل الذكي - حكيم</title>
    <style>
        body { font-family: Tahoma; background: #0f1016; color: #fff; padding: 20px; margin: 0; }
        .container { max-width: 1000px; margin: auto; background: #1a1c29; padding: 30px; border-radius: 12px; }
        h1 { color: #00f2c3; text-align: center; }
        .section-box { background: #11121a; padding: 20px; border-radius: 8px; margin-top: 20px; border: 1px solid #333; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px; text-align: center; border-bottom: 1px solid #222; }
        th { background: #00f2c3; color: #0f1016; }
        .btn-act { padding: 5px 10px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 13px; display: inline-block; margin: 2px; }
        .accept { background: #27ae60; color: #fff; }
        .reject { background: #c0392b; color: #fff; }
        .edit { background: #2980b9; color: #fff; }
        .logout { float: left; color: #e74c3c; text-decoration: none; font-weight: bold; }
        input[type="file"] { background: #1a1c29; padding: 10px; border: 1px dashed #00f2c3; width: 100%; box-sizing: border-box; color: #fff; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/admin/logout" class="logout">تسجيل الخروج 🚪</a>
        <h1>لوحة تحكم المشرف والمحتوى الأكاديمي</h1>

        <!-- قسم رفع ملفات الذكاء الاصطناعي والمناهج -->
        <div class="section-box">
            <h3>📁 مستودع الكتب والتجميعات (لتغذية التحليل الذكي)</h3>
            <form method="POST" action="/admin/upload" enctype="multipart/form-data">
                <input type="file" name="study_file" required>
                <button type="submit" style="background: #00f2c3; color: #0f1016; border: none; padding: 10px 20px; margin-top: 10px; font-weight: bold; border-radius: 5px; cursor: pointer;">رفع الملف وتأكيد الحفظ على السيرفر</button>
            </form>
            <p style="margin-top: 15px; color: #00f2c3; font-weight: bold;">الملفات المتاحة حالياً على السيرفر:</p>
            <ul>
                {% for f in files_list %}
                    <li>{{ f }}</li>
                {% else %}
                    <li style="color: #777;">لم يتم رفع أي ملفات حتى الآن.</li>
                {% endfor %}
            </ul>
        </div>

        <!-- قسم إدارة الطلاب المتقدمين -->
        <div class="section-box">
            <h3>👥 إدارة شؤون الطلاب المسجلين</h3>
            <table>
                <tr>
                    <th>اسم الطالب</th>
                    <th>رقم التواصل</th>
                    <th>رقم الجلوس</th>
                    <th>الحالة</th>
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
                        <a href="/admin/edit/{{ loop.index0 }}" class="btn-act edit">تعديل</a>
                    </td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="5" style="color: #777;">لا توجد طلبات معلقة حالياً.</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>
</body>
</html>
"""

# مسارات التطبيق البرمجية الأساسية
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
                students_database.append({
                    'name': name,
                    'phone': phone,
                    'student_id': student_id,
                    'status': 'قيد الانتظار'
                })
            student_status = 'قيد الانتظار'
            searched_id = student_id

    return render_template_string(student_template, student_status=student_status, searched_id=searched_id)

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
    return render_template_string(admin_login_template, error=error)

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
    app.run(host='0.0.0.0', port=10000)import os
from flask import Flask, render_template_string, request, redirect, url_for, session, send_from_directory

app = Flask(__name__)
app.secret_key = 'hakim_elite_university_portal_2026'

# إعداد مجلدات التخزين الفعلي للملفات والكتب والتجميعات
UPLOAD_FOLDER = 'server_storage'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# قاعدة بيانات الطلاب الافتراضية
students_database = [
    {'name': 'حكيم (المشرف العام)', 'phone': '0500000000', 'student_id': 'admin777', 'status': 'مقبول'}
]

# الرمز السري لغرفة القيادة
ADMIN_PIN = "999"

# 1. واجهة الطالب الأكاديمية المتكاملة
student_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>منصة حكيم الأكاديمية</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #0f1016; color: #fff; margin: 0; padding: 0; }
        .header { background: #1a1c29; padding: 20px; text-align: center; border-bottom: 2px solid #00f2c3; }
        .header h1 { color: #00f2c3; margin: 0; }
        .main-container { max-width: 900px; margin: 30px auto; padding: 20px; }
        .card { background: #1a1c29; padding: 30px; border-radius: 12px; box-shadow: 0 8px 25px rgba(0,0,0,0.6); margin-bottom: 20px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #333; background: #11121a; color: #fff; box-sizing: border-box; }
        button { background: #00f2c3; color: #0f1016; border: none; padding: 12px 25px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; width: 100%; margin-top: 10px; }
        button:hover { background: #00c8a0; }
        .alert-pending { background: #f39c12; color: #0f1016; padding: 15px; border-radius: 8px; font-weight: bold; text-align: center; }
        .alert-accepted { background: #27ae60; color: #fff; padding: 15px; border-radius: 8px; font-weight: bold; text-align: center; }
        .alert-rejected { background: #c0392b; color: #fff; padding: 15px; border-radius: 8px; font-weight: bold; text-align: center; }
        .grid-sections { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 25px; }
        .sec-box { background: #11121a; padding: 20px; border-radius: 10px; border: 1px solid #00f2c3; text-align: right; }
        .sec-box h3 { color: #00f2c3; margin-top: 0; }
        .sec-box a { color: #fff; text-decoration: none; background: #00f2c3; color: #0f1016; padding: 6px 12px; border-radius: 5px; display: inline-block; margin-top: 10px; font-weight: bold; font-size: 14px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>منصة حكيم الأكاديمية التفاعلية</h1>
        <p>البوابة الرسمية للتحضير والاختبارات الذكية</p>
    </div>

    <div class="main-container">
        <div class="card">
            <div style="text-align: center; margin-bottom: 20px;">
                <h3>استعلام عن حالة الحساب برقم الجلوس:</h3>
                <form method="GET" action="/">
                    <input type="text" name="check_id" placeholder="أدخل رقم الجلوس الخاص بك" value="{{ searched_id or '' }}" style="max-width: 400px; display: inline-block;">
                    <button type="submit" style="max-width: 150px; display: inline-block; padding: 10px;">تحقق</button>
                </form>
            </div>

            {% if student_status == 'قيد الانتظار' %}
                <div class="alert-pending">طلبك مسجل وقيد المراجعة الإدارية من قبل المشرف.</div>
            {% elif student_status == 'مقبول' %}
                <div class="alert-accepted">أهلاً بك في بيئة التعلم المتقدمة. تم تفعيل حسابك بنجاح!</div>
                <div class="grid-sections">
                    <div class="sec-box">
                        <h3>📚 اختبارات الميد (Midterms)</h3>
                        <p>ملخصات، بنوك أسئلة، ومراجعات النصف الدراسي الأول والثاني.</p>
                        <a href="#midterm">استعرض المحتوى</a>
                    </div>
                    <div class="sec-box">
                        <h3>🎓 اختبارات الفاينل (Finals)</h3>
                        <p>التجميعات الشاملة، الاختبارات السابقة، ونماذج الإجابة.</p>
                        <a href="#final">استعرض التجميعات</a>
                    </div>
                    <div class="sec-box">
                        <h3>📝 الواجبات والكويزات الذكية</h3>
                        <p>تدريبات تفاعلية يحللها الذكاء الاصطناعي خصيصاً لمستواك.</p>
                        <a href="#quizzes">ابدأ التدريب</a>
                    </div>
                </div>
            {% elif student_status == 'مرفوض' %}
                <div class="alert-rejected">نعتذر، عذراً تم رفض الطلب أو إلغاء التصريح.</div>
            {% endif %}

            {% if not searched_id and not student_status %}
                <h3 style="text-align: center; color: #00f2c3;">التسجيل الأكاديمي للانضمام للمنصة</h3>
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
        </div>
    </div>
</body>
</html>
"""

# 2. واجهة دخول المشرف
admin_login_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>دخول غرفة القيادة - حكيم</title>
    <style>
        body { font-family: Tahoma; background: #0f1016; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-card { background: #1a1c29; padding: 40px; border-radius: 12px; width: 350px; text-align: center; border: 1px solid #e74c3c; }
        input { width: 100%; padding: 12px; margin: 15px 0; background: #11121a; border: 1px solid #333; color: #fff; border-radius: 6px; box-sizing: border-box; text-align: center; font-size: 18px; }
        button { background: #e74c3c; color: #fff; border: none; padding: 12px; width: 100%; font-weight: bold; border-radius: 6px; cursor: pointer; }
        .error { color: #e74c3c; margin-top: 10px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2 style="color: #e74c3c;">غرفة القيادة السيادية</h2>
        <form method="POST">
            <input type="password" name="pin" required placeholder="أدخل الرمز السري">
            <button type="submit">دخول النظام</button>
        </form>
        {% if error %}
            <div class="error">الرمز السري غير صحيح!</div>
        {% endif %}
    </div>
</body>
</html>
"""

# 3. لوحة تحكم المشرف الشاملة والمتقدمة
admin_dashboard_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>لوحة التحكم والتحليل الذكي - حكيم</title>
    <style>
        body { font-family: Tahoma; background: #0f1016; color: #fff; padding: 20px; margin: 0; }
        .container { max-width: 1000px; margin: auto; background: #1a1c29; padding: 30px; border-radius: 12px; }
        h1 { color: #00f2c3; text-align: center; }
        .section-box { background: #11121a; padding: 20px; border-radius: 8px; margin-top: 20px; border: 1px solid #333; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px; text-align: center; border-bottom: 1px solid #222; }
        th { background: #00f2c3; color: #0f1016; }
        .btn-act { padding: 5px 10px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 13px; display: inline-block; margin: 2px; }
        .accept { background: #27ae60; color: #fff; }
        .reject { background: #c0392b; color: #fff; }
        .edit { background: #2980b9; color: #fff; }
        .logout { float: left; color: #e74c3c; text-decoration: none; font-weight: bold; }
        input[type="file"] { background: #1a1c29; padding: 10px; border: 1px dashed #00f2c3; width: 100%; box-sizing: border-box; color: #fff; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/admin/logout" class="logout">تسجيل الخروج 🚪</a>
        <h1>لوحة تحكم المشرف والمحتوى الأكاديمي</h1>

        <!-- قسم رفع ملفات الذكاء الاصطناعي والمناهج -->
        <div class="section-box">
            <h3>📁 مستودع الكتب والتجميعات (لتغذية التحليل الذكي)</h3>
            <form method="POST" action="/admin/upload" enctype="multipart/form-data">
                <input type="file" name="study_file" required>
                <button type="submit" style="background: #00f2c3; color: #0f1016; border: none; padding: 10px 20px; margin-top: 10px; font-weight: bold; border-radius: 5px; cursor: pointer;">رفع الملف وتأكيد الحفظ على السيرفر</button>
            </form>
            <p style="margin-top: 15px; color: #00f2c3; font-weight: bold;">الملفات المتاحة حالياً على السيرفر:</p>
            <ul>
                {% for f in files_list %}
                    <li>{{ f }}</li>
                {% else %}
                    <li style="color: #777;">لم يتم رفع أي ملفات حتى الآن.</li>
                {% endfor %}
            </ul>
        </div>

        <!-- قسم إدارة الطلاب المتقدمين -->
        <div class="section-box">
            <h3>👥 إدارة شؤون الطلاب المسجلين</h3>
            <table>
                <tr>
                    <th>اسم الطالب</th>
                    <th>رقم التواصل</th>
                    <th>رقم الجلوس</th>
                    <th>الحالة</th>
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
                        <a href="/admin/edit/{{ loop.index0 }}" class="btn-act edit">تعديل</a>
                    </td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="5" style="color: #777;">لا توجد طلبات معلقة حالياً.</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>
</body>
</html>
"""

# مسارات التطبيق البرمجية الأساسية
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
                students_database.append({
                    'name': name,
                    'phone': phone,
                    'student_id': student_id,
                    'status': 'قيد الانتظار'
                })
            student_status = 'قيد الانتظار'
            searched_id = student_id

    return render_template_string(student_template, student_status=student_status, searched_id=searched_id)

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
    return render_template_string(admin_login_template, error=error)

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
    app.run(host='0.0.0.0', port=10000)import os
from flask import Flask, render_template_string, request, redirect, url_for, session, send_from_directory

app = Flask(__name__)
app.secret_key = 'hakim_elite_university_portal_2026'

# إعداد مجلدات التخزين الفعلي للملفات والكتب والتجميعات
UPLOAD_FOLDER = 'server_storage'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# قاعدة بيانات الطلاب الافتراضية
students_database = [
    {'name': 'حكيم (المشرف العام)', 'phone': '0500000000', 'student_id': 'admin777', 'status': 'مقبول'}
]

# الرمز السري لغرفة القيادة
ADMIN_PIN = "999"

# 1. واجهة الطالب الأكاديمية المتكاملة
student_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>منصة حكيم الأكاديمية</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #0f1016; color: #fff; margin: 0; padding: 0; }
        .header { background: #1a1c29; padding: 20px; text-align: center; border-bottom: 2px solid #00f2c3; }
        .header h1 { color: #00f2c3; margin: 0; }
        .main-container { max-width: 900px; margin: 30px auto; padding: 20px; }
        .card { background: #1a1c29; padding: 30px; border-radius: 12px; box-shadow: 0 8px 25px rgba(0,0,0,0.6); margin-bottom: 20px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #333; background: #11121a; color: #fff; box-sizing: border-box; }
        button { background: #00f2c3; color: #0f1016; border: none; padding: 12px 25px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; width: 100%; margin-top: 10px; }
        button:hover { background: #00c8a0; }
        .alert-pending { background: #f39c12; color: #0f1016; padding: 15px; border-radius: 8px; font-weight: bold; text-align: center; }
        .alert-accepted { background: #27ae60; color: #fff; padding: 15px; border-radius: 8px; font-weight: bold; text-align: center; }
        .alert-rejected { background: #c0392b; color: #fff; padding: 15px; border-radius: 8px; font-weight: bold; text-align: center; }
        .grid-sections { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 25px; }
        .sec-box { background: #11121a; padding: 20px; border-radius: 10px; border: 1px solid #00f2c3; text-align: right; }
        .sec-box h3 { color: #00f2c3; margin-top: 0; }
        .sec-box a { color: #fff; text-decoration: none; background: #00f2c3; color: #0f1016; padding: 6px 12px; border-radius: 5px; display: inline-block; margin-top: 10px; font-weight: bold; font-size: 14px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>منصة حكيم الأكاديمية التفاعلية</h1>
        <p>البوابة الرسمية للتحضير والاختبارات الذكية</p>
    </div>

    <div class="main-container">
        <div class="card">
            <div style="text-align: center; margin-bottom: 20px;">
                <h3>استعلام عن حالة الحساب برقم الجلوس:</h3>
                <form method="GET" action="/">
                    <input type="text" name="check_id" placeholder="أدخل رقم الجلوس الخاص بك" value="{{ searched_id or '' }}" style="max-width: 400px; display: inline-block;">
                    <button type="submit" style="max-width: 150px; display: inline-block; padding: 10px;">تحقق</button>
                </form>
            </div>

            {% if student_status == 'قيد الانتظار' %}
                <div class="alert-pending">طلبك مسجل وقيد المراجعة الإدارية من قبل المشرف.</div>
            {% elif student_status == 'مقبول' %}
                <div class="alert-accepted">أهلاً بك في بيئة التعلم المتقدمة. تم تفعيل حسابك بنجاح!</div>
                <div class="grid-sections">
                    <div class="sec-box">
                        <h3>📚 اختبارات الميد (Midterms)</h3>
                        <p>ملخصات، بنوك أسئلة، ومراجعات النصف الدراسي الأول والثاني.</p>
                        <a href="#midterm">استعرض المحتوى</a>
                    </div>
                    <div class="sec-box">
                        <h3>🎓 اختبارات الفاينل (Finals)</h3>
                        <p>التجميعات الشاملة، الاختبارات السابقة، ونماذج الإجابة.</p>
                        <a href="#final">استعرض التجميعات</a>
                    </div>
                    <div class="sec-box">
                        <h3>📝 الواجبات والكويزات الذكية</h3>
                        <p>تدريبات تفاعلية يحللها الذكاء الاصطناعي خصيصاً لمستواك.</p>
                        <a href="#quizzes">ابدأ التدريب</a>
                    </div>
                </div>
            {% elif student_status == 'مرفوض' %}
                <div class="alert-rejected">نعتذر، عذراً تم رفض الطلب أو إلغاء التصريح.</div>
            {% endif %}

            {% if not searched_id and not student_status %}
                <h3 style="text-align: center; color: #00f2c3;">التسجيل الأكاديمي للانضمام للمنصة</h3>
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
        </div>
    </div>
</body>
</html>
"""

# 2. واجهة دخول المشرف
admin_login_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>دخول غرفة القيادة - حكيم</title>
    <style>
        body { font-family: Tahoma; background: #0f1016; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-card { background: #1a1c29; padding: 40px; border-radius: 12px; width: 350px; text-align: center; border: 1px solid #e74c3c; }
        input { width: 100%; padding: 12px; margin: 15px 0; background: #11121a; border: 1px solid #333; color: #fff; border-radius: 6px; box-sizing: border-box; text-align: center; font-size: 18px; }
        button { background: #e74c3c; color: #fff; border: none; padding: 12px; width: 100%; font-weight: bold; border-radius: 6px; cursor: pointer; }
        .error { color: #e74c3c; margin-top: 10px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2 style="color: #e74c3c;">غرفة القيادة السيادية</h2>
        <form method="POST">
            <input type="password" name="pin" required placeholder="أدخل الرمز السري">
            <button type="submit">دخول النظام</button>
        </form>
        {% if error %}
            <div class="error">الرمز السري غير صحيح!</div>
        {% endif %}
    </div>
</body>
</html>
"""

# 3. لوحة تحكم المشرف الشاملة والمتقدمة
admin_dashboard_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>لوحة التحكم والتحليل الذكي - حكيم</title>
    <style>
        body { font-family: Tahoma; background: #0f1016; color: #fff; padding: 20px; margin: 0; }
        .container { max-width: 1000px; margin: auto; background: #1a1c29; padding: 30px; border-radius: 12px; }
        h1 { color: #00f2c3; text-align: center; }
        .section-box { background: #11121a; padding: 20px; border-radius: 8px; margin-top: 20px; border: 1px solid #333; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px; text-align: center; border-bottom: 1px solid #222; }
        th { background: #00f2c3; color: #0f1016; }
        .btn-act { padding: 5px 10px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 13px; display: inline-block; margin: 2px; }
        .accept { background: #27ae60; color: #fff; }
        .reject { background: #c0392b; color: #fff; }
        .edit { background: #2980b9; color: #fff; }
        .logout { float: left; color: #e74c3c; text-decoration: none; font-weight: bold; }
        input[type="file"] { background: #1a1c29; padding: 10px; border: 1px dashed #00f2c3; width: 100%; box-sizing: border-box; color: #fff; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/admin/logout" class="logout">تسجيل الخروج 🚪</a>
        <h1>لوحة تحكم المشرف والمحتوى الأكاديمي</h1>

        <!-- قسم رفع ملفات الذكاء الاصطناعي والمناهج -->
        <div class="section-box">
            <h3>📁 مستودع الكتب والتجميعات (لتغذية التحليل الذكي)</h3>
            <form method="POST" action="/admin/upload" enctype="multipart/form-data">
                <input type="file" name="study_file" required>
                <button type="submit" style="background: #00f2c3; color: #0f1016; border: none; padding: 10px 20px; margin-top: 10px; font-weight: bold; border-radius: 5px; cursor: pointer;">رفع الملف وتأكيد الحفظ على السيرفر</button>
            </form>
            <p style="margin-top: 15px; color: #00f2c3; font-weight: bold;">الملفات المتاحة حالياً على السيرفر:</p>
            <ul>
                {% for f in files_list %}
                    <li>{{ f }}</li>
                {% else %}
                    <li style="color: #777;">لم يتم رفع أي ملفات حتى الآن.</li>
                {% endfor %}
            </ul>
        </div>

        <!-- قسم إدارة الطلاب المتقدمين -->
        <div class="section-box">
            <h3>👥 إدارة شؤون الطلاب المسجلين</h3>
            <table>
                <tr>
                    <th>اسم الطالب</th>
                    <th>رقم التواصل</th>
                    <th>رقم الجلوس</th>
                    <th>الحالة</th>
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
                        <a href="/admin/edit/{{ loop.index0 }}" class="btn-act edit">تعديل</a>
                    </td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="5" style="color: #777;">لا توجد طلبات معلقة حالياً.</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>
</body>
</html>
"""

# مسارات التطبيق البرمجية الأساسية
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
                students_database.append({
                    'name': name,
                    'phone': phone,
                    'student_id': student_id,
                    'status': 'قيد الانتظار'
                })
            student_status = 'قيد الانتظار'
            searched_id = student_id

    return render_template_string(student_template, student_status=student_status, searched_id=searched_id)

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
    return render_template_string(admin_login_template, error=error)

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
