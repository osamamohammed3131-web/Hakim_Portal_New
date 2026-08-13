from flask import Blueprint, request, jsonify, session
from models import User

auth = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth.post("/register")
def register():
    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    role = data.get("role", "student")

    if not username or not email or not password:
        return jsonify({
            "error": "اسم المستخدم والبريد وكلمة المرور مطلوبة"
        }), 400

    if role not in {"student", "admin", "superadmin"}:
        role = "student"

    if User.query.filter_by(username=username).first():
        return jsonify({
            "error": "اسم المستخدم مستخدم مسبقًا"
        }), 409

    if User.query.filter_by(email=email).first():
        return jsonify({
            "error": "البريد الإلكتروني مستخدم مسبقًا"
        }), 409

    user = User(
        username=username,
        email=email,
        role=role
    )

    user.set_password(password)

    from extensions import db
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "تم إنشاء الحساب بنجاح",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }), 201


@auth.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    password = data.get("password", "")

    user = User.query.filter_by(username=username).first()

    if not user or not user.is_active:
        return jsonify({
            "error": "بيانات تسجيل الدخول غير صحيحة"
        }), 401

    if not user.check_password(password):
        return jsonify({
            "error": "بيانات تسجيل الدخول غير صحيحة"
        }), 401

    session["user_id"] = user.id
    session["role"] = user.role

    return jsonify({
        "message": "تم تسجيل الدخول بنجاح",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    })


@auth.post("/logout")
def logout():
    session.clear()

    return jsonify({
        "message": "تم تسجيل الخروج بنجاح"
    })


@auth.get("/me")
def current_user():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "authenticated": False
        }), 401

    user = User.query.get(user_id)

    if not user or not user.is_active:
        session.clear()

        return jsonify({
            "authenticated": False
        }), 401

    return jsonify({
        "authenticated": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    })
