from flask import Blueprint, jsonify, request, session

from auth import login_required, role_required
from models import User
from extensions import db


dashboard = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/api/dashboard"
)


@dashboard.get("/student")
@login_required
def student_dashboard():

    user = User.query.get(session["user_id"])

    return jsonify({
        "dashboard": "student",
        "message": "مرحبًا بك في لوحة الطالب",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        },
        "sections": [
            "السنة التمهيدية",
            "خطة A",
            "خطة B",
            "الجدول الذكي",
            "المحاضرات",
            "بوابة الأنظمة",
            "المساعد الأكاديمي",
            "التدريب والتجارب",
            "التقدم والمتابعة"
        ]
    })


@dashboard.get("/admin")
@role_required("admin", "superadmin")
def admin_dashboard():

    user = User.query.get(session["user_id"])

    return jsonify({
        "dashboard": "admin",
        "message": "مرحبًا بك في لوحة المشرف",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        },
        "sections": [
            "الإحصائيات العامة",
            "إدارة الطلاب",
            "إدارة الخطط A/B",
            "إدارة المواد",
            "إدارة الكتب والملفات",
            "إدارة الجداول والمحاضرات",
            "مركز معرفة AI",
            "قاعدة معرفة الدعم",
            "بنك التدريب",
            "الأخبار والتحديثات",
            "الصلاحيات",
            "سجل العمليات",
            "الإعدادات"
        ]
    })


# =========================================================
# إدارة الطلاب
# =========================================================

@dashboard.get("/admin/students")
@role_required("admin", "superadmin")
def get_students():

    students = User.query.filter_by(role="student").order_by(
        User.id.desc()
    ).all()

    return jsonify({
        "students": [
            {
                "id": student.id,
                "username": student.username,
                "email": student.email,
                "role": student.role,
                "is_active": student.is_active
            }
            for student in students
        ]
    })


@dashboard.post("/admin/students")
@role_required("admin", "superadmin")
def create_student():

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

    student = User(
        username=username,
        email=email,
        role="student",
        is_active=True
    )

    student.set_password(password)

    db.session.add(student)
    db.session.commit()

    return jsonify({
        "message": "تم إنشاء حساب الطالب بنجاح",
        "student": {
            "id": student.id,
            "username": student.username,
            "email": student.email,
            "role": student.role,
            "is_active": student.is_active
        }
    }), 201


@dashboard.put("/admin/students/<int:student_id>")
@role_required("admin", "superadmin")
def update_student(student_id):

    student = User.query.filter_by(
        id=student_id,
        role="student"
    ).first()

    if not student:
        return jsonify({
            "error": "الطالب غير موجود"
        }), 404

    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not username or not email:
        return jsonify({
            "error": "اسم المستخدم والبريد الإلكتروني مطلوبان"
        }), 400

    existing_username = User.query.filter(
        User.username == username,
        User.id != student.id
    ).first()

    if existing_username:
        return jsonify({
            "error": "اسم المستخدم مستخدم مسبقًا"
        }), 409

    existing_email = User.query.filter(
        User.email == email,
        User.id != student.id
    ).first()

    if existing_email:
        return jsonify({
            "error": "البريد الإلكتروني مستخدم مسبقًا"
        }), 409

    student.username = username
    student.email = email

    if password:
        student.set_password(password)

    db.session.commit()

    return jsonify({
        "message": "تم تحديث بيانات الطالب بنجاح",
        "student": {
            "id": student.id,
            "username": student.username,
            "email": student.email,
            "role": student.role,
            "is_active": student.is_active
        }
    })


@dashboard.post("/admin/students/<int:student_id>/toggle")
@role_required("admin", "superadmin")
def toggle_student(student_id):

    student = User.query.filter_by(
        id=student_id,
        role="student"
    ).first()

    if not student:
        return jsonify({
            "error": "الطالب غير موجود"
        }), 404

    student.is_active = not student.is_active

    db.session.commit()

    return jsonify({
        "message": "تم تحديث حالة الطالب",
        "student": {
            "id": student.id,
            "username": student.username,
            "email": student.email,
            "role": student.role,
            "is_active": student.is_active
        }
    })
