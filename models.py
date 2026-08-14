from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


# =========================================================
# المستخدمون
# =========================================================

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(30),
        nullable=False,
        default="student"
    )

    # pending = قيد المراجعة
    # active = مقبول ونشط
    # rejected = مرفوض

    status = db.Column(
        db.String(30),
        nullable=False,
        default="pending"
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    # =====================================================
    # الخطة التي اختارها الطالب
    # =====================================================

    study_plan_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "study_plans.id"
        ),
        nullable=True
    )

    study_plan = db.relationship(
        "StudyPlan",
        backref=db.backref(
            "students",
            lazy=True
        )
    )

    # =====================================================
    # كلمات المرور
    # =====================================================

    def set_password(self, password):

        self.password_hash = (
            generate_password_hash(password)
        )

    def check_password(self, password):

        return check_password_hash(
            self.password_hash,
            password
        )


# =========================================================
# الخطط الدراسية A / B
# =========================================================

class StudyPlan(db.Model):

    __tablename__ = "study_plans"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    subjects = db.relationship(
        "Subject",
        backref="study_plan",
        lazy=True,
        cascade="all, delete-orphan"
    )


# =========================================================
# المواد الدراسية
# =========================================================

class Subject(db.Model):

    __tablename__ = "subjects"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    code = db.Column(
        db.String(50),
        nullable=True
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    plan_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "study_plans.id"
        ),
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )


# =========================================================
# المحاضرات
# =========================================================

class Lecture(db.Model):

    __tablename__ = "lectures"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "subjects.id"
        ),
        nullable=False
    )

    # رقم الأسبوع
    week_number = db.Column(
        db.Integer,
        nullable=True
    )

    # التاريخ المحدد للمحاضرة إذا كانت لمحاضرة بتاريخ معين
    lecture_date = db.Column(
        db.Date,
        nullable=True
    )

    # وقت المحاضرة الأصلي
    start_time = db.Column(
        db.Time,
        nullable=True
    )

    end_time = db.Column(
        db.Time,
        nullable=True
    )

    # رابط المحاضرة / Blackboard
    content_url = db.Column(
        db.String(500),
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    subject = db.relationship(
        "Subject",
        backref=db.backref(
            "lectures",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )


# =========================================================
# جدول الطالب الذكي
# =========================================================

class ScheduleItem(db.Model):

    __tablename__ = "schedule_items"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # الطالب صاحب الجدول
    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id"
        ),
        nullable=False
    )

    # المادة
    subject_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "subjects.id"
        ),
        nullable=False
    )

    # المحاضرة المرتبطة
    lecture_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "lectures.id"
        ),
        nullable=True
    )

    # =====================================================
    # اليوم
    #
    # 0 = الأحد
    # 1 = الإثنين
    # 2 = الثلاثاء
    # 3 = الأربعاء
    # 4 = الخميس
    # 5 = الجمعة
    # 6 = السبت
    # =====================================================

    day_of_week = db.Column(
        db.Integer,
        nullable=False
    )

    # بداية المحاضرة في جدول الطالب
    start_time = db.Column(
        db.Time,
        nullable=False
    )

    # نهاية المحاضرة في جدول الطالب
    end_time = db.Column(
        db.Time,
        nullable=False
    )

    # =====================================================
    # حالة المحاضرة
    #
    # upcoming = قادمة
    # live = جارية الآن
    # finished = انتهت
    # =====================================================

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

    # =====================================================
    # العلاقات
    # =====================================================

    user = db.relationship(
        "User",
        backref=db.backref(
            "schedule_items",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )

    subject = db.relationship(
        "Subject",
        backref=db.backref(
            "schedule_items",
            lazy=True
        )
    )

    lecture = db.relationship(
        "Lecture",
        backref=db.backref(
            "schedule_items",
            lazy=True
        )
    )
