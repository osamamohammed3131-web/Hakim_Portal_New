from datetime import datetime
from uuid import uuid4
from threading import Lock

from flask import Blueprint, jsonify, request


competition = Blueprint(
    "competition",
    __name__,
    url_prefix="/api/competition"
)


# =========================================================
# جلسات المنافسة
#
# كل جهاز له جلسة مستقلة تمامًا.
# =========================================================

sessions = {}

sessions_lock = Lock()


# =========================================================
# إنشاء جلسة جديدة
# =========================================================

@competition.post("/session")
def create_session():

    session_id = str(uuid4())

    with sessions_lock:

        sessions[session_id] = {
            "session_id": session_id,
            "device_number": None,

            "image_hash": None,

            "question_number": 1,

            "answer": None,

            "answer_status": "waiting",

            "last_image_at": None,

            "last_answer_at": None,

            "created_at": datetime.utcnow().isoformat()
        }


    return jsonify({
        "success": True,
        "session_id": session_id
    }), 201


# =========================================================
# تسجيل رقم الجهاز
#
# مثال:
# 2000
# 2001
# 2002
# ...
# =========================================================

@competition.post("/session/<session_id>/device")
def register_device(session_id):

    with sessions_lock:

        session = sessions.get(session_id)


        if not session:

            return jsonify({
                "success": False,
                "error": "جلسة المنافسة غير موجودة"
            }), 404


        data = request.get_json(
            silent=True
        ) or {}


        device_number = data.get(
            "device_number"
        )


        if device_number is None:

            return jsonify({
                "success": False,
                "error": "رقم الجهاز مطلوب"
            }), 400


        try:

            device_number = int(
                device_number
            )

        except (
            ValueError,
            TypeError
        ):

            return jsonify({
                "success": False,
                "error": "رقم الجهاز غير صحيح"
            }), 400


        session["device_number"] = device_number


    return jsonify({
        "success": True,
        "session_id": session_id,
        "device_number": device_number
    })


# =========================================================
# حالة الجلسة
# =========================================================

@competition.get("/session/<session_id>")
def get_session(session_id):

    with sessions_lock:

        session = sessions.get(
            session_id
        )


        if not session:

            return jsonify({
                "success": False,
                "error": "جلسة المنافسة غير موجودة"
            }), 404


        return jsonify({
            "success": True,
            "session": dict(session)
        })


# =========================================================
# استقبال صورة السؤال
#
# في هذه المرحلة نستقبل الصورة فقط.
# تحليل الذكاء الاصطناعي سنضيفه في الخطوة التالية.
# =========================================================

@competition.post("/session/<session_id>/image")
def receive_image(session_id):

    with sessions_lock:

        session = sessions.get(
            session_id
        )


        if not session:

            return jsonify({
                "success": False,
                "error": "جلسة المنافسة غير موجودة"
            }), 404


        if "image" not in request.files:

            return jsonify({
                "success": False,
                "error": "لم يتم إرسال صورة"
            }), 400


        image = request.files["image"]


        if not image.filename:

            return jsonify({
                "success": False,
                "error": "اسم الصورة غير موجود"
            }), 400


        session["answer_status"] = "processing"

        session["last_image_at"] = (
            datetime.utcnow().isoformat()
        )


        current_question = (
            session["question_number"]
        )


    return jsonify({
        "success": True,
        "session_id": session_id,
        "question_number": current_question,
        "status": "processing",
        "message": "تم استلام الصورة"
    })
