from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="student")
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class StudyPlan(db.Model):
    __tablename__ = "study_plans"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    subjects = db.relationship(
        "Subject",
        backref="study_plan",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)

    plan_id = db.Column(
        db.Integer,
        db.ForeignKey("study_plans.id"),
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )


class Lecture(db.Model):
    __tablename__ = "lectures"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subjects.id"),
        nullable=False
    )

    week_number = db.Column(db.Integer, nullable=True)
    lecture_date = db.Column(db.Date, nullable=True)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)

    content_url = db.Column(db.String(500), nullable=True)

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    subject = db.relationship(
        "Subject",
        backref=db.backref("lectures", lazy=True)
    )


class ScheduleItem(db.Model):
    __tablename__ = "schedule_items"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subjects.id"),
        nullable=False
    )

    lecture_id = db.Column(
        db.Integer,
        db.ForeignKey("lectures.id"),
        nullable=True
    )

    day_of_week = db.Column(
        db.Integer,
        nullable=False
    )

    start_time = db.Column(
        db.Time,
        nullable=False
    )

    end_time = db.Column(
        db.Time,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="upcoming"
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    user = db.relationship(
        "User",
        backref=db.backref("schedule_items", lazy=True)
    )

    subject = db.relationship(
        "Subject",
        backref=db.backref("schedule_items", lazy=True)
    )

    lecture = db.relationship(
        "Lecture",
        backref=db.backref("schedule_items", lazy=True)
    )
