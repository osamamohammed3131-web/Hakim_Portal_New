from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'hakim_secret_key_12345'  # مفتاح الأمان للجلسات

# قاعدة بيانات مؤقتة لتخزين الطلاب المسجلين (في الذاكرة)
students_database = []

# الرمز السري الخاص بك لدخول لوحة التحكم
ADMIN_PIN = "999"

# قالب الصفحة الرئيسية لتسجيل الطالب
student_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>منصة حكيم - تسجيل الطلاب</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #1e1e2f; color: #fff; text-align: center; padding-top: 50px; }
        .container { background: #27293d; max-width: 500px; margin: auto; padding: 40px; border-radius: 12px; box-shadow: 0 8px 20px rgba(0,0,0,0.5); }
        h1 { color: #00f2c3; }
        input, select { width: 90%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #444; background: #1a1a24; color: #fff; font-size: 16px; }
        button { background: #00f2c3; color: #1e1e2f; border: none; padding: 12px 25px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; margin-top: 15px; width: 95%; }
        button:hover { background: #00c8a0; }
        .alert { background: #ffaa00; color: #1e1e2f; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>منصة حكيم التعليمية</h1>
        <p>قم بتسجيل بياناتك للانضمام إلى المنصة</p>
        {% if submitted %}
            <div class="alert">تم إرسال طلبك بنجاح! طلبك الآن قيد الانتظار لمراجعة المشرف.</div>
        {% endif %}
        <form method="POST">
            <input type="text" name="name" placeholder="الاسم الكامل" required><br>
            <input type="text" name="phone" placeholder="رقم الهاتف / التواصل" required><br>
            <input type="text" name="student_id" placeholder="رقم الجلوس أو التخصص" required><br>
            <button type="submit">إرسال الطلب</button>
        </form>
    </div>
</body>
</html>
"""

# قالب صفحة إدخال الرمز للمشرف
admin_login_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تسجيل دخول المشرف - حكيم</title>
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
        <p>الرجاء إدخال رمز المشرف للدخول</p>
        <form method="POST">
            <input type="password" name="pin" placeholder="أدخل الرمز السري" required><br>
            <button type="submit">دخول</button>
        </form>
        {% if error %}
            <div class="error">الرمز غير صحيح، حاول مرة أخرى.</div>
        {% endif %}
    </div>
</body>
</html>
"""

# قالب لوحة التحكم للمشرف (إدارة الطلاب)
admin_dashboard_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>لوحة تحكم المشرف - حكيم</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #1e1e2f; color: #fff; padding: 30px; }
        .container { max-width: 900px; margin: auto; background: #27293d; padding: 30px; border-radius: 12px; box-shadow: 0 8px 20px rgba(0,0,0,0.5); }
        h1 { color: #00f2c3; text-align: center; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #1a1a24; border-radius: 8px; overflow: hidden; }
        th, td { padding: 12px 15px; text-align: center; border-bottom: 1px solid #444; }
        th { background: #00f2c3; color: #1e1e2f; }
        .btn-accept { background: #2ecc71; color: white; padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; font-weight: bold; }
        .btn-reject { background: #e74c3c; color: white; padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; font-weight: bold; }
        .status-accepted { color: #2ecc71; font-weight: bold; }
        .status-rejected { color: #e74c3c; font-weight: bold; }
        .status-pending { color: #f1c40f; font-weight: bold; }
        .logout { display: block; text-align: left; margin-bottom: 15px; color: #ff5252; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/hakim-secure-command-room-999/logout" class="logout">تسجيل الخروج 🚪</a>
        <h1>🛡️ لوحة قيادة المشرف - طلبات الطلاب</h1>
        <table>
            <tr>
                <th>الاسم</th>
                <th>رقم الهاتف</th>
                <th>رقم الجلوس / التخصص</th>
                <th>الحالة</th>
                <th>الإجراء</th>
            </tr>
            {% for student in students %}
            <tr>
                <td>{{ student.name }}</td>
                <td>{{ student.phone }}</td>
                <td>{{ student.student_id }}</td>
                <td>
                    {% if student.status == 'مقبول' %}
                        <span class="status-accepted">مقبول</span>
                    {% elif student.status == 'مرفوض' %}
                        <span class="status-rejected">مرفوض</span>
                    {% else %}
                        <span class="status-pending">قيد الانتظار</span>
                    {% endif %}
                </td>
                <td>
                    <a href="/hakim-secure-command-room-999/action/{{ loop.index0 }}/accept" class="btn-accept">قبول</a>
                    <a href="/hakim-secure-command-room-999/action/{{ loop.index0 }}/reject" class="btn-reject">رفض</a>
                </td>
            </tr>
            {% else %}
            <tr>
                <td colspan="5">لا يوجد طلاب متقدمون حتى الآن.</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def student_portal():
    submitted = False
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        student_id = request.form.get('student_id')
        if name and phone:
            students_database.append({
                'name': name,
                'phone': phone,
                'student_id': student_id,
                'status': 'قيد الانتظار'
            })
            submitted = True
    return render_template_string(student_template, submitted=submitted)

@app.route('/hakim-secure-command-room-999', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged'):
        return render_template_string(admin_dashboard_template, students=students_database)
    
    error = False
    if request.method == 'POST':
        pin = request.form.get('pin')
        if pin == ADMIN_PIN:
            session['admin_logged'] = True
            return redirect(url_for('admin_login'))
        else:
            error = True
    return render_template_string(admin_login_template, error=error)

@app.route('/hakim-secure-command-room-999/action/<int:index>/<action_type>')
def admin_action(index, action_type):
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))
    
    if 0 <= index < len(students_database):
        if action_type == 'accept':
            students_database[index]['status'] = 'مقبول'
        elif action_type == 'reject':
            students_database[index]['status'] = 'مرفوض'
            
    return redirect(url_for('admin_login'))

@app.route('/hakim-secure-command-room-999/logout')
def admin_logout():
    session.pop('admin_logged', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
