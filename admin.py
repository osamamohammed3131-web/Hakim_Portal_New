from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role not in ['super_admin', 'admin']:
        flash('غير مسموح لك بالوصول إلى لوحة المشرف.')
        return redirect(url_for('auth.login'))
    return "مرحباً بك في لوحة تحكم المشرف العام - المنصة تعمل بكامل الصلاحيات."
