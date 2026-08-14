import os
import hashlib
from datetime import datetime
from uuid import uuid4
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

from flask import Blueprint, jsonify, request

from google import genai
from google.genai import types


competition = Blueprint(
    "competition",
    __name__,
    url_prefix="/api/competition"
)


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


gemini_client = None

if GEMINI_API_KEY:
    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY
    )


sessions = {}

sessions_lock = Lock()


next_device_number = 2000


try:
    AI_WORKERS = max(
        1,
        int(
            os.getenv(
                "AI_WORKERS",
                "8"
            )
        )
    )
except Exception:
    AI_WORKERS = 8


ai_executor = ThreadPoolExecutor(
    max_workers=AI_WORKERS
)


def utc_now():
    return datetime.utcnow().isoformat()@competition.post("/session")
def create_session():

    global next_device_number

    with sessions_lock:

        session_id = str(uuid4())

        device_number = next_device_number

        next_device_number += 1

        sessions[session_id] = {
            "session_id": session_id,
            "device_number": device_number,
            "image_hash": None,
            "question_number": 1,
            "answer": None,
            "answer_status": "waiting",
            "last_image_at": None,
            "last_answer_at": None,
            "created_at": utc_now(),
            "stopped": False
        }

    return jsonify({
        "success": True,
        "session_id": session_id,
        "device_number": device_number,
        "question_number": 1
    }), 201


@competition.get("/session/<session_id>")
def get_session(session_id):

    with sessions_lock:

        session = sessions.get(session_id)

        if not session:
            return jsonify({
                "success": False,
                "error": "جلسة المنافسة غير موجودة"
            }), 404

        return jsonify({
            "success": True,
            "session": dict(session)
        })def analyze_question_image(
    image_bytes,
    mime_type="image/jpeg"
):

    if not gemini_client:
        raise RuntimeError(
            "GEMINI_API_KEY غير موجود"
        )

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type
    )

    prompt = """
أنت محلل بصري لأسئلة منافسة تقنية.

الصورة المرفقة تحتوي على سؤال وقد تحتوي على خيارات.

اقرأ السؤال والخيارات الموجودة في الصورة بدقة شديدة،
ثم حدد الإجابة الصحيحة.

القواعد:

1. اقرأ السؤال كاملًا.
2. اقرأ جميع الخيارات.
3. حل السؤال داخليًا قبل اختيار الإجابة.
4. أعد خيارًا واحدًا فقط.
5. لا تكتب شرحًا.
6. لا تكتب أي نص إضافي.

إذا كانت الخيارات:

A / B / C / D

أعد حرف الخيار الصحيح فقط.

إذا كانت الخيارات:

أ / ب / ج / د

أعد الحرف الصحيح كما يظهر في الصورة.

إذا كانت الخيارات مرقمة:

1 / 2 / 3 / 4

أعد رقم الخيار الصحيح.

الإجابة النهائية يجب أن تكون قصيرة جدًا.
"""

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[
            image_part,
            prompt
        ]
    )

    answer = (
        response.text or ""
    ).strip()

    if not answer:
        raise RuntimeError(
            "Gemini لم يرجع إجابة"
        )

    answer = answer.replace(
        "**",
        ""
    ).replace(
        "`",
        ""
    ).strip()

    lines = [
        line.strip()
        for line in answer.splitlines()
        if line.strip()
    ]

    if lines:
        answer = lines[0]

    if not answer:
        raise RuntimeError(
            "إجابة Gemini فارغة"
        )

    return answerdef process_ai_answer(
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
            repr(error)
        )

        with sessions_lock:

            session = sessions.get(
                session_id
            )

            if not session:
                return

            if session.get(
                "image_hash"
            ) != image_hash:
                return

            if session.get(
                "question_number"
            ) != question_number:
                return

            session["answer"] = None

            session[
                "answer_status"
            ] = "error"

            session[
                "last_answer_at"
            ] = utc_now()

        return


    with sessions_lock:

        session = sessions.get(
            session_id
        )

        if not session:
            return

        if session.get(
            "image_hash"
        ) != image_hash:
            return

        if session.get(
            "question_number"
        ) != question_number:
            return

        if session.get(
            "stopped"
        ):
            return

        session["answer"] = answer

        session[
            "answer_status"
        ] = "completed"

        session[
            "last_answer_at"
        ] = utc_now()@competition.post("/session/<session_id>/frame")
