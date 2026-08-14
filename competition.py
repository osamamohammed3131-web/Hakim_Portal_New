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
    })# =========================================================
# اكتشاف تغير صورة السؤال
#
# إذا كانت الصورة نفسها:
#     same_question = True
#
# إذا تغيرت الصورة:
#     same_question = False
#     ويتم اعتبارها سؤالًا جديدًا
# =========================================================

@competition.post("/session/<session_id>/image/check")
def check_question_image(session_id):

    import hashlib

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


        image_bytes = image.read()


        if not image_bytes:

            return jsonify({
                "success": False,
                "error": "الصورة فارغة"
            }), 400


        # -------------------------------------------------
        # إنشاء بصمة للصورة
        # -------------------------------------------------

        image_hash = hashlib.sha256(
            image_bytes
        ).hexdigest()


        previous_hash = session.get(
            "image_hash"
        )


        # -------------------------------------------------
        # الصورة لم تتغير
        # -------------------------------------------------

        if (
            previous_hash is not None
            and previous_hash == image_hash
        ):

            return jsonify({
                "success": True,
                "same_question": True,
                "new_question": False,

                "session_id": session_id,

                "device_number":
                    session.get(
                        "device_number"
                    ),

                "question_number":
                    session.get(
                        "question_number"
                    ),

                "answer":
                    session.get(
                        "answer"
                    ),

                "answer_status":
                    session.get(
                        "answer_status"
                    ),

                "message":
                    "السؤال ما زال نفسه"
            })


        # -------------------------------------------------
        # الصورة تغيرت
        # -------------------------------------------------

        session["image_hash"] = image_hash


        # السؤال الجديد
        if previous_hash is not None:

            session["question_number"] += 1


        session["answer"] = None

        session["answer_status"] = "processing"

        session["last_image_at"] = (
            datetime.utcnow().isoformat()
        )


        return jsonify({
            "success": True,
            "same_question": False,
            "new_question": True,

            "session_id": session_id,

            "device_number":
                session.get(
                    "device_number"
                ),

            "question_number":
                session.get(
                    "question_number"
                ),

            "answer": None,

            "answer_status": "processing",

            "message":
                "تم اكتشاف سؤال جديد، جاهز للتحليل"
        })# =========================================================
# محلل الصور بالذكاء الاصطناعي
# =========================================================

import os
import base64

from openai import OpenAI


# ---------------------------------------------------------
# إنشاء عميل OpenAI
#
# المفتاح يتم قراءته من:
# OPENAI_API_KEY
#
# ولا يوجد المفتاح داخل الكود.
# ---------------------------------------------------------

openai_client = OpenAI(
    api_key=os.environ.get(
        "OPENAI_API_KEY"
    )
)


# =========================================================
# تحليل صورة السؤال
# =========================================================

def analyze_question_image(image_bytes):

    image_base64 = base64.b64encode(
        image_bytes
    ).decode("utf-8")


    response = openai_client.responses.create(

        model="gpt-5.5",

        input=[
            {
                "role": "user",

                "content": [

                    {
                        "type": "input_text",

                        "text": """
أنت محلل أسئلة في منافسة تقنية تجريبية.

حلل صورة السؤال بدقة.

إذا كان السؤال من نوع الاختيار من متعدد:
حدد الإجابة الصحيحة.

أعد النتيجة بهذا الشكل فقط:

ANSWER: A

أو:

ANSWER: B

أو:

ANSWER: C

أو:

ANSWER: D

إذا كانت الخيارات مختلفة، اكتب الخيار الصحيح بوضوح.

لا تكتب شرحًا طويلًا.
لا تكتب أكثر من إجابة واحدة.
""",
                    },

                    {
                        "type": "input_image",

                        "image_url":
                            f"data:image/jpeg;base64,{image_base64}",
                    },

                ],
            }
        ],
    )


    answer = (
        response.output_text
        .strip()
    )


    return answer# =========================================================
