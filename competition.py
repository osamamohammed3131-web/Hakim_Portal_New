# =========================================================
# competition.py
# Hakim AI Competition
# =========================================================

import os
import hashlib
from datetime import datetime
from uuid import uuid4
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

from flask import Blueprint, jsonify, request

from google import genai
from google.genai import types


# =========================================================
# Blueprint
# =========================================================

competition = Blueprint(
    "competition",
    __name__,
    url_prefix="/api/competition"
)


# =========================================================
# إعدادات Gemini
# =========================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


# =========================================================
# إنشاء عميل Gemini
# =========================================================

gemini_client = None

if GEMINI_API_KEY:

    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY
    )


# =========================================================
# جلسات الأجهزة
#
# كل جهاز يحصل على جلسة مستقلة.
# =========================================================

sessions = {}

sessions_lock = Lock()


# =========================================================
# أرقام الأجهزة
#
# تبدأ من 2000
# =========================================================

next_device_number = 2000


# =========================================================
# عدد عمليات الذكاء الاصطناعي المتزامنة
# =========================================================

AI_WORKERS = int(
    os.getenv(
        "AI_WORKERS",
        "8"
    )
)


ai_executor = ThreadPoolExecutor(
    max_workers=AI_WORKERS
)


# =========================================================
# إنشاء جلسة جديدة
# =========================================================

@competition.post("/session")
def create_session():

    global next_device_number

    with sessions_lock:

        session_id = str(
            uuid4()
        )

        device_number = (
            next_device_number
        )

        next_device_number += 1

        sessions[session_id] = {

            "session_id":
                session_id,

            "device_number":
                device_number,

            "image_hash":
                None,

            "question_number":
                1,

            "answer":
                None,

            "answer_status":
                "waiting",

            "last_image_at":
                None,

            "last_answer_at":
                None,

            "created_at":
                datetime.utcnow().isoformat()

        }

    return jsonify({

        "success":
            True,

        "session_id":
            session_id,

        "device_number":
            device_number

    }), 201


# =========================================================
# الحصول على حالة الجلسة
# =========================================================

@competition.get("/session/<session_id>")
def get_session(session_id):

    with sessions_lock:

        session = sessions.get(
            session_id
        )

        if not session:

            return jsonify({

                "success":
                    False,

                "error":
                    "جلسة المنافسة غير موجودة"

            }), 404

        return jsonify({

            "success":
                True,

            "session":
                dict(session)

        })


# =========================================================
# تحليل صورة السؤال بواسطة Gemini
# =========================================================

def analyze_question_image(
    image_bytes,
    mime_type="image/jpeg"
):

    if not gemini_client:

        raise RuntimeError(
            "GEMINI_API_KEY غير موجود في Environment Variables"
        )


    # -----------------------------------------------------
    # تجهيز الصورة
    # -----------------------------------------------------

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type
    )


    # -----------------------------------------------------
    # تعليمات التحليل
    # -----------------------------------------------------

    prompt = """
أنت محلل بصري لأسئلة منافسة تقنية تجريبية.

الصورة المرفقة تحتوي على سؤال وقد تحتوي على عدة خيارات.

اقرأ السؤال والخيارات الموجودة في الصورة بدقة.

المطلوب هو تحديد الإجابة الصحيحة فقط.

القواعد:

1. اقرأ السؤال كاملًا.
2. اقرأ جميع الخيارات.
3. حل السؤال داخليًا قبل اختيار الإجابة.
4. لا تخمن إذا كانت الصورة غير واضحة.
5. أعد خيارًا واحدًا فقط.
6. لا تكتب شرحًا.
7. لا تكتب أي نص إضافي.

إذا كانت الخيارات:

A / B / C / D

أعد:

A

أو B أو C أو D.

إذا كانت الخيارات:

أ / ب / ج / د

أعد الحرف الصحيح كما يظهر في الصورة.

إذا كانت الخيارات مرقمة:

1 / 2 / 3 / 4

أعد رقم الخيار الصحيح.

الرد النهائي يجب أن يكون الإجابة فقط.
"""


    # -----------------------------------------------------
    # إرسال الصورة إلى Gemini
    # -----------------------------------------------------

    response = gemini_client.models.generate_content(

        model=GEMINI_MODEL,

        contents=[
            image_part,
            prompt
        ]

    )


    # -----------------------------------------------------
    # استخراج النص
    # -----------------------------------------------------

    answer = (
        response.text or ""
    ).strip()


    if not answer:

        raise RuntimeError(
            "Gemini لم يرجع إجابة"
        )


    # -----------------------------------------------------
    # تنظيف الإجابة
    #
    # نأخذ أول سطر فقط لأن النظام
    # يريد إجابة قصيرة.
    # -----------------------------------------------------

    answer = answer.splitlines()[0].strip()


    # إزالة بعض العلامات الشائعة

    answer = answer.replace(
        "**",
        ""
    ).strip()

    answer = answer.replace(
        "`",
        ""
    ).strip()


    if not answer:

        raise RuntimeError(
            "إجابة Gemini فارغة بعد المعالجة"
        )


    return answer


