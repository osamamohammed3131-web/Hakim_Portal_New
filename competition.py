import os
import hashlib
import time
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
# إعدادات الذكاء الاصطناعي
# =========================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


# =========================================================
# عميل Gemini
# =========================================================

gemini_client = None

if GEMINI_API_KEY:

    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY
    )


# =========================================================
# جلسات الأجهزة
#
# كل جهاز له session مستقلة.
# =========================================================

sessions = {}

sessions_lock = Lock()


# =========================================================
# أرقام الأجهزة
#
# يبدأ من 2000
# =========================================================

next_device_number = 2000


# =========================================================
# طابور تحليل الذكاء الاصطناعي
#
# نستخدم عددًا محدودًا من الطلبات حتى لا نرسل
# مئات الطلبات إلى Gemini في نفس اللحظة.
#
# يمكن رفع الرقم لاحقًا بعد اختبار المنافسة.
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
# إنشاء جلسة
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
    image_bytes
):

    if not gemini_client:

        raise RuntimeError(
            "GEMINI_API_KEY غير موجود"
        )


    image_part = (
        types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/jpeg"
        )
    )


    prompt = """
أنت محلل أسئلة بصري لمنافسة تقنية تجريبية.

الصورة المرفقة تحتوي على سؤال قد يكون اختيارًا من متعدد.

اقرأ السؤال والخيارات الموجودة في الصورة بدقة شديدة.

حدد الإجابة الصحيحة فقط.

إذا كانت الخيارات:
A / B / C / D
أعد حرف الخيار الصحيح.

إذا كانت الخيارات تستخدم:
أ / ب / ج / د
أعد حرف الخيار الصحيح كما يظهر.

إذا كانت الخيارات مرقمة، أعد رقم الخيار الصحيح.

لا تشرح الحل.

لا تكتب أكثر من إجابة واحدة.

يجب أن يكون الرد النهائي قصيرًا جدًا، مثل:

A

أو:

ب

أو:

3
"""


    response = (
        gemini_client.models.generate_content(

            model=GEMINI_MODEL,

            contents=[
                image_part,
                prompt
            ]

        )
    )


    answer = (
        response.text or ""
    ).strip()


    if not answer:

        raise RuntimeError(
            "Gemini لم يعطِ إجابة"
        )


    return answer


# =========================================================
# مهمة التحليل في الخلفية
# =========================================================

def process_ai_answer(
    session_id,
    image_hash,
    image_bytes,
    question_number
):

    try:

        answer = analyze_question_image(
            image_bytes
        )


    except Exception as error:

        with sessions_lock:

            session = sessions.get(
                session_id
            )


            if not session:

                return


            # لا نسمح لنتيجة قديمة
            # بتغيير سؤال جديد.

            if (
                session.get(
                    "image_hash"
                )
                != image_hash
            ):

                return


            session[
                "answer_status"
            ] = "error"


            session[
                "answer"
            ] = None


            session[
                "last_answer_at"
            ] = (
                datetime.utcnow()
                .isoformat()
            )


        print(
            "Gemini error:",
            error
        )

        return


    # =====================================================
    # حفظ الإجابة للجهاز نفسه
    # =====================================================

    with sessions_lock:

        session = sessions.get(
            session_id
        )


        if not session:

            return


        # إذا تغير السؤال أثناء التحليل
        # نتجاهل الإجابة القديمة.

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
# استقبال لقطة الشاشة وتحليلها
# =========================================================

@competition.post(
    "/session/<session_id>/frame"
)
def receive_frame(
    session_id
):

    # -----------------------------------------------------
    # التحقق من الجلسة
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
    # التحقق من الصورة
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
    # بصمة الصورة
    # -----------------------------------------------------

    image_hash = hashlib.sha256(
        image_bytes
    ).hexdigest()


    with sessions_lock:

        session = sessions.get(
            session_id
        )


        if not session:

            return jsonify({

                "success":
                    False,

                "error":
                    "الجلسة غير موجودة"

            }), 404


        previous_hash = (
            session.get(
                "image_hash"
            )
        )


        # =================================================
        # الصورة نفسها
        # =================================================

        if (
            previous_hash
            == image_hash
        ):

            return jsonify({

                "success":
                    True,

                "same_question":
                    True,

                "question_number":
                    session[
                        "question_number"
                    ],

                "answer":
                    session[
                        "answer"
                    ],

                "answer_status":
                    session[
                        "answer_status"
                    ]

            })


        # =================================================
        # سؤال جديد
        # =================================================

        if previous_hash is not None:

            session[
                "question_number"
            ] += 1


        question_number = (
            session[
                "question_number"
            ]
        )


        session[
            "image_hash"
        ] = image_hash


        session[
            "answer"
        ] = None


        session[
            "answer_status"
        ] = "processing"


        session[
            "last_image_at"
        ] = (
            datetime.utcnow()
            .isoformat()
        )


        device_number = (
            session[
                "device_number"
            ]
        )


    # =====================================================
    # إرسال التحليل للطابور
    #
    # لا ننتظر Gemini هنا.
    # =====================================================

    ai_executor.submit(

        process_ai_answer,

        session_id,

        image_hash,

        image_bytes,

        question_number

    )


    return jsonify({

        "success":
            True,

        "new_question":
            True,

        "same_question":
            False,

        "device_number":
            device_number,

        "question_number":
            question_number,

        "answer":
            None,

        "answer_status":
            "processing"

    }), 202


# =========================================================
# الحصول على نتيجة الذكاء الاصطناعي
# =========================================================

@competition.get(
    "/session/<session_id>/result"
)
def get_result(
    session_id
):

    with sessions_lock:

        session = sessions.get(
            session_id
        )


        if not session:

            return jsonify({

                "success":
                    False,

                "error":
                    "الجلسة غير موجودة"

            }), 404


        return jsonify({

            "success":
                True,

            "session_id":
                session_id,

            "device_number":
                session[
                    "device_number"
                ],

            "question_number":
                session[
                    "question_number"
                ],

            "answer":
                session[
                    "answer"
                ],

            "answer_status":
                session[
                    "answer_status"
                ]

        })


# =========================================================
# إيقاف جلسة
# =========================================================

@competition.post(
    "/session/<session_id>/stop"
)
def stop_session(
    session_id
):

    with sessions_lock:

        session = sessions.get(
            session_id
        )


        if not session:

            return jsonify({

                "success":
                    False,

                "error":
                    "الجلسة غير موجودة"

            }), 404


        session[
            "answer_status"
        ] = "stopped"


    return jsonify({

        "success":
            True,

        "message":
            "تم إيقاف جلسة المنافسة"

    })
