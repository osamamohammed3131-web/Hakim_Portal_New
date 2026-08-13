from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>بوابة حكيم الجديدة</title>
    </head>
    <body>
        <h1>بوابة حكيم الجديدة</h1>
        <p>تم تشغيل النظام بنجاح.</p>
    </body>
    </html>
    """


@app.route("/health")
def health():
    return "OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
