from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "hakim_academic_2026_pro"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# قواعد البيانات المؤقتة
STUDENTS_DB = {}
UPLOADED_FILES = []
CURRENT_SERIAL_INDEX = 2000

# HTML الموحد (يمكن وضعه في ملفات منفصلة مستقبلاً)
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f4f7f6; font-family: 'Segoe UI', sans-serif; }
        .card { border: none; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .btn-primary { background: #0056b3; border: none; }
    </style>
</head>
<body class="p-4">
"""

@app.route("/")
def home():
    return render_template_string(BASE_TEMPLATE + """
    <div class="text-center mt-5">
        <h1>منصة حكيم الأكاديمية</h1>
        <div class="mt-4">
            <a href="/student" class="btn btn-primary btn-lg">بوابة الطالب</a>
            <a href="/admin" class="btn btn-secondary btn-lg">لوحة المشرف</a>
        </div>
    </div>
    </body></html>""")

@app.route("/student")
def student():
    return render_template_string(BASE_TEMPLATE + """
    <div class="container" id="app">
        <div id="login-box" class="card p-4 mx-auto" style="max-width:400px">
            <h3>تسجيل الدخول</h3>
            <input id="name" class="form-control my-2" placeholder="الاسم الكامل">
            <input id="phone" class="form-control my-2" placeholder="رقم الهاتف">
            <button class="btn btn-primary w-100" onclick="register()">دخول</button>
        </div>
        <div id="dashboard" class="d-none">
            <h2 id="welcome-msg"></h2>
            <div id="status-alert" class="alert alert-warning">حالتك: قيد المراجعة</div>
            <div id="content-area" class="d-none">
                <h4>الملفات والملازم المعتمدة</h4>
                <div id="files-list" class="list-group"></div>
            </div>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script>
        var socket = io(); var mySerial = "";
        function register() {
            socket.emit('reg', {name: document.getElementById('name').value, phone: document.getElementById('phone').value});
        }
        socket.on('reg_success', (data) => {
            mySerial = data.serial;
            document.getElementById('login-box').classList.add('d-none');
            document.getElementById('dashboard').classList.remove('d-none');
            document.getElementById('welcome-msg').innerText = "مرحباً " + data.name;
        });
        socket.on('status_change', (data) => {
            if(data.serial == mySerial && data.status == 'مقبول') {
                document.getElementById('status-alert').className = 'alert alert-success';
                document.getElementById('status-alert').innerText = 'تم قبولك في المنصة!';
                document.getElementById('content-area').classList.remove('d-none');
            }
        });
        socket.on('files_update', (files) => {
            let list = document.getElementById('files-list');
            list.innerHTML = files.map(f => `<a href="${f.link}" class="list-group-item">${f.title} (${f.cat})</a>`).join('');
        });
    </script>
    </body></html>""")

@app.route("/admin")
def admin():
    return render_template_string(BASE_TEMPLATE + """
    <div class="container">
        <h3>لوحة المشرف</h3>
        <div class="card p-3 my-3">
            <h5>رفع ملف جديد</h5>
            <input id="fTitle" class="form-control" placeholder="عنوان الملف">
            <select id="fCat" class="form-control my-2"><option>ملازم</option><option>تجميعات</option></select>
            <input id="fLink" class="form-control" placeholder="الرابط">
            <button class="btn btn-success mt-2" onclick="upload()">نشر للطلاب</button>
        </div>
        <table class="table">
            <thead><tr><th>الاسم</th><th>الحالة</th><th>التحكم</th></tr></thead>
            <tbody id="st-table"></tbody>
        </table>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script>
        var socket = io();
        function upload() {
            socket.emit('admin_upload', {title: document.getElementById('fTitle').value, cat: document.getElementById('fCat').value, link: document.getElementById('fLink').value});
        }
        function accept(serial) { socket.emit('accept_st', serial); }
        socket.on('st_list', (data) => {
            document.getElementById('st-table').innerHTML = data.map(s => `<tr><td>${s.name}</td><td>${s.status}</td><td><button class="btn btn-sm btn-info" onclick="accept('${s.serial}')">قبول</button></td></tr>`).join('');
        });
    </script>
    </body></html>""")

@socketio.on('reg')
def reg(data):
    global CURRENT_SERIAL_INDEX
    serial = f"HAKIM-{CURRENT_SERIAL_INDEX}"
    STUDENTS_DB[serial] = {'serial': serial, 'name': data['name'], 'status': 'قيد المراجعة'}
    CURRENT_SERIAL_INDEX += 1
    emit('reg_success', {'serial': serial, 'name': data['name']})
    socketio.emit('st_list', list(STUDENTS_DB.values()))

@socketio.on('accept_st')
def accept(serial):
    if serial in STUDENTS_DB:
        STUDENTS_DB[serial]['status'] = 'مقبول'
        socketio.emit('st_list', list(STUDENTS_DB.values()))
        socketio.emit('status_change', {'serial': serial, 'status': 'مقبول'})

@socketio.on('admin_upload')
def upload(data):
    UPLOADED_FILES.append(data)
    socketio.emit('files_update', UPLOADED_FILES)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
