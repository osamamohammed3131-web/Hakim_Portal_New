from flask import Blueprint, jsonify

from auth import login_required, role_required
from models import User


dashboard = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/api/dashboard"
)


@dashboard.get("/student")
@login_required
def student_dashboard():
    from flask import session

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
    from flask import session

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
