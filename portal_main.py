from datetime import datetime
from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "hakim_master_platform_2026"
socketio = SocketIO(app, cors_allowed_origins="*")

# قاعدة بيانات الطلاب والأرقام التسلسلية (من 2000 إلى 2100+ وما فوق)
# يمكنك تعديلها أو ربطها بقاعدة بيانات لاحقاً
ACTIVE_STUDENTS = {}


def generate_valid_serials():
  # توليد نطاق الأرقام التسلسلية تلقائياً من 2000 إلى 2200 كمرحلة أولية
  serials = {}
  for i in range(2000, 2201):
    serial_str = f"HAKIM-{i}"
    serials[serial_str] = {
        "name": f"الطالب رقم {i}",
        "track": "Plan A / Mid-Final",
    }
  return serials


VALID_SERIALS = generate_valid_serials()

# --- واجهة لوحة تحكم المشرف (Admin Dashboard) ---
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>منصة حكيم الأكاديمية - غرفة عمليات الاختبارات الذكية</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #0f1016; color: white; text-align: center; padding: 20px; }
        h1 { color: #00f2c3; }
        .control-panel { background: #1a1c23; padding: 20px; border-radius: 12px; border: 2px solid #00f2c3; display: inline-block; margin-bottom: 20px; max-width: 800px; }
        .btn { background-color: #00f2c3; color: black; padding: 12px 25px; font-size: 16px; font-weight: bold; border: none; cursor: pointer; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,242,195,0.3); transition: 0.3s; margin: 5px; }
        .btn:hover { background-color: #00c29a; transform: scale(1.05); }
        .btn-ai { background-color: #f39c12; color: black; }
        .btn-ai:hover { background-color: #d68910; }
        #screens { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin-top: 20px; }
        .screen-box { border: 2px solid #00f2c3; padding: 15px; border-radius: 10px; background: #1a1c23; width: 380px; text-align: right; }
        .screen-box img { width: 100%; border-radius: 5px; border: 1px solid #333; margin-top: 10px; }
        .badge { background: #9b59b6; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    </style>
</head>
<body>
    <h1>🛡️ منصة حكيم - لوحة تحكم اختبارات الميد والفاينل (الذكاء الاصطناعي)</h1>
    
    <div class="control-panel">
        <p>حالة النظام السحابي: <span id="status" style="color: yellow; font-weight:bold;">جاري الاتصال...</span> | الطلاب المتصلون: <span id="count" style="color: #00f2c3; font-weight:bold;">0</span></p>
        <button class="btn" onclick="triggerGlobalCapture()">📷 تحديث وعرض شاشات الطلاب</button>
        <button class="btn btn-ai" onclick="triggerAIAnalysis()">⚡ إرسال أمر الحل الذكي والتحليل للجميع</button>
    </div>

    <div id="screens">
        <!-- ستظهر شاشات الطلاب هنا مباشرة -->
    </div>

    <script>
        var socket = io();

        socket.on('connect', function() {
            document.getElementById('status').innerText = "متصل بنجاح وجاهز للإدارة";
            document.getElementById('status').style.color = "#27ae60";
        });

        function triggerGlobalCapture() {
            socket.emit('admin_request_screenshots');
        }

        function triggerAIAnalysis() {
            let aiAnswer = prompt("أدخل نص الإجابة الذكية النموذجية التي ستظهر في نافذة الطالب المنبثقة:");
            if (aiAnswer) {
                socket.emit('admin_trigger_ai_solution', { solution_text: aiAnswer });
                alert("تم إرسال أمر الحل الذكي والنافذة المنبثقة لجميع الطلاب بنجاح!");
            }
        }

        socket.on('server_broadcast_screen', function(data) {
            var screensDiv = document.getElementById('screens');
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
                    <b>${data.name}</b>
                    <span class="badge">${data.serial}</span>
                </div>
                <hr style="border-color: #333;">
                <div style="font-size: 12px; color: #f39c12;">وقت التحديث: ${data.time}</div>
                <img src="data:image/jpeg;base64,${data.image}">
            `;
        });
    </script>
</body>
</html>
"""


# --- تم إضافة المسار الرئيسي لكي لا يظهر خطأ 404 عند فتح الرابط ---
@app.route("/")
def home():
  return """
    <div style="font-family: Tahoma; background: #0f1016; color: white; height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
        <h1 style="color: #00f2c3;">🚀 منصة حكيم الأكاديمية تعمل بنجاح</h1>
        <p>السيستم متصل وجاهز لاستقبال الطلاب والمشرفين.</p>
        <a href="/admin" style="background: #00f2c3; color: black; padding: 12px 25px; text-decoration: none; font-weight: bold; border-radius: 8px; margin-top: 15px;">دخول لوحة تحكم المشرف (Admin)</a>
    </div>
    """


@app.route("/admin")
def admin_route():
  return render_template_string(ADMIN_HTML)


@socketio.on("connect")
def handle_connect():
  print("اتصال جديد بالمنصة السحابية")


# التحقق من الرقم التسلسلي للطالب (من النطاق المخصص 2000 فما فوق)
@socketio.on("verify_student_serial")
def verify_serial(data):
  serial = data.get("serial", "").strip()
  if serial in VALID_SERIALS:
    student_info = VALID_SERIALS[serial]
    ACTIVE_STUDENTS[request.sid] = {
        "serial": serial,
        "name": student_info["name"],
    }
    emit(
        "serial_verified_success",
        {
            "status": "allowed",
            "name": student_info["name"],
            "track": student_info["track"],
        },
    )
    print(f"تم تفعيل الطالب بنجاح برقم تسلسلي: {serial}")
  else:
    emit(
        "serial_verified_fail",
        {
            "status": "rejected",
            "message": "الرقم التسلسلي غير صحيح أو غير مفعل في النظام!",
        },
    )


@socketio.on("admin_request_screenshots")
def admin_request_screenshots():
  emit("request_screenshot_from_student", broadcast=True)


@socketio.on("admin_trigger_ai_solution")
def admin_trigger_ai_solution(data):
  # بث أمر إظهار النافذة المنبثقة للحل الذكي لجميع الطلاب المتصلين
  emit("show_ai_popup_window", data, broadcast=True)


@socketio.on("submit_student_screenshot")
def receive_screenshot(data):
  socketio.emit("server_broadcast_screen", data)


if __name__ == "__main__":
  socketio.run(app, host="0.0.0.0", port=10000, allow_unsafe_werkzeug=True)
