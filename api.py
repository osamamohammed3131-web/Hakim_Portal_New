from flask import Blueprint, jsonify
from models import StudyPlan, Subject

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
