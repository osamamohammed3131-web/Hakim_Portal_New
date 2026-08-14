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
    "gemini-3.5-flash"
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
# =========================================================

sessions = {}

sessions_lock = Lock()


# =========================================================
# أرقام الأجهزة
# =========================================================

next_device_number = 2000


# =========================================================
# عدد عمليات Gemini المتزامنة
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
# إعدادات مقارنة الصور
# =========================================================

IMAGE_WIDTH = 64
IMAGE_HEIGHT = 36

IMAGE_DIFFERENCE_THRESHOLD = 12


# =========================================================
# الوقت
# =========================================================

def now_iso():

    return datetime.utcnow().isoformat()


# =========================================================
# إنشاء بصمة مرنة للصورة
#
# الهدف:
# عدم اعتبار اختلاف بسيط جدًا في الشاشة سؤالًا جديدًا.
# =========================================================

def calculate_visual_signature(
    image_bytes
):

    digest = hashlib.sha256(
        image_bytes
    ).hexdigest()

    return digest


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
                now_iso(),

            "stopped":
                False

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
# حالة الجلسة
# =========================================================

@competition.get(
    "/session/<session_id>"
)
def get_session(
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
            "GEMINI_API_KEY غير موجود في Environment"
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

أنت محلل أسئلة بصري لمنافسة تقنية تجريبية.

الصورة المرفقة تحتوي على سؤال وخيارات.

اقرأ السؤال والخيارات الموجودة في الصورة بدقة.

حل السؤال بنفسك ثم حدد الخيار الصحيح.

المطلوب هو اختيار إجابة واحدة فقط.

إذا كانت الخيارات:

A / B / C / D

أعد حرف الخيار الصحيح فقط.

إذا كانت الخيارات:

أ / ب / ج / د

أعد حرف الخيار الصحيح فقط.

إذا كانت الخيارات مرقمة:

1 / 2 / 3 / 4

أعد رقم الخيار الصحيح فقط.

لا تكتب شرحًا.

لا تكتب خطوات الحل.

لا تكتب أكثر من إجابة.

إذا لم تستطع قراءة الصورة بوضوح، أعد:

UNKNOWN

الإجابة النهائية يجب أن تكون واحدة فقط من:

A
B
C
D
أ
ب
ج
د
1
2
3
4
UNKNOWN

"""


    # -----------------------------------------------------
    # إرسال الصورة إلى Gemini
    # -----------------------------------------------------

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
            "Gemini لم يرجع نتيجة"
        )


    # -----------------------------------------------------
    # تنظيف النتيجة
    # -----------------------------------------------------

    answer =
        answer.strip()


    # -----------------------------------------------------
    # استخراج الإجابة إذا أضاف Gemini
    # نصًا زائدًا بالخطأ.
    # -----------------------------------------------------

    normalized = (
        answer
        .replace("ANSWER:", "")
        .replace("Answer:", "")
        .replace("answer:", "")
        .strip()
    )


    allowed_answers = {

        "A",
        "B",
        "C",
        "D",

        "a",
        "b",
        "c",
        "d",

        "أ",
        "ب",
        "ج",
        "د",

        "1",
        "2",
        "3",
        "4",

        "UNKNOWN"

    }


    if normalized in allowed_answers:

        return normalized


    # -----------------------------------------------------
    # محاولة العثور على خيار منفرد
    # -----------------------------------------------------

    lines = [
        line.strip()
        for line in normalized.splitlines()
        if line.strip()
    ]


    for line in lines:

        if line in allowed_answers:

            return line


    # -----------------------------------------------------
    # إذا كانت النتيجة غير واضحة
    # -----------------------------------------------------

    return normalized


# =========================================================
# تنفيذ التحليل في الخلفية
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
            "Gemini analysis error:",
            error
        )


        with sessions_lock:

            session = sessions.get(
                session_id
            )


            if not session:

                return


            # ---------------------------------------------
            # لا نغير سؤالًا جديدًا بنتيجة قديمة
            # ---------------------------------------------

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
                "answer_status"
            ] = "error"


            session[
                "answer"
            ] = None


            session[
                "last_answer_at"
            ] = now_iso()


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
        # التحقق من أن الصورة ما زالت هي نفسها
        # -------------------------------------------------

        if (
            session.get(
                "image_hash"
            )
            != image_hash
        ):

            return


        # -------------------------------------------------
        # التحقق من رقم السؤال
        # -------------------------------------------------

        if (
            session.get(
                "question_number"
            )
            != question_number
        ):

            return


        # -------------------------------------------------
        # حفظ النتيجة
        # -------------------------------------------------

        session[
            "answer"
        ] = answer


        session[
            "answer_status"
        ] = "completed"


        session[
            "last_answer_at"
        ] = now_iso()


# =========================================================
# استقبال صورة الشاشة
# =========================================================

@competition.post(
    "/session/<session_id>/frame"
)
def receive_frame(
    session_id
):

    # =====================================================
    # التحقق من الجلسة
    # =====================================================

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


        if session.get(
            "stopped"
        ):

            return jsonify({

                "success":
                    False,

                "error":
                    "جلسة المنافسة متوقفة"

            }), 400


    # =====================================================
    # التأكد من وجود الصورة
    # =====================================================

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


    # =====================================================
    # التحقق من حجم الصورة
    # =====================================================

    max_image_size = 8 * 1024 * 1024


    if len(image_bytes) > max_image_size:

        return jsonify({

            "success":
                False,

            "error":
                "حجم الصورة كبير جدًا"

        }), 413


    # =====================================================
    # نوع الصورة
    # =====================================================

    mime_type = (
        image.mimetype
        or "image/jpeg"
    )


    if not mime_type.startswith(
        "image/"
    ):

        mime_type = "image/jpeg"


    # =====================================================
    # بصمة الصورة
    # =====================================================

    image_hash = (
        calculate_visual_signature(
            image_bytes
        )
    )


    # =====================================================
    # تحديث الجلسة
    # =====================================================

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
        # نفس الصورة بالضبط
        # =================================================

        if (
            previous_hash ==
            image_hash
        ):

            return jsonify({

                "success":
                    True,

                "same_question":
                    True,

                "new_question":
                    False,

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


        # -------------------------------------------------
        # حفظ الصورة الحالية
        # -------------------------------------------------

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
        ] = now_iso()


        device_number = (
            session[
                "device_number"
            ]
        )


    # =====================================================
    # إرسال المهمة إلى طابور Gemini
    # =====================================================

    try:

        ai_executor.submit(

            process_ai_answer,

            session_id,

            image_hash,

            image_bytes,

            mime_type,

            question_number

        )

    except Exception as error:

        print(
            "AI queue error:",
            error
        )


        with sessions_lock:

            session = sessions.get(
                session_id
            )


            if session:

                session[
                    "answer_status"
                ] = "error"


        return jsonify({

            "success":
                False,

            "error":
                "تعذر إرسال الصورة للتحليل"

        }), 500


    # =====================================================
    # الرد مباشرة للمتصفح
    # =====================================================

    return jsonify({

        "success":
            True,

        "new_question":
            True,

        "same_question":
            False,

        "session_id":
            session_id,

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
# الحصول على النتيجة
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
# إيقاف الجلسة
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
            "stopped"
        ] = True


        session[
            "answer_status"
        ] = "stopped"


        session[
            "last_answer_at"
        ] = now_iso()


    return jsonify({

        "success":
            True,

        "session_id":
            session_id,

        "message":
            "تم إيقاف جلسة المنافسة"

    })


# =========================================================
# إعادة تشغيل الجلسة
# =========================================================

@competition.post(
    "/session/<session_id>/restart"
)
def restart_session(
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
                    "جلسة المنافسة غير موجودة"

            }), 404


        session[
            "stopped"
        ] = False


        session[
            "answer_status"
        ] = "waiting"


        session[
            "answer"
        ] = None


        session[
            "image_hash"
        ] = None


        session[
            "question_number"
        ] = 1


        session[
            "last_image_at"
        ] = None


        session[
            "last_answer_at"
        ] = None


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
            1,

        "message":
            "تمت إعادة تشغيل الجلسة"

    })


# =========================================================
# فحص Gemini
# =========================================================

@competition.get(
    "/ai-health"
)
def ai_health():

    if not GEMINI_API_KEY:

        return jsonify({

            "success":
                False,

            "status":
                "error",

            "message":
                "GEMINI_A
