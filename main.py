if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # إضافة حساب المشرف التلقائي
        admin = User.query.filter_by(email='superadmin@hakim.com').first()
        if not admin:
            from werkzeug.security import generate_password_hash
            hashed_password = generate_password_hash('Admin@Hakim2026!', method='pbkdf2:sha256')
            new_admin = User(username='SuperAdmin', email='superadmin@hakim.com', password=hashed_password, is_admin=True)
            db.session.add(new_admin)
            db.session.commit()
    app.run(debug=True)
