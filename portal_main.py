from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "hakim_master_platform_ultimate_2026"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

STUDENTS_DB = {}
CURRENT_SERIAL_INDEX = 2000
UPLOADED_FILES = []

GATEWAY_HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>منصة حكيم الأكاديمية</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #0f1016; color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .container { background: #1a1c23; padding: 40px; border-radius: 20px; border: 2px solid #00f2c3; text-align: center; width: 80%; max-width: 500px; }
        h1 { color: #00f2c3; }
        .btn { display: block; width: 100%; padding: 15px; margin: 15px 0; background: #00f2c3; color: black; text-decoration: none; font-weight: bold; border-radius: 10px; box-sizing: border-box; }
        .btn-admin { background: transparent; border: 2px solid #f39c12; color: #f39c12; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 منصة حكيم الأكاديمية</h1>
        <p>النظام المتكامل لإدارة الطلاب والمحتوى</p>
        <a href="/student" class="btn">🎓 دخول بوابة الطلاب</a>
        <a href="/admin" class="btn btn-admin">🛡️ لوحة تحكم المشرف</a>
    </div>
</body>
</html>"""

STUDENT_HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>بوابة الطالب</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #0f1016; color: white; padding: 20px; text-align: center; }
        .card { background: #1a1c23; padding: 30px; border-radius: 15px; border: 2px solid #00f2c3; display: inline-block; max-width: 700px; width: 100%; text-align: right; box-sizing: border-box; }
        .input-field { width: 100%; padding: 12px; margin: 10px 0; background: #0f1016; border: 1px solid #00f2c3; color: white; border-radius: 8px; box-sizing: border-box; }
        .btn { background: #00f2c3; color: black; padding: 12px; border: none; border-radius: 8px; cursor: pointer; width: 100%; font-weight: bold; }
        .file-item { background: #1a1c23; padding: 10px; margin: 8px 0; border-radius: 6px; border: 1px solid #00f2c3; display: flex; justify-content: space-between; align-items: center; }
    </style>
</head>
<body>
    <h1>🎓 بوابة الطلاب</h1>
    <div class="card" id="register-section">
        <h3>تسجيل حساب جديد</h3>
        <label>الاسم الكامل:</label>
        <input type="text" id="fullName" class="input-field" placeholder="اسمك الثلاثي">
        <label>رقم الهاتف:</label>
        <input type="text" id="phoneNum" class="input-field" placeholder="77xxxxxxx">
        <button class="btn" onclick="registerStudent()">تسجيل ودخول 🚀</button>
    </div>
    <div class="card" id="dashboard-section" style="display:none;">
        <h3>مرحباً، <span id="student-name-display"></span></h3>
        <p>الرقم التسلسلي: <b id="serial-display" style="color: #f39c12;"></b></p>
        <p>الحالة: <span id="status-display" style="color: #f39c12;">قيد المراجعة</span></p>
        <hr style="border-color: #333;">
        <h4>📖 الملازم والتجميعات</h4>
        <div id="files-container"><p style="color: #777;">لا توجد ملفات مرفوعة حالياً.</p></div>
    </div>
    <script>
        var socket = io();
        var mySerial = "";
        function registerStudent() {
            let name = document.getElementById('fullName').value.trim();
            let phone = document.getElementById('phoneNum').value.trim();
            if(!name || !phone) { alert("الرجاء إكمال البيانات"); return; }
            socket.emit('student_register_request', { name: name, phone: phone });
        }
        socket.on('registration_response', function(data) {
            if(data.success) {
                mySerial = data.serial;
                document.getElementById('student-name-display').innerText = data.name;
                document.getElementById('serial-display').innerText = mySerial;
                document.getElementById('register-section').style.display = 'none';
                document.getElementById('dashboard-section').style.display = 'inline-block';
                socket.emit('get_files_list');
            } else { alert(data.message); }
        });
        socket.on('student_status_updated', function(data) {
            if(data.serial === mySerial) {
                document.getElementById('status-display').innerText = data.status;
            }
        });
        socket.on('update_files_view', function(data) {
            let container = document.getElementById('files-container');
            if(data.files.length === 0) { container.innerHTML = '<p style="color: #777;">لا توجد ملفات مرفوعة حالياً.</p>'; return; }
            container.innerHTML = "";
            data.files.forEach(function(f) {
                container.innerHTML += '<div class="file-item"><span><b>' + f.title + '</b> (' + f.category + ')</span><a href="' + f.link + '" target="_blank" style="background:#00f2c3; color:black; padding:5px 10px; border-radius:4px; text-decoration:none; font-weight:bold;">تحميل</a></div>';
            });
        });
        socket.on('request_screenshot_from_student', function() {
            let canvas = document.createElement('canvas');
            canvas.width = 400; canvas.height = 300;
            let ctx = canvas.getContext('2d');
            ctx.fillStyle = '#111'; ctx.fillRect(0, 0, 400, 300);
            ctx.fillStyle = '#00f2c3'; ctx.fillText("شاشة الطالب: " + mySerial, 50, 150);
            let base64Img = canvas.toDataURL('image/jpeg', 0.6).split(',')[1];
            socket.emit('submit_student_screenshot', { serial: mySerial, name: document.getElementById('student-name-display').innerText, image: base64Img });
        });
    </script>
</body>
</html>"""

ADMIN_HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>لوحة التحكم</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #0f1016; color: white; padding: 20px; text-align: center; }
        .panel { background: #1a1c23; padding: 20px; border-radius: 12px; border: 2px solid #00f2c3; margin-bottom: 20px; display: inline-block; width: 90%; max-width: 900px; text-align: right; box-sizing: border-box; }
        .btn { background: #00f2c3; color: black; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #333; padding: 8px; text-align: center; }
        th { background: #00f2c3; color: black; }
        .input-field { width: 100%; padding: 10px; margin: 8px 0; background: #0f1016; border: 1px solid #00f2c3; color: white; border-radius: 6px; box-sizing: border-box; }
    </style>
</head>
<body>
    <h1>🛡️ لوحة تحكم المشرف العام</h1>
    <div class="panel">
        <h3>📤 رفع ملف أو ملزمة</h3>
        <input type="text" id="fileTitle" class="input-field" placeholder="عنوان الملف">
        <select id="fileCategory" class="input-field">
            <option value="ملازم دراسية">ملازم دراسية</option>
            <option value="تجميعات الفاينل">تجميعات الفاينل</option>
        </select>
        <input type="text" id="fileLink" class="input-field" placeholder="رابط الملف">
        <button class="btn" onclick="uploadFile()">نشر الملف</button>
    </div>
    <div class="panel">
        <h3>📋 إدارة الطلاب</h3>
        <table id="admin-students-table">
            <tr><th>الرقم</th><th>الاسم</th><th>الهاتف</th><th>الحالة</th><th>إجراء</th></tr>
        </table>
    </div>
    <script>
        var socket = io();
        function uploadFile() {
            let title = document.getElementById('fileTitle').value.trim();
            let category = document.getElementById('fileCategory').value;
            let link = document.getElementById('fileLink').value.trim();
            if(!title || !link) { alert("أدخل العنوان والرابط"); return; }
            socket.emit('admin_upload_file', { title: title, category: category, link: link });
            alert("تم النشر بنجاح");
        }
        socket.emit('admin_get_students_list');
        socket.on('update_students_list', function(data) {
            let table = document.getElementById('admin-students-table');
            table.innerHTML = '<tr><th>الرقم</th><th>الاسم</th><th>الهاتف</th><th>الحالة</th><th>إجراء</th></tr>';
            data.students.forEach(function(st) {
                table.innerHTML += '<tr><td><b>' + st.serial + '</b></td><td>' + st.name + '</td><td>' + st.phone + '</td><td>' + st.status + '</td><td><button onclick="updateStatus(\'' + st.serial + '\', \'accept\')">✔</button> <button onclick="updateStatus(\'' + st.serial + '\', \'reject\')">✖</button></td></tr>';
            });
        });
        function updateStatus(serial, action) {
            socket.emit('admin_change_student_status', { serial: serial, action: action });
        }
    </script>
</body>
</html>"""

@app.route("/")
def home():
    return render_template_string(GATEWAY_HTML)

@app.route("/student")
def student_route():
    return render_template_string(STUDENT_HTML)

@app.route("/admin")
def admin_route():
    return render_template_string(ADMIN_HTML)

@socketio.on('student_register_request')
def handle_student_registration(data):
    global CURRENT_SERIAL_INDEX
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    if not name or not phone:
        emit('registration_response', {'success': False, 'message': 'الرجاء إدخال البيانات!'})
        return
    serial = f"HAKIM-{CURRENT_SERIAL_INDEX}"
    CURRENT_SERIAL_INDEX += 1
    STUDENTS_DB[serial] = {'serial': serial, 'name': name, 'phone': phone, 'status': 'قيد الانتظار'}
    emit('registration_response', {'success': True, 'serial': serial, 'name': name})
    socketio.emit('update_students_list', {'students': list(STUDENTS_DB.values())})

@socketio.on('admin_get_students_list')
def handle_get_students():
    emit('update_students_list', {'students': list(STUDENTS_DB.values())})

@socketio.on('admin_change_student_status')
def handle_status_change(data):
    serial = data.get('serial')
    action = data.get('action')
    if serial in STUDENTS_DB:
        STUDENTS_DB[serial]['status'] = 'مقبول' if action == 'accept' else 'مرفوض'
        socketio.emit('update_students_list', {'students': list(STUDENTS_DB.values())})
        socketio.emit('student_status_updated', {'serial': serial, 'status': STUDENTS_DB[serial]['status']})

@socketio.on('admin_upload_file')
def handle_file_upload(data):
    UPLOADED_FILES.append({'title': data.get('title'), 'category': data.get('category'), 'link': data.get('link')})
    socketio.emit('update_files_view', {'files': UPLOADED_FILES})

@socketio.on('get_files_list')
def handle_get_files():
    emit('update_files_view', {'files': UPLOADED_FILES})

@socketio.on('submit_student_screenshot')
def handle_student_screenshot(data):
    pass

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
