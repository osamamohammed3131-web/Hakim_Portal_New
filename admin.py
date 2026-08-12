from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
def admin_dashboard():
    # التحقق من الصلاحيات بأمان تام (سواء بـ role أو is_admin)
    is_authorized = False
    
    if hasattr(current_user, 'role') and current_user.role in ['super_admin', 'admin']:
        is_authorized = True
    elif hasattr(current_user, 'is_admin') and current_user.is_admin:
        is_authorized = True
        
    if not is_authorized:
        flash('غير مسموح لك بالوصول إلى لوحة المشرف.')
        return redirect(url_for('auth.login'))
        
    return "مرحباً بك في لوحة تحكم المشرف العام - المنصة تعمل بكامل الصلاحيات."
