from flask import Flask, render_template_string

app = Flask(__name__)

# الصفحة الرئيسية للمنصة
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>بوابة حكيم</title>
        <style>
            body { font-family: Tahoma, sans-serif; background: #f4f6f9; text-align: center; padding-top: 50px; }
            .card { background: white; max-width: 500px; margin: auto; padding: 30px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; }
            p { color: #555; font-size: 18px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>مرحباً بك في بوابة حكيم</h1>
            <p>النظام يعمل بنجاح تام وجاهز لخدمة الطلاب.</p>
        </div>
    </body>
    </html>
    """

# لوحة تحكم المشرف (الرابط السري)
@app.route('/hakim-secure-command-room-999')
def admin_command_room():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>غرفة قيادة المشرف - بوابة حكيم</title>
        <style>
            body { font-family: Tahoma, sans-serif; background: #1e1e2f; color: #fff; text-align: center; padding-top: 50px; }
            .admin-container { background: #27293d; max-width: 600px; margin: auto; padding: 40px; border-radius: 12px; box-shadow: 0 8px 20px rgba(0,0,0,0.5); border: 2px solid #e14eca; }
            h1 { color: #e14eca; }
            p { font-size: 18px; color: #d0d0d0; }
            .btn { display: inline-block; margin-top: 20px; padding: 10px 20px; background: #00f2c3; color: #1e1e2f; text-decoration: none; font-weight: bold; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="admin-container">
            <h1>🛡️ غرفة قيادة المشرف - حكيم</h1>
            <p>أهلاً بك يا حكيم، أنت الآن داخل لوحة التحكم والتحكم الكامل بالمنصة.</p>
            <hr style="border: 0; border-top: 1px solid #444; margin: 20px 0;">
            <p>جميع صلاحيات الإدارة والتحكم مفعلة هنا.</p>
            <a href="/" class="btn">العودة للرئيسية</a>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
