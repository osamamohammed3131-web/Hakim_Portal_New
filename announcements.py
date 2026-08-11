from flask import Blueprint, render_template_string

announcements_bp = Blueprint('announcements', __name__)

@announcements_bp.route('/announcements')
def announcements():
    return '''
        <div style="font-family: Tahoma; direction: rtl; text-align: center; margin-top: 30px; background: #fff; padding: 20px; border-radius: 10px; width: 80%; margin-right: auto; margin-left: auto; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
            <h1 style="color: #2c3e50;">لوحة الإعلانات والتنبيهات الأكاديمية</h1>
            <p style="font-size: 16px; color: #666;">آخر التحديثات والإعلانات الخاصة بمجموعات منصة حكيم وقنوات التواصل.</p>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
            
            <div style="text-align: right; background: #fdfefe; border: 1px solid #e1e8ed; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <h3 style="color: #007bff; margin-top: 0;">📢 إعلان هام: تحديث الجداول الدراسية</h3>
                <p style="color: #444; font-size: 15px;">تم اعتماد توزيع الخطط الدراسية (Plan A & Plan B) ومقررات قانون الإعلام رسمياً. يرجى من جميع الطلاب مراجعة لوحة التحكم للاطلاع على التفاصيل.</p>
                <span style="font-size: 12px; color: #999;">تاريخ النشر: أغسطس 2026</span>
            </div>

            <div style="text-align: right; background: #fdfefe; border: 1px solid #e1e8ed; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <h3 style="color: #28a745; margin-top: 0;">📌 تنبيه لطلاب المجموعات الأكاديمية</h3>
                <p style="color: #444; font-size: 15px;">سيتم رفع الملخصات والمواد الإضافية عبر قنوات المنصة السحابية تباعاً خلال هذا الأسبوع.</p>
                <span style="font-size: 12px; color: #999;">تاريخ النشر: أغسطس 2026</span>
            </div>
            
            <br>
            <a href="/dashboard" style="padding: 10px 20px; background: #17a2b8; color: white; text-decoration: none; border-radius: 5px; margin-left: 10px;">العودة للوحة التحكم</a>
            <a href="/" style="padding: 10px 20px; background: #6c757d; color: white; text-decoration: none; border-radius: 5px;">الرئيسية</a>
        </div>
    '''
