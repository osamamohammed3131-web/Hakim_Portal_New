from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hakim_secure_platform_2026'
socketio = SocketIO(app, cors_allowed_origins="*")

# قاعدة بيانات مؤقتة للأرقام التسلسلية المعتمدة للطلاب (يمكنك إضافتها أو تعديلها)
VALID_SERIALS = {
    "HAKIM-2026-A1": {"name": "طالب مسار A", "track": "Plan A"},
    "HAKIM-2026-B2": {"name": "طالب مسار B", "track": "Plan B"},
    "HAKIM-2026-M3": {"name": "طالب إعلام", "track": "Media Law"}
}

# --- واجهة لوحة تحكم المشرف ---
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>منصة حكيم - لوحة تحكم المشرف العام</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #0f1016; color: white; text-align: center; padding: 20px; }
        h1 { color: #00f2c3; }
        .control-panel { background: #1a1c23; padding: 20px; border-radius: 12px; border: 1px solid #00f2c3; display: inline-block; margin-bottom: 20px; }
        .btn { background-color: #00f2c3; color: black; padding: 12px 25px; font-size: 16px; font-weight: bold; border: none; cursor: pointer; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,242,195,0.3); transition: 0.3s; }
        .btn:hover { background-color: #00c29a; transform: scale(1.05); }
        #screens { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin-top: 20px; }
        .screen-box { border: 2px solid #00f2c3; padding: 15px; border-radius: 10px; background: #1a1c23; width: 420px; text-align: right; }
        .screen-box img { width: 100%; border-radius: 5px; border: 1px solid #333; margin-top: 10px; }
        .badge { background: #f39c12; color: black; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    </style>
</head>
<body>
    <h1>🛡️ منصة حكيم الأكاديمية - غرفة العمليات والتحليل</h1>
    
    <div class="control-panel">
        <p>حالة الاتصال بالسيرفر: <span id="status" style="color: yellow; font-weight:bold;">جاري الاتصال...</span></p>
        <button class="btn" onclick="triggerGlobalCapture()">🚀 بدء اختبار / التقاط شاشات لجميع الطلاب</button>
    </div>

    <div id="screens">
        <!-- ستظهر شاشات الطلاب المباشرة هنا -->
    </div>

    <script>
        var socket = io();

        socket.on('connect', function() {
            document.getElementById('status').innerText = "متصل بنجاح وجاهز للإدارة";
            document.getElementById('status').style.color = "#27ae60";
        });

        function triggerGlobalCapture() {
            socket.emit('admin_trigger_all');
            let btn = document.querySelector('.btn');
            btn.innerText = "⏳ يتم إرسال أمر الالتقاط للطلاب...";
            setTimeout(() => btn.innerText = "🚀 بدء اختبار / التقاط شاشات لجميع الطلاب", 2000);
        }

        socket.on('server_broadcast_screen', function(data) {
            var screensDiv = document.getElementById('screens');
            
            // التحقق إذا كان صندوق الطالب موجود مسبقاً لتحديثه أو إنشاء صندوق جديد
            var boxId = "student_" + data.serial.replace(/[^a-zA-Z0-9]/g, "_");
            var box = document.getElementById(boxId);
            
            if (!box) {
                box = document.createElement('div');
                box.id = boxId;
                box.className = 'screen-box';
                screensDiv.appendChild(box);
            }
            
            box.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <b>الطالب: ${data.name}</b>
                    <span class="badge">${data.track}</span>
                </div>
                <hr style="border-color: #333;">
                <div style="font-size: 12px; color: #aaa;">الرقم التسلسلي: ${data.serial}</div>
                <div style="font-size: 12px; color: #f39c12;">وقت التحديث: ${data.time}</div>
                <img src="data:image/jpeg;base64,${data.image}">
            `;
        });
    </script>
</body>
</html>
"""

@app.route('/admin')
def admin_route():
    return render_template_string(ADMIN_HTML)

@socketio.on('connect')
def handle_connect():
    print("اتصال جديد بالمنصة السحابية")

# التحقق من مفتاح أو رقم تسلسلي للطالب
@socketio.on('verify_student_serial')
def verify_serial(data):
    serial = data.get('serial')
    if serial in VALID_SERIALS:
        student_info = VALID_SERIALS[serial]
        emit('serial_verified_success', {
            'status': 'allowed',
            'name': student_info['name'],
            'track': student_info['track']
        })
        print(f"تم تفعيل طالب بنجاح: {student_info['name']} - المسار: {student_info['track']}")
    else:
        emit('serial_verified_fail', {'status': 'rejected', 'message': 'الرقم التسلسلي غير صحيح أو منتهي الصلاحية'})

# المشرف يعطي أمر الفحص الشامل
@socketio.on('admin_trigger_all')
def admin_trigger_all():
    print("المشرف طلب التقاط الشاشة لكل الطلاب المتصلين")
    emit('request_screenshot_from_student', broadcast=True)

# استقبال لقطة الشاشة من الطالب وإرسالها للمشرف
@socketio.on('submit_student_screenshot')
def receive_screenshot(data):
    socketio.emit('server_broadcast_screen', data)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=10000, allow_unsafe_werkzeug=True)