# =========================================================
# تنفيذ تحليل Gemini في الخلفية
# =========================================================

def process_ai_answer(
    session_id,
    image_hash,
    image_bytes,
    mime_type,
    question_number
):

    try:

        answer = analyze_question_image(

            image_bytes,

            mime_type

        )

    except Exception as error:

        print(
            "Gemini error:",
            error
        )

        with sessions_lock:

            session = sessions.get(
                session_id
            )

            if not session:

                return


            # -------------------------------------------------
            # لا نغيّر حالة سؤال جديد بنتيجة قديمة
            # -------------------------------------------------

            if (
                session.get(
                    "image_hash"
                )
                != image_hash
            ):

                return


            if (
                session.get(
                    "question_number"
                )
                != question_number
            ):

                return


            session[
                "answer"
            ] = None


            session[
                "answer_status"
            ] = "error"


            session[
                "last_answer_at"
            ] = (
                datetime.utcnow()
                .isoformat()
            )

        return


    # =====================================================
    # حفظ الإجابة
    # =====================================================

    with sessions_lock:

        session = sessions.get(
            session_id
        )

        if not session:

            return


        # -------------------------------------------------
        # التأكد أن السؤال لم يتغير
        # -------------------------------------------------

        if (
            session.get(
                "image_hash"
            )
            != image_hash
        ):

            return


        if (
            session.get(
                "question_number"
            )
            != question_number
        ):

            return


        # -------------------------------------------------
        # حفظ الإجابة
        # -------------------------------------------------

        session[
            "answer"
        ] = answer


        session[
            "answer_status"
        ] = "completed"


        session[
            "last_answer_at"
        ] = (
            datetime.utcnow()
            .isoformat()
        )


# =========================================================
# استقبال لقطة الشاشة
# =========================================================

@competition.post(
    "/session/<session_id>/frame"
)
def receive_frame(session_id):

    # -----------------------------------------------------
    # التأكد من الجلسة
    # -----------------------------------------------------

    with sessions_lock:

        session = sessions.get(
            session_id
        )

        if not session:

            return jsonify({

                "success":
                    False,

                "error":
                    "جلسة المنافسة غير موجودة"

            }), 404


    # -----------------------------------------------------
    # التأكد من وجود الصورة
    # -----------------------------------------------------

    if "image" not in request.files:

        return jsonify({

            "success":
                False,

            "error":
                "لم يتم إرسال صورة"

        }), 400


    image = request.files[
        "image"
    ]


    image_bytes = image.read()


    if not image_bytes:

        return jsonify({

            "success":
                False,

            "error":
                "الصورة فارغة"

        }), 400


    # -----------------------------------------------------
    # معرفة نوع الصورة
    # -----------------------------------------------------

    mime_type = (
        image.mimetype
        or "
