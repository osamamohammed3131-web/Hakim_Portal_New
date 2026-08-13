from datetime import datetime

from flask import Blueprint, jsonify, request, session

from extensions import db
from models import StudyPlan, Subject, ScheduleItem


api = Blueprint("api", __name__, url_prefix="/api")


@api.get("/plans")
def get_plans():
    plans = StudyPlan.query.filter_by(is_active=True).all()

    return jsonify([
        {
            "id": plan.id,
            "name": plan.name,
            "description": plan.description,
            "subjects": [
                {
                    "id": subject.id,
                    "name": subject.name,
                    "code": subject.code,
                    "description": subject.description,
                }
                for subject in plan.subjects
                if subject.is_active
            ],
        }
        for plan in plans
    ])


@api.get("/plans/<int:plan_id>/subjects")
def get_plan_subjects(plan_id):
    plan = StudyPlan.query.filter_by(
        id=plan_id,
        is_active=True
    ).first()

    if not plan:
        return jsonify({
            "error": "الخطة غير موجودة"
        }), 404

    subjects = Subject.query.filter_by(
        plan_id=plan.id,
        is_active=True
    ).all()

    return jsonify([
        {
            "id": subject.id,
            "name": subject.name,
            "code": subject.code,
            "description": subject.description,
        }
        for subject in subjects
    ])


@api.post("/schedule")
def create_schedule_item():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "error": "يجب تسجيل الدخول أولًا"
        }), 401

    data = request.get_json(silent=True) or {}

    subject_id = data.get("subject_id")
    lecture_id = data.get("lecture_id")
    day_of_week = data.get("day_of_week")
    start_time = data.get("start_time")
    end_time = data.get("end_time")

    if not all([
        subject_id,
        day_of_week,
        start_time,
        end_time
    ]):
        return jsonify({
            "error": "بيانات الجدول غير مكتملة"
        }), 400

    subject = Subject.query.filter_by(
        id=subject_id,
        is_active=True
    ).first()

    if not subject:
        return jsonify({
            "error": "المادة غير موجودة"
        }), 404

    try:
        start = datetime.strptime(
            start_time,
            "%H:%M"
        ).time()

        end = datetime.strptime(
            end_time,
            "%H:%M"
        ).time()

        day = int(day_of_week)

    except (ValueError, TypeError):
        return jsonify({
            "error": "صيغة اليوم أو الوقت غير صحيحة"
        }), 400

    if day < 0 or day > 6:
        return jsonify({
            "error": "اليوم يجب أن يكون بين 0 و6"
        }), 400

    item = ScheduleItem(
        user_id=user_id,
        subject_id=subject.id,
        lecture_id=lecture_id,
        day_of_week=day,
        start_time=start,
        end_time=end,
        status="upcoming"
    )

    db.session.add(item)
    db.session.commit()

    return jsonify({
        "message": "تمت إضافة الموعد إلى الجدول",
        "schedule": {
            "id": item.id,
            "subject_id": item.subject_id,
            "lecture_id": item.lecture_id,
            "day_of_week": item.day_of_week,
            "start_time": item.start_time.strftime("%H:%M"),
            "end_time": item.end_time.strftime("%H:%M"),
            "status": item.status
        }
    }), 201


@api.get("/schedule")
def get_schedule():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "error": "يجب تسجيل الدخول أولًا"
        }), 401

    items = ScheduleItem.query.filter_by(
        user_id=user_id,
        is_active=True
    ).order_by(
        ScheduleItem.day_of_week,
        ScheduleItem.start_time
    ).all()

    return jsonify([
        {
            "id": item.id,
            "subject": {
                "id": item.subject.id,
                "name": item.subject.name,
                "code": item.subject.code
            },
            "lecture_id": item.lecture_id,
            "day_of_week": item.day_of_week,
            "start_time": item.start_time.strftime("%H:%M"),
            "end_time": item.end_time.strftime("%H:%M"),
            "status": item.status
        }
        for item in items
    ])
