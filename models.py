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

    day_of_week = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

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
