from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "بوابة حكيم الجديدة تعمل بنجاح"

@app.route("/health")
def health():
    return "OK"
