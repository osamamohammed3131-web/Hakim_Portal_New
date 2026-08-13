from functools import wraps

from flask import Blueprint, request, jsonify, session
from models import User
from extensions import db


auth = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


# =========================================================
# تسجيل حساب طالب جديد
# =========================================================

@auth.post("/register")
def register():

    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({
            "error": "اسم المستخدم والبريد وكلمة المرور مطلوبة"
        }), 400

    if User.query.filter_by(username=username).first():
        return jsonify({
            "error": "اسم المستخدم مستخدم مسبقًا"
        }), 409

    if User.query.filter_by(email=email).first():
        return jsonify({
            "error": "البريد الإلكتروني مستخدم مسبقًا"
        }), 409

    # =====================================================
    # الطالب الجديد يكون قيد المراجعة
    # =====================================================

    user = User(
        username=username,
        email=email,
        role="student",
        is_active=False
    )

    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "تم إنشاء الحساب، وهو الآن قيد المراجعة من المشرف",
        "status": "pending",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active
        }
    }), 201


# =========================================================
# تسجيل الدخول
# =========================================================

@auth.post("/login")
def login():

    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    password = data.get("password", "")

    user = User.query.filter_by(
        username=username
    ).first()

    # الحساب غير موجود
    if not user:
        return jsonify({
            "error": "بيانات تسجيل الدخول غير صحيحة"
        }), 401

    # =====================================================
    # الطالب موجود ولكن لم تتم الموافقة عليه
    # =====================================================

    if user.role == "student" and not user.is_active:
        return jsonify({
            "error": "حسابك قيد المراجعة من المشرف، وسيتم تفعيل الحساب بعد الموافقة"
        }), 403

    # الحساب غير نشط
    if not user.is_active:
        return jsonify({
            "error": "الحساب غير نشط"
        }), 401

    # كلمة المرور غير صحيحة
    if not user.check_password(password):
        return jsonify({
            "error": "بيانات تسجيل الدخول غير صحيحة"
        }), 401

    # =====================================================
    # إنشاء الجلسة
    # =====================================================

    session["user_id"] = user.id
    session["role"] = user.role

    # =====================================================
    # تحديد الصفحة حسب نوع الحساب
    # =====================================================

    if user.role in ("admin", "superadmin"):
        redirect_to = "/admin"
    else:
        redirect_to = "/student"

    return jsonify({
        "message": "تم تسجيل الدخول بنجاح",
        "redirect": redirect_to,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    })


# =========================================================
# تسجيل الخروج
# =========================================================

@auth.post("/logout")
def logout():

    session.clear()

    return jsonify({
        "message": "تم تسجيل الخروج بنجاح"
    })


# =========================================================
# المستخدم الحالي
# =========================================================

@auth.get("/me")
def current_user():

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "authenticated": False
        }), 401

    user = db.session.get(User, user_id)

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


# =========================================================
# حماية الصفحات التي تتطلب تسجيل الدخول
# =========================================================

def login_required(view):

    @wraps(view)
    def wrapped_view(*args, **kwargs):

        user_id = session.get("user_id")

        if not user_id:
            return jsonify({
                "error": "يجب تسجيل الدخول أولًا"
            }), 401

        user = db.session.get(User, user_id)

        if not user or not user.is_active:

            session.clear()

            return jsonify({
                "error": "الحساب غير صالح أو لم تتم الموافقة عليه"
            }), 401

        return view(*args, **kwargs)

    return wrapped_view


# =========================================================
# حماية الصفحات حسب الصلاحية
# =========================================================

def role_required(*allowed_roles):

    def decorator(view):

        @wraps(view)
        def wrapped_view(*args, **kwargs):

            user_id = session.get("user_id")

            if not user_id:
                return jsonify({
                    "error": "يجب تسجيل الدخول أولًا"
                }), 401

            user = db.session.get(User, user_id)

            if not user or not user.is_active:

                session.clear()

                return jsonify({
                    "error": "الحساب غير صالح أو لم تتم الموافقة عليه"
                }), 401

            if user.role not in allowed_roles:

                return jsonify({
                    "error": "ليس لديك صلاحية للوصول إلى هذه الصفحة"
                }), 403

            return view(*args, **kwargs)

        return wrapped_view

    return decorator
