from flask import Blueprint, render_template_string
from flask_login import login_required
from auth import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
@admin_required
def admin_panel():
    return '''
    <div style="font-family: Tahoma; direction: rtl; text-align: center; margin-top: 50px;">
        <h1 style="color: #c0392b;">لوحة تحكم المشرفين (Admin Panel)</h1>
        <p style="font-size: 16px; color: #555;">مرحباً بك في لوحة الإدارة.</p>
    </div>
    '''
