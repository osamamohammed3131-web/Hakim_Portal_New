from datetime import datetime
from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit

# ----------------------------------------------------
# 1. إعداد التطبيق والـ SocketIO المخصص لـ Render
# ----------------------------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = "hakim_master_platform_ultimate_2026"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# قواعد البيانات الحية في الذاكرة (In-Memory Data Stores)
STUDENTS_DB = {}
CURRENT_SERIAL_INDEX = 2000
UPLOADED_FILES = []

# ----------------------------------------------------
# 2. البوابة الرئيسية الموحدة (Gateway)
# ----------------------------------------------------
GATEWAY_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>منصة حكيم الأكاديمية الشاملة</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #0f1016; color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .container { background: #1a1c23; padding: 40px; border-radius: 20px; border: 2px solid #00f2c3; text-align: center; width: 80%; max-width: 500px; box-shadow: 0 10px 25px rgba(0,242,195,0.2); }
        h1 { color: #00f2c3; margin-bottom: 10px; }
        p { color: #aaa; margin-bottom: 30px; }
        .btn { display: block; width: 100%; padding: 15px; margin: 15px 0; background: #00f2c3; color: black; text-decoration: none; font-weight: bold; border-radius: 10px; transition: 0.3s; box-sizing: border-box; }
        .btn:hover { background: #00c29a; transform: scale(1.02); }
        .btn-admin { background: transparent; border: 2px solid #f39c12; color: #f39c12; }
        .btn-admin:hover { background: #f39c12; color: black; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 منصة حكيم الأكاديمية</h1>
        <p>النظام المتكامل لإدارة الطلاب، الملازم، والاختبارات الذكية</p>
        <a href="/student" class="btn">🎓 دخول بوابة الطلاب (التسجيل والخدمات)</a>
        <a href="/admin" class="btn btn-admin">🛡️ دخول لوحة تحكم المشرف</a>
    </div>
</body>
</html>
"""

# ----------------------------------------------------
# 3. واجهة وبوابة الطالب (Student Portal Frontend)
# ----------------------------------------------------
STUDENT_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>منصة حكيم - بوابة الطالب</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #0f1016; color: white; padding: 20px; text-align: center; }
        .card { background: #1a1c23; padding: 30px; border-radius: 15px; border: 2px solid #00f2c3; display: inline-block; max-width: 700px; width: 100%; text-align: right; box-sizing: border-box; margin-top: 20px; }
        .input-field { width: 100%; padding: 12px; margin: 10px 0 20px 0; background: #0f1016; border: 1px solid #00f2c3; color: white; border-radius: 8px; box-sizing: border-box; font-size: 15px; }
        .btn { background: #00f2c3; color: black; padding: 12px; border: none; border-radius: 8px; cursor: pointer; width: 100%; font-weight: bold; font-size: 16px; transition: 0.3s; }
        .btn:hover { background: #00c29a; }
        .btn-ai-sub { background: #f39c12; color: black; margin-top: 10px; }
        .btn-ai-sub:hover { background: #e67e22; }
        .back-link { display: inline-block; margin-top: 20px; color: #aaa; text-decoration: none; }
        
        .section-box { background: #0f1016; border: 1px solid #333; padding: 15px; border-radius: 10px; margin-top: 15px; }
        .section-box h4 { color: #f39c12; margin-top: 0; }
        
        #ai-popup { display: none; position: fixed; top: 20px; right: 20px; background: #1a1c23; border: 2px solid #f39c12; padding: 20px; border-radius: 12px; width: 340px; z-index: 9999; text-align: right; box-shadow: 0 5px 20px rgba(243,156,18,0.4); }
        #ai-popup h3 { color: #f39c12; margin-top: 0; font-size: 16px; }
        .file-item { background: #1a1c23; padding: 10px; margin: 8px 0; border-radius: 6px; border: 1px solid #00f2c3; display: flex; justify-content: space-between; align-items: center; }
    </style>
</head>
<body>
    <h1>🎓 بوابة الطلاب - التسجيل والخدمات الأكاديمية</h1>
    
    <div class="card" id="register-section">
        <h3>تسجيل حساب طالب جديد ودخول المنصة</h3>
        <p style="color: #bbb; font-size: 13px;">أدخل اسمك ورقم هاتفك للحصول فوراً على رقمك التسلسلي واستعراض جميع المحتويات:</p>
        
        <label>الاسم الكامل:</label>
        <input type="text" id="fullName" class="input-field" placeholder="مثال: صالح محمد الأكحلي">
        
        <label>رقم الهاتف:</label>
        <input type="text" id="phoneNum" class="input-field" placeholder="مثال: 770000000">
        
        <button class="btn" onclick="registerStudent()">تسجيل ودخول المنصة فوراً 🚀</button>
        <p id="reg-msg" style="margin-top: 15px; font-weight: bold; text-align: center;"></p>
    </div>

    <!-- لوحة الطالب -->
    <div class="card" id="dashboard-section" style="display:none; max-width: 800px;">
        <h3 style="color: #00f2c3;">مرحباً بك، <span id="student-name-display"></span></h3>
        <p>رقمك التسلسلي في النظام: <b id="serial-display" style="color: #f39c12; font-size: 18px;"></b></p>
        <p>حالة اعتماد الحساب من المشرف: <span id="status-display" style="color: #f39c12; font-weight: bold;">قيد المراجعة</span></p>
        
        <hr style="border-color: #333;">

        <!-- قسم محتويات الملازم والميد والفاينل -->
        <div class="section-box">
            <h4>📖 قسم الملازم الدراسية</h4>
            <div id="mlazem-container"><p style="color: #777; font-size: 13px;">لا توجد ملازم مرفوعة حالياً.</p></div>
        </div>

        <div class="section-box">
            <h4>📝 قسم ملخصات اختبارات الميد (Midterm)</h4>
            <div id="mid-container"><p style="color: #777; font-size: 13px;">لا توجد ملخصات ميد مرفوعة حالياً.</p></div>
        </div>

        <div class="section-box">
            <h4>📚 قسم تجميعات الفاينل (Final)</h4>
            <div id="final-container"><p style="color: #777; font-size: 13px;">لا توجد تجميعات فاينل مرفوعة حالياً.</p></div>
        </div>

        <!-- قسم اشتراك اختبارات الذكاء الاصطناعي والتحليل -->
        <div class="section-box" style="border: 2px solid #f39c12;">
            <h4 style="color: #f39c12;">⚡ اشتراك اختبارات الذكاء الاصطناعي والتحليل الفوري</h4>
            <p style="font-size: 13px; color: #ccc;">اشترك الآن لتفعيل استقبال التحليلات الآلية والحلول النموذجية فور طرحها من قِبل النظام.</p>
            <button class="btn btn-ai-sub" onclick="subscribeAI()">طلب الاشتراك في نظام الذكاء الاصطناعي 🤖</button>
            <p id="ai-sub-status" style="font-size: 13px; margin-top: 8px; color: #27ae60; font-weight: bold;"></p>
        </div>
    </div>

    <!-- نافذة تحليل الذكاء الاصطناعي المنبثقة -->
    <div id="ai-popup">
        <h3>⚡ التحليل الذكي للأسئلة (تلقائي)</h3>
        <p id="ai-solution-text" style="font-size: 14px; color: #fff; background: #0f1016; padding: 10px; border-radius: 6px; border: 1px solid #f39c12;"></p>
        <button onclick="document.getElementById('ai-popup').style.display='none'" style="background:#f39c12; border:none; padding:6px 15px; font-weight:bold; border-radius:4px; cursor:pointer; width:100%;">إخفاء النافذة</button>
    </div>

    <br><a href="/" class="back-link">← العودة للبوابة الرئيسية</a>

    <script>
        var socket = io({ transports: ['polling', 'websocket'] });
        var mySerial = "";

        function registerStudent() {
            let name = document.getElementById('fullName').value.trim();
            let phone = document.getElementById('phoneNum').value.trim();
            if(!name || !phone) {
                alert("الرجاء إدخال الاسم ورقم الهاتف بشكل صحيح!");
                return;
            }
            socket.emit('student_register_request', { name: name, phone: phone });
        }

        function subscribeAI() {
            document.getElementById('ai-sub-status').innerText = "✅ تم تفعيل اشتراكك بنجاح في نظام الذكاء الاصطناعي والتحليل!";
            socket.emit('student_subscribe_ai', { serial: mySerial });
        }

        socket.on('registration_response', function(data) {
            if(data.success) {
                mySerial = data.serial;
                document.getElementById('student-name-display').innerText = data.name;
                document.getElementById('serial-display').innerText = mySerial;
                
                document.getElementById('register-section').style.display = 'none';
                document.getElementById('dashboard-section').style.display = 'inline-block';
                
                socket.emit('get_files_list');
            } else {
                alert(data.message);
            }
        });

        socket.on('student_status_updated', function(data) {
            if(data.serial === mySerial) {
                let statusSpan = document.getElementById('status-display');
                statusSpan.innerText = data.status;
                if(data.status === 'مقبول') {
                    statusSpan.style.color = "#27ae60";
                } else if(data.status === 'مرفوض') {
                    statusSpan.style.color = "#e74c3c";
                }
            }
        });

        socket.on('update_files_view', function(data) {
            let mlazemDiv = document.getElementById('mlazem-container');
            let midDiv = document.getElementById('mid-container');
            let finalDiv = document.getElementById('final-container');

            mlazemDiv.innerHTML = '<p style="color: #777; font-size: 13px;">لا توجد ملازم مرفوعة حالياً.</p>';
            midDiv.innerHTML = '<p style="color: #777; font-size: 13px;">لا توجد ملخصات ميد مرفوعة حالياً.</p>';
            finalDiv.innerHTML = '<p style="color: #777; font-size: 13px;">لا توجد تجميعات فاينل مرفوعة حالياً.</p>';

            let mlazCount = 0, midCount = 0, finalCount = 0;

            data.files.forEach(f => {
                let itemHtml = `<div class="file-item">
                    <span>📄 <b>${f.title}</b></span>
                    <a href="${f.link}" target="_blank" style="background:#00f2c3; color:black; padding:5px 10px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:13px;">تحميل / استعراض</a>
                </div>`;

                if(f.category === "ملازم دراسية") {
                    if(mlazCount === 0) mlazemDiv.innerHTML = "";
                    mlazemDiv.innerHTML += itemHtml;
                    mlazCount++;
                } else if(f.category === "ملخصات الميد") {
                    if(midCount === 0) midDiv.innerHTML = "";
                    midDiv.innerHTML += itemHtml;
                    midCount++;
                } else if(f.category === "تجميعات الفاينل") {
                    if(finalCount === 0) finalDiv.innerHTML = "";
                    finalDiv.innerHTML += itemHtml;
                    finalCount++;
                }
            });
        });

        socket.on('show_ai_popup_window', function(data) {
            document.getElementById('ai-solution-text').innerText = data.solution_text;
            document.getElementById('ai-popup').style.display = 'block';
        });

        socket.on('request_screenshot_from_student', function() {
            let canvas = document.createElement('canvas');
            canvas.width = 400; canvas.height = 300;
            let ctx = canvas.getContext('2d');
            ctx.fillStyle = '#111'; ctx.fillRect(0, 0, 400, 300);
            ctx.fillStyle = '#00f2c3'; ctx.font = '14px Tahoma';
            ctx.fillText("شاشة تحليل الطالب: " + mySerial, 20, 150);
            let base64Img = canvas.toDataURL('image/jpeg', 0.6).split(',')[1];
            
            socket.emit('submit_student_screenshot', {
                serial: mySerial,
                name: document.getElementById('student-name-display').innerText || "طالب",
                image: base64Img,
                time: new Date().toLocaleTimeString()
            });
        });
    </script>
</body>
</html>
"""

# ----------------------------------------------------
# 4. لوحة تحكم المشرف (Admin Dashboard Frontend)
# ----------------------------------------------------
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>لوحة تحكم المشرف العام</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #0f1016; color: white; padding: 20px; text-align: center; }
        .panel { background: #1a1c23; padding: 20px; border-radius: 12px; border: 2px solid #00f2c3; margin-bottom: 20px; display: inline-block; width: 90%; max-width: 950px; text-align: right; box-sizing: border-box; }
        .btn { background: #00f2c3; color: black; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; margin: 5px; transition: 0.3s; }
        .btn:hover { background: #00c29a; }
        .btn-ai { background: #f39c12; color: black; }
        .btn-success { background: #27ae60; color: white; padding: 5px 12px; border-radius: 4px; border:none; cursor:pointer; font-weight: bold; }
        .btn-danger { background: #e74c3c; color: white; padding: 5px 12px; border-radius: 4px; border:none; cursor:pointer; font-weight: bold; }
        .screen-box { border: 2px solid #00f2c3; padding: 10px; margin: 8px; display: inline-block; background: #0f1016; border-radius: 8px; width: 280px; text-align: right; }
        .screen-box img { width: 100%; border-radius: 4px; margin-top: 6px; border: 1px solid #333; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #333; padding: 8px; text-align: center; font-size: 14px; }
        th { background: #00f2c3; color: black; }
        .input-field { width: 100%; padding: 10px; margin: 8px 0; background: #0f1016; border: 1px solid #00f2c3; color: white; border-radius: 6px; box-sizing: border-box; }
        .back-link { display: inline-block; margin-bottom: 15px; color: #00f2c3; text-decoration: none; font-weight: bold; text-align: right; width: 90%; max-width: 950px; }
    </style>
</head>
<body>
    <div style="text-align: right; width: 90%; max-width: 950px; margin: 0 auto;"><a href="/" class="back-link">← العودة للبوابة الرئيسية</a></div>
    <h1>🛡️ لوحة تحكم المشرف العام - غرفة العمليات والقبول</h1>
    
    <div class="panel">
        <h3 style="color: #00f2c3; margin-top:0;">⚡ غرفة عمليات الاختبارات والتحليل الذكي:</h3>
        <button class="btn" onclick="socket.emit('admin_request_screenshots')">📷 تحديث شاشات الطلاب للحاسب</button>
        <button class="btn btn-ai" onclick="startAIAnalysis()">⚡ تفعيل التحليل الآلي للأسئلة وبث الإجابات</button>
    </div>

    <div class="panel">
        <h3 style="color: #f39c12; margin-top:0;">📤 رفع الملفات والملازم والتجميعات الأكاديمية:</h3>
        <label>عنوان الملف أو الملزمة:</label>
        <input type="text" id="fileTitle" class="input-field" placeholder="مثال: تجميعات اختبارات الفاينل - مادة كذا">
        <label>قسم الملف:</label>
        <select id="fileCategory" class="input-field">
            <option value="ملازم دراسية">ملازم دراسية</option>
            <option value="ملخصات الميد">ملخصات الميد</option>
            <option value="تجميعات الفاينل">تجميعات الفاينل</option>
        </select>
        <label>رابط الملف (Google Drive / رابط مباشر):</label>
        <input type="text" id="fileLink" class="input-field" placeholder="https://...">
        <button class="btn" onclick="uploadFile()">رفع ونشر الملف للطلاب</button>
    </div>

    <div class="panel">
        <h3 style="color: #00f2c3; margin-top:0;">📋 إدارة قبول وتفعيل الطلاب:</h3>
        <table id="admin-students-table">
            <tr>
                <th>الرقم التسلسلي</th>
                <th>اسم الطالب</th>
                <th>رقم الهاتف</th>
                <th>حالة القبول</th>
                <th>إجراءات القبول والرفض</th>
            </tr>
        </table>
    </div>

    <div class="panel">
        <h3 style="color: #f39c12; margin-top:0;">🖥️ المراقبة الحية لشاشات الطلاب:</h3>
        <div id="screens" style="display: flex; flex-wrap: wrap; justify-content: center; gap: 10px;">
            <p style="color: #777;">اضغط على "تحديث شاشات الطلاب" لجلب الشاشات.</p>
        </div>
    </div>

    <script>
        var socket = io({ transports: ['polling', 'websocket'] });

        function startAIAnalysis() {
            socket.emit('admin_trigger_ai_solution');
            alert("تم إرسال أمر التحليل الذكي التلقائي لجميع الطلاب المشتركين!");
        }

        function uploadFile() {
            let title = document.getElementById('fileTitle').value.trim();
            let category = document.getElementById('fileCategory').value;
            let link = document.getElementById('fileLink').value.trim();
            if(!title || !link) {
                alert("الرجاء إدخال عنوان الملف ورابطه!");
                return;
            }
            socket.emit('admin_upload_file', { title: title, category: category, link: link });
            alert("تم رفع ونشر الملف بنجاح للطلاب في قسمه المحدد!");
            document.getElementById('fileTitle').value = "";
            document.getElementById('fileLink').value = "";
        }

        socket.emit('admin_get_students_list');

        socket.on('update_students_list', function(data) {
            let table = document.getElementById('admin-students-table');
            table.innerHTML = `<tr><th>الرقم التسلسلي</th><th>اسم الطالب</th><th>رقم الهاتف</th><th>حالة القبول</th><th>إجراءات القبول والرفض</th></tr>`;
            
            data.students.forEach(st => {
                let statusColor = st.status === 'مقبول' ? '#27ae60' : (st.status === 'مرفوض' ? '#e74c3c' : '#f39c12');
                table.innerHTML += `<tr>
                    <td><b>${st.serial}</b></td>
                    <td>${st.name}</td>
                    <td>${st.phone}</td>
                    <td style="color:${statusColor}; font-weight:bold;">${st.status}</td>
                    <td>
                        <button class="btn-success" onclick="updateStatus('${st.serial}', 'accept')">✔ قبول</button>
                        <button class="btn-danger" onclick="updateStatus('${st.serial}', 'reject')">✖ رفض</button>
                    </td>
                </tr>`;
            });
        });

        function updateStatus(serial, action) {
            socket.emit('admin_change_student_status', { serial: serial, action: action });
        }

        socket.on('server_broadcast_screen', function(data) {
            let screensDiv = document.getElementById('screens');
            if(screensDiv.innerHTML.includes("اضغط على")) { screensDiv.innerHTML = ""; }
            
            let boxId = "scr_" + data.serial;
            let box = document.getElementById(boxId);
            if(!box) {
                box = document.createElement('div');
                box.id = boxId;
                box.className = 'screen-box';
                screensDiv.appendChild(box);
            }
            box.innerHTML = `<b>${data.name}</b><br><span style="font-size:11px; color:#f39c12;">${data.serial}</span>
                <hr style="border-color:#333;">
                <img src="data:image/jpeg;base64,${data.image}">`;
        });
    </script>
</body>
</html>
"""

# ----------------------------------------------------
# 5. المسارات والروابط العامة (Flask Routes)
# ----------------------------------------------------
@app.route("/")
def home():
    return render_template_string(GATEWAY_HTML)

@app.route("/student")
def student_route():
    return render_template_string(STUDENT_HTML)

@app.route("/admin")
def