def receive_frame(session_id):

    with sessions_lock:

        session = sessions.get(session_id)

        if not session:
            return jsonify({
                "success": False,
                "error": "جلسة المنافسة غير موجودة"
            }), 404

        if session.get("stopped"):
            return jsonify({
                "success": False,
                "error": "الجلسة متوقفة"
            }), 409


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


    mime_type = (
        image.mimetype
        or "image/jpeg"
    )

    if not mime_type.startswith("image/"):
        mime_type = "image/jpeg"


    image_hash = hashlib.sha256(
        image_bytes
    ).hexdigest()


    with sessions_lock:

        session = sessions.get(session_id)

        if not session:
            return jsonify({
                "success": False,
                "error": "الجلسة غير موجودة"
            }), 404

        if session.get("stopped"):
            return jsonify({
                "success": False,
                "error": "الجلسة متوقفة"
            }), 409


        previous_hash = session.get(
            "image_hash"
        )


        if previous_hash == image_hash:

            return jsonify({
                "success": True,
                "same_question": True,
                "new_question": False,
                "session_id": session_id,
                "device_number": session[
                    "device_number"
                ],
                "question_number": session[
                    "question_number"
                ],
                "answer": session[
                    "answer"
                ],
                "answer_status": session[
                    "answer_status"
                ]
            })


        if previous_hash is not None:
            session[
                "question_number"
            ] += 1


        question_number = session[
            "question_number"
        ]


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
        ] = utc_now()


        device_number = session[
            "device_number"
        ]


    ai_executor.submit(
        process_ai_answer,
        session_id,
        image_hash,
        image_bytes,
        mime_type,
        question_number
    )


    return jsonify({
        "success": True,
        "new_question": True,
        "same_question": False,
        "session_id": session_id,
        "device_number": device_number,
        "question_number": question_number,
        "answer": None,
        "answer_status": "processing",
        "message": "تم استلام السؤال وبدأ التحليل"
    }), 202@competition.get("/session/<session_id>/result")
def get_result(session_id):

    with sessions_lock:

        session = sessions.get(
            session_id
        )

        if not session:

            return jsonify({
                "success": False,
                "error": "الجلسة غير موجودة"
            }), 404


        return jsonify({
            "success": True,
            "session_id": session_id,
            "device_number": session[
                "device_number"
            ],
            "question_number": session[
                "question_number"
            ],
            "answer": session[
                "answer"
            ],
            "answer_status": session[
                "answer_status"
            ],
            "last_image_at": session[
                "last_image_at"
            ],
            "last_answer_at": session[
                "last_answer_at"
            ]
        })


@competition.post("/session/<session_id>/stop")
def stop_session(session_id):

    with sessions_lock:

        session = sessions.get(
            session_id
        )

        if not session:

            return jsonify({
                "success": False,
                "error": "الجلسة غير موجودة"
            }), 404


        session["stopped"] = True

        session[
            "answer_status"
        ] = "stopped"

        session["answer"] = None


    return jsonify({
        "success": True,
        "session_id": session_id,
        "message": "تم إيقاف جلسة المنافسة"
    })


@competition.get("/ai-health")
def ai_health():

    if not GEMINI_API_KEY:

        return jsonify({
            "success": False,
            "ai": "Gemini",
            "status": "missing_api_key",
            "message": "GEMINI_API_KEY غير موجود"
        }), 503


    if not gemini_client:

        return jsonify({
            "success": False,
            "ai": "Gemini",
            "status": "not_initialized"
        }), 503


    return jsonify({
        "success": True,
        "ai": "Gemini",
        "status": "ready",
        "model": GEMINI_MODEL
    })


@competition.get("/info")
def competition_info():

    with sessions_lock:

        active_sessions = len(
            sessions
        )


    return jsonify({
        "success": True,
        "name": "Hakim AI Competition",
        "status": "running",
        "ai": "Gemini",
        "model": GEMINI_MODEL,
        "active_sessions": active_sessions,
        "ai_workers": AI_WORKERS
    })