# تحليل السؤال وربط النتيجة بنفس الجهاز
# =========================================================

@competition.post("/session/<session_id>/analyze")
def analyze_session_image(session_id):

    # -----------------------------------------------------
    # استقبال الجلسة
    # -----------------------------------------------------

    with sessions_lock:

        session = sessions.get(
            session_id
        )

        if not session:
            return jsonify({
                "success": False,
                "error": "جلسة المنافسة غير موجودة"
            }), 404


    # -----------------------------------------------------
    # التأكد من وجود الصورة
    # -----------------------------------------------------

    if "image" not in request.files:

        return jsonify({
            "success": False,
            "error": "لم يتم إرسال صورة"
        }), 400


    image = request.files["image"]

    image_bytes = image.read()


    if not image_bytes:

        return jsonify({
            "success": False,
            "error": "الصورة فارغة"
        }), 400


    # -----------------------------------------------------
    # إنشاء بصمة للصورة
    # -----------------------------------------------------

    import hashlib

    image_hash = hashlib.sha256(
        image_bytes
    ).hexdigest()


    # -----------------------------------------------------
    # التحقق من السؤال الحالي
    # -----------------------------------------------------

    with sessions_lock:

        session = sessions.get(
            session_id
        )

        previous_hash = session.get(
            "image_hash"
        )


        # -------------------------------------------------
        # نفس السؤال
        # -------------------------------------------------

        if (
            previous_hash == image_hash
            and session.get("answer") is not None
        ):

            return jsonify({
                "success": True,

                "same_question": True,

                "new_question": False,

                "session_id": session_id,

                "device_number":
                    session.get(
                        "device_number"
                    ),

                "question_number":
                    session.get(
                        "question_number"
                    ),

                "answer":
                    session.get(
                        "answer"
                    ),

                "answer_status":
                    "completed",

                "message":
                    "السؤال نفسه، تم استخدام الإجابة السابقة"
            })


        # -------------------------------------------------
        # سؤال جديد
        # -------------------------------------------------

        if previous_hash is not None:

            session["question_number"] += 1


        current_question = (
            session["question_number"]
        )


        session["image_hash"] = image_hash

        session["answer"] = None

        session["answer_status"] = "processing"

        session["last_image_at"] = (
            datetime.utcnow().isoformat()
        )


        device_number = (
            session.get("device_number")
        )


    # -----------------------------------------------------
    # تحليل الصورة
    #
    # مهم:
    # لا نضع استدعاء OpenAI داخل sessions_lock
    # حتى لا نوقف بقية الأجهزة أثناء انتظار الذكاء الاصطناعي.
    # -----------------------------------------------------

    try:

        answer = analyze_question_image(
            image_bytes
        )

    except Exception as error:

        with sessions_lock:

            session = sessions.get(
                session_id
            )

            if session:

                session["answer_status"] = (
                    "error"
                )


        return jsonify({
            "success": False,
            "error": "حدث خطأ أثناء تحليل الصورة"
        }), 500


    # -----------------------------------------------------
    # حفظ النتيجة للجهاز نفسه
    # -----------------------------------------------------

    with sessions_lock:

        session = sessions.get(
            session_id
        )

        if not session:

            return jsonify({
                "success": False,
                "error": "جلسة المنافسة انتهت"
            }), 404


        session["answer"] = answer

        session["answer_status"] = (
            "completed"
        )

        session["last_answer_at"] = (
            datetime.utcnow().isoformat()
        )


    # -----------------------------------------------------
    # إرسال النتيجة
    # -----------------------------------------------------

    return jsonify({

        "success": True,

        "same_question": False,

        "new_question": True,

        "session_id": session_id,

        "device_number": device_number,

        "question_number":
            current_question,

        "answer": answer,

        "answer_status":
            "completed",

        "message":
            "تم تحليل السؤال بنجاح"
    })
