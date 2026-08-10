import os
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'hakim_ultimate_portal_secret_2026'

# قاعدة بيانات مؤقتة للطلاب والملفات
students_database = [
    {'name': 'حكيم (تجريبي)', 'phone': '0500000000', 'student_id': '101', 'status': 'مقبول'}
]
uploaded_files = []

ADMIN_PIN = "999"

# قالب صفحة الطالب المتكاملة
student_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>منصة حكيم التعليمية</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #1e1e2f; color: #fff; text-align: center; padding: 30px; }
        .container { background: #27293d; max-width: 600px; margin: auto; padding: 40px; border-radius: 12px; box-shadow: 0 8px 20px rgba(0,0,0,0.5); }
        h1 { color: #00f2c3; }
        input { width: 90%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #444; background: #1a1a24; color: #fff; font-size: 16px; }
        button { background: #00f2c3; color: #1e1e2f; border: none; padding: 12px 25px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; margin-top: 15px; width: 95%; }
        button:hover { background: #00c8a0; }
        .alert-pending { background: #ffaa00; color: #1e1e2f; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; }
        .alert-accepted { background: #2ecc71; color: #fff; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; }
        .alert-rejected { background: #e74c3c; color: #fff; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; }
        .sections-grid { display: grid; grid-template-columns: 1fr; gap: 15px; margin-top: 20px; }
        .section-card { background: #1a1a24; padding: 20px; border-radius: 8px; border: 1px solid #00f2c3; text-align: right; }
        .section-card h3 { color: #00f2c3; margin-top: 0; }
        .search-box { margin-bottom: 25px; padding-bottom: 20px; border-bottom: 1px solid #444; }
    </style>
</head>
<body>
    <div class="container">
        <h1>منصة حكيم التعليمية</h1>
        
        <div class="search-box">
            <p>استعلم عن حالة طلبك برقم الجلوس أو التخصص:</p>
            <form method="GET" action="/">
                <input type="text" name="check_id" placeholder="أدخل رقم الجلوس" value="{{ searched_id or '' }}">
                <button type="submit" style="background: #4e5d6c; color: #fff; font-size: 14px; padding: 8px; width: auto;">بحث</button>
            </form>
        </div>

        {% if student_status == 'قيد الانتظار' %}
            <div class="alert-pending">تم إرسال طلبك بنجاح! طلبك الآن قيد الانتظار لمراجعة المشرف.</div>
        {% elif student_status == 'مقبول' %}
            <div class="alert-accepted">🎉 مبروك! تم قبولك في المنصة بنجاح. أهلاً بك.</div>
            <div class="sections-grid">
                <div class="section-card">
                    <h3>📚 اختبارات الميد (Midterms)</h3>
                    <p>محتوى اختبارات النصف الدراسي والخطط المقررة.</p>
                </div>
                <div class="section-card">
                    <h3>🎓 اختبارات الفاينل (Finals)</h3>
                    <p>المراجعات النهائية والتجميعات الشاملة.</p>
                </div>
                <div class="section-card">
                    <h3>📝 الواجبات والكويزات</h3>
                    <p>التمارين والاختبارات القصيرة والتحليل الذكي.</p>
                </div>
            </div>
        {% elif student_status == 'مرفوض' %}
            <div class="alert-rejected">❌ نعتذر منك، تم رفض الطلب من قبل المشرف.</div>
        {% endif %}

        {% if not searched_id and not student_status %}
            <p>سجل بياناتك للانضمام للمنصة:</p>
            <form method="POST">
                <input type="text" name="name" placeholder="الاسم الكامل" required><br>
                <input type="text" name="phone" placeholder="رقم الهاتف / التواصل" required><br>
                <input type="text" name="student_id" placeholder="رقم الجلوس أو التخصص" required><br>
                <button type="submit">إرسال طلب الانضمام</button>
            </form>
        {% endif %}
    </div>
</body>
</html>
"""

# قالب تسجيل دخول المشرف
admin_login_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>دخول المشرف - منصة حكيم</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #1e1e2f; color: #fff; text-align: center; padding-top: 100px; }
        .container { background: #27293d; max-width: 400px; margin: auto; padding: 40px; border-radius: 12px; box-shadow: 0 8px 20px rgba(0,0,0,0.5); }
        h1 { color: #ff5252; }
        input { width: 85%; padding: 12px; margin: 15px 0; border-radius: 8px; border: 1px solid #444; background: #1a1a24; color: #fff; font-size: 18px; text-align: center; }
        button { background: #ff5252; color: #fff; border: none; padding: 12px 25px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; width: 90%; }
        .error { color: #ff5252; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 غرفة القيادة</h1>
        <p>أدخل رمز المشرف السري (999)</p>
        <form method="POST">
            <input type="password" name="pin" placeholder="الرمز السري" required><br>
            <button type="submit">دخول</button>
        </form>
        {% if error %}
            <div class="error">الرمز غير صحيح!</div>
        {% endif %}
    </div>
</body>
</html>
"""

# قالب لوحة تحكم المشرف الشاملة
admin_dashboard_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>لوحة قيادة المشرف - حكيم</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #1e1e2f; color: #fff; padding: 20px; }
        .container { max-width: 1000px; margin: auto; background: #27293d; padding: 30px; border-radius: 12px; box-shadow: 0 8px 20px rgba(0,0,0,0.5); }
        h1 { color: #00f2c3; text-align: center; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #1a1a24; border-radius: 8px; overflow: hidden; }
        th, td { padding: 12px; text-align: center; border-bottom: 1px solid #444; }
        th { background: #00f2c3; color: #1e1e2f; }
        .btn-accept { background: #2ecc71; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-weight: bold; }
        .btn-reject { background: #e74c3c; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-weight: bold; }
        .btn-edit { background: #3498db; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-weight: bold; }
        .box { background: #1a1a24; padding: 20px; border-radius: 8px; margin-top: 20px; border: 1px solid #444; text-align: right; }
        .logout { float: left; color: #ff5252; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/hakim-secure-command-room-999/logout" class="logout">تسجيل الخروج 🚪</a>
        <h1>🛡️ غرفة القيادة والتحكم الشاملة - حكيم</h1>
        
        <!-- قسم رفع الكتب والتجميعات للذكاء الاصطناعي -->
        <div class="box">
            <h3>📁 رفع الكتب والتجميعات والملفات (للتحليل الذكي)</h3>
            <form method="POST" action="/hakim-secure-command-room-999/upload" enctype="multipart/form-data">
                <input type="file" name="file" required style="background: #27293d; padding: 8px; color:#fff;"><br>
                <button type="submit" style="background: #00f2c3; color: #1e1e2f; width: auto; padding: 8px 20px; margin-top: 10px; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">رفع الملف وتفعيل التحليل</button>
            </form>
            <p style="margin-top: 10px; color: #aaa; font-size: 14px;">الملفات المرفوعة حالياً: {{ files_count }} ملف</p>
        </div>

        <!-- قسم إدارة الطلاب المتقدمين -->
        <div class="box">
            <h3>👥 إدارة الطلاب المسجلين</h3>
            <table>
                <tr>
                    <th>الاسم</th>
                    <th>الهاتف</th>
                    <th>رقم الجلوس / التخصص</th>
                    <th>الحالة</th>
                    <th>التحكم والإجراءات</th>
                </tr>
                {% for s in students %}
                <tr>
                    <td>{{ s.name }}</td>
                    <td>{{ s.phone }}</td>
                    <td>{{ s.student_id }}</td>
                    <td>{{ s.status }}</td>
                    <td>
                        <a href="/hakim-secure-command-room-999/action/{{ loop.index0 }}/accept" class="btn-accept">قبول</a>
                        <a href="/hakim-secure-command-room-999/action/{{ loop.index0 }}/reject" class="btn-reject">رفض</a>
                        <a href="/hakim-secure-command-room-999/edit/{{ loop.index0 }}" class="btn-edit">تعديل</a>
                    </td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="5">لا توجد طلبات تسجيل حتى الآن.</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>
</body>
</html>
"""

# قالب صفحة تعديل طالب محدد
edit_student_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تعديل بيانات الطالب - حكيم</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #1e1e2f; color: #fff; padding: 50px; text-align: center; }
        .container { background: #27293d; max-width: 400px; margin: auto; padding: 30px; border-radius: 12px; }
        input { width: 90%; padding: 10px; margin: 10px 0; border-radius: 6px; background: #1a1a24; border: 1px solid #444; color: #fff; }
        button { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; width: 95%; }
    </style>
</head>
<body>
    <div class="container">
        <h2>تعديل بيانات الطالب</h2>
        <form method="POST">
            <input type="text" name="name" value="{{ student.name }}" required><br>
            <input type="text" name="phone" value="{{ student.phone }}" required><br>
            <input type="text" name="student_id" value="{{ student.student_id }}" required><br>
            <button type="submit">حفظ التعديلات</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def student_portal():
    student_status = None
    searched_id = request.args.get('check_id')
    
    if searched_id:
        s_found = next((s for s in students_database if s['student_id'] == searched_id), None)
        if s_found:
            student_status = s_found['status']
        else:
            student_status = 'قيد الانتظار'

    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        student_id = request.form.get('student_id')
        if name and phone and student_id:
            existing = next((s for s in students_database if s['student_id'] == student_id), None)
            if not existing:
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
    if session.get('admin_logged'):
        return redirect(url_for('admin_dashboard'))
    
    error = False
    if request.method == 'POST':
        if request.form.get('pin') == ADMIN_PIN:
            session['admin_logged'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = True
    return render_template_string(admin_login_template, error=error)

@app.route('/hakim-secure-command-room-999/dashboard')
def admin_dashboard():
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))
    return render_template_string(admin_dashboard_template, students=students_database, files_count=len(uploaded_files))

@app.route('/hakim-secure-command-room-999/action/<int:index>/<action_type>')
def admin_action(index, action_type):
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))
    if 0 <= index < len(students_database):
        if action_type == 'accept':
            students_database[index]['status'] = 'مقبول'
        elif action_type == 'reject':
            students_database[index]['status'] = 'مرفوض'
    return redirect(url_for('admin_dashboard'))

@app.route('/hakim-secure-command-room-999/edit/<int:index>', methods=['GET', 'POST'])
def edit_student(index):
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))
    if index < 0 or index >= len(students_database):
        return redirect(url_for('admin_dashboard'))
    
    student = students_database[index]
    if request.method == 'POST':
        student['name'] = request.form.get('name')
        student['phone'] = request.form.get('phone')
        student['student_id'] = request.form.get('student_id')
        return redirect(url_for('admin_dashboard'))
        
    return render_template_string(edit_student_template, student=student)

@app.route('/hakim-secure-command-room-999/upload', methods=['POST'])
def upload_file():
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))
    f = request.files.get('file')
    if f:
        uploaded_files.append(f.filename)
    return redirect(url_for('admin_dashboard'))

@app.route('/hakim-secure-command-room-999/logout')
def admin_logout():
    session.pop('admin_logged', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
