from main import app
from extensions import db
from models import StudyPlan, Subject


def seed_plans():
    with app.app_context():

        plan_a = StudyPlan.query.filter_by(name="A").first()

        if not plan_a:
            plan_a = StudyPlan(
                name="A",
                description="الخطة التمهيدية A"
            )
            db.session.add(plan_a)

        plan_b = StudyPlan.query.filter_by(name="B").first()

        if not plan_b:
            plan_b = StudyPlan(
                name="B",
                description="الخطة التمهيدية B"
            )
            db.session.add(plan_b)

        db.session.commit()

        subjects_a = [
            ("المهارات الأكاديمية", "A-ACA"),
            ("الحاسب الآلي", "A-CS"),
            ("اللغة الإنجليزية", "A-ENG"),
        ]

        subjects_b = [
            ("مهارات الاتصال", "B-COM"),
            ("الرياضيات", "B-MATH"),
            ("اللغة الإنجليزية", "B-ENG"),
        ]

        for name, code in subjects_a:
            exists = Subject.query.filter_by(
                name=name,
                plan_id=plan_a.id
            ).first()

            if not exists:
                db.session.add(
                    Subject(
                        name=name,
                        code=code,
                        plan_id=plan_a.id
                    )
                )

        for name, code in subjects_b:
            exists = Subject.query.filter_by(
                name=name,
                plan_id=plan_b.id
            ).first()

            if not exists:
                db.session.add(
                    Subject(
                        name=name,
                        code=code,
                        plan_id=plan_b.id
                    )
                )

        db.session.commit()

        print("Plans and subjects created successfully.")


if __name__ == "__main__":
    seed_plans()
