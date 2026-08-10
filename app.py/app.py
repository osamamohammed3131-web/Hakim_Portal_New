import os
from flask import Flask, request, redirect, url_for

app = Flask(__name__)

# إعداد مجلد حفظ الملفات والتجميعات
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# قواعد البيانات الداخلية
students_database = {}  
files_database = []     
custom_buttons = []     
current_serial_counter = 2001  

# ==========================================
# 1. رابط الطالب (بوابة الطلاب العامة فقط)
# ==========================================
@app.route('/')
def student_portal():
    extra_links = "".join([f"<p><a href='#'>{btn}</a></p>" for btn in custom_buttons])
    
    return f"""
    <div style="font-family: Tahoma; text-align: center; margin-top: 50px; direction: rtl;">
        <h2>بوابة الطالب - منصة حكيم</h2>
        <p>قم بتسجيل بياناتك للحصول على رقمك التسلسلي:</p>
        <form action="/register" method="POST">
            <input type="text" name="student_name" placeholder="اسم الطالب الكامل" style="padding: 10px; width: 250px;" required><br><br>
            <button type="submit" style="padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; border-radius: 5px;">إرسال طلب الانضمام</button>
        </form>
        <div style="margin-top: 20px;">
            {extra_links}
        </div>
    </div>
    """

@app.route('/register', methods=['POST'])
def register_student():
    global current_serial_counter
    name = request.form.get('student_name')
    serial = current_serial_counter
    students_database[serial] = {"name": name, "status": "قيد الانتظار"}
    current_serial_counter += 1
    
    return f"""
    <div style="font-family: Tahoma; text-align: center; margin-top: 50px; direction: rtl;">
        <h3>تم إرسال طلبك بنجاح يا {name}!</h3>
        <p>رقمك التسلسلي المعزول هو: <b style="color: red; font-size: 22px;">{serial}</b></p>
        <p>بانتظار موافقة المشرف لتفعيل حسابك.</p>
        <a href="/">العودة للرئيسية</a>
    </div>
    """

# ==========================================
# 2. رابط لوحة المشرف (غرفة القيادة السرية والمستقلة تماماً)
# ==========================================
@app.route('/hakim-secure-command-room-999')
def admin_panel():
    students_list = ""
    for serial, data in students_database.items():
        students_list += f"""
        <tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 10px; text-align: center;">{serial}</td>
            <td style="padding: 10px; text-align: center;">{data['name']}</td>
            <td style="padding: 10px; text-align: center;">{data['status']}</td>
            <td style="padding: 10px; text-align: center;">
                <a href="/admin/approve/{serial}" style="background: green; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">قبول</a>
                <a href="/admin/reject/{serial}" style="background: red; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">رفض</a>
            </td>
        </tr>
        """
    
    files_list = "".join([f"<li>📄 {f}</li>" for f in files_database])
    
    return f"""
    <div style="font-family: Tahoma; direction: rtl; padding: 20px; background: #f4f6f9; min-height: 100vh;">
        <div style="background: #333; color: white; padding: 15px; border-radius: 5px;">
            <h2>غرفة القيادة والسيطرة - لوحة تحكم حكيم الأمنية 🛡️</h2>
            <p>رابط منفصل سري وخاص بك وحدك لإدارة المنصة بالكامل.</p>
        </div>

        <div style="background: white; padding: 15px; margin-top: 20px; border-radius: 5px; box-shadow: 0 0 5px rgba(0,0,0,0.1);">
            <h3>إضافة عنصر أو زر جديد لواجهة الطالب</h3>
            <form action="/admin/add-element" method="POST">
                <input type="text" name="element_name" placeholder="اسم الزر أو النافذة الجديدة" style="padding: 8px; width: 250px;" required>
                <button type="submit" style="background: #17a2b8; color: white; padding: 8px 15px; border: none; cursor: pointer; border-radius: 3px;">إضافة للمنصة</button>
            </form>
        </div>

        <div style="background: white; padding: 15px; margin-top: 20px; border-radius: 5px; box-shadow: 0 0 5px rgba(0,0,0,0.1);">
            <h3>مستودع الذكاء الاصطناعي (رفع الكتب والتجميعات)</h3>
            <form action="/admin/upload" method="POST" enctype="multipart/form-data">
                <input type="file" name="study_file" required>
                <button type="submit" style="background: #28a745; color: white; padding: 8px 15px; border: none; cursor: pointer; border-radius: 3px;">رفع الملف وتجهيزه</button>
            </form>
            <ul style="margin-top: 10px;">
                {files_list if files_list else "<li>لا توجد ملفات مرفوعة حتى الآن.</li>"}
            </ul>
        </div>

        <div style="background: white; padding: 15px; margin-top: 20px; border-radius: 5px; box-shadow: 0 0 5px rgba(0,0,0,0.1);">
            <h3>إدارة الطلاب المسجلين (تبدأ من الرقم 2001)</h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                <tr style="background: #007bff; color: white;">
                    <th style="padding: 10px;">الرقم التسلسلي</th>
                    <th style="padding: 10px;">اسم الطالب</th>
                    <th style="padding: 10px;">الحالة</th>
                    <th style="padding: 10px;">الإجراءات</th>
                </tr>
                {students_list if students_list else "<tr><td colspan='4' style='text-align: center; padding: 20px;'>لا توجد طلبات تسجيل حتى الآن.</td></tr>"}
            </table>
        </div>
    </div>
    """

@app.route('/admin/add-element', methods=['POST'])
def add_element():
    name = request.form.get('element_name')
    if name:
        custom_buttons.append(name)
    return redirect('/hakim-secure-command-room-999')

@app.route('/admin/upload', methods=['POST'])
def upload_file():
    if 'study_file' in request.files:
        file = request.files['study_file']
        if file.filename != '':
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            files_database.append(file.filename)
    return redirect('/hakim-secure-command-room-999')

@app.route('/admin/approve/<int:serial>')
def approve_student(serial):
    if serial in students_database:
        students_database[serial]["status"] = "مقبول ومفعل ✅"
    return redirect('/hakim-secure-command-room-999')

@app.route('/admin/reject/<int:serial>')
def reject_student(serial):
    if serial in students_database:
        students_database[serial]["status"] = "مرفوض ❌"
    return redirect('/hakim-secure-command-room-999')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
