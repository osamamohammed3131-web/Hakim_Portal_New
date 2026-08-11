from flask import Blueprint, render_template_string

community_bp = Blueprint('community', __name__)

@community_bp.route('/community')
def community():
    return '''
        <div style="font-family: Tahoma; direction: rtl; text-align: center; margin-top: 30px; background: #fff; padding: 20px; border-radius: 10px; width: 80%; margin-right: auto; margin-left: auto; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
            <h1 style="color: #2c3e50;">المجتمع الطلابي وقنوات التواصل</h1>
            <p style="font-size: 16px; color: #666;">مجموعات النقاش، قنوات الدفعة، ووسائل التواصل الأكاديمي.</p>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
            
            <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-top: 20px;">
                <div style="background: #e3f2fd; border: 1px solid #90caf9; padding: 15px; border-radius: 8px; width: 280px; text-align: right;">
                    <h4 style="color: #1976d2; margin-top: 0;">👥 مجموعة دفعة التحضيري</h4>
                    <p style="font-size: 14px; color: #444;">مجموعة النقاش الرسمية للطلاب ومتابعة الخطط والمهام.</p>
                    <span style="font-size: 13px; color: #1565c0; font-weight: bold;">الحالة: نشطة 🟢</span>
                </div>
                
                <div style="background: #e8f5e9; border: 1px solid #a5d6a7; padding: 15px; border-radius: 8px; width: 280px; text-align: right;">
                    <h4 style="color: #388e3c; margin-top: 0;">📢 قناة الإعلانات المركزية</h4>
                    <p style="font-size: 14px; color: #444;">القناة الرسمية لنشر التنبيهات والتعاميم والمواعيد الهامة.</p>
                    <span style="font-size: 13px; color: #2e7d32; font-weight: bold;">الحالة: متصلة 🟢</span>
                </div>
            </div>
            
            <br><br>
            <a href="/dashboard" style="padding: 10px 20px; background: #17a2b8; color: white; text-decoration: none; border-radius: 5px; margin-left: 10px;">لوحة التحكم</a>
            <a href="/" style="padding: 10px 20px; background: #6c757d; color: white; text-decoration: none; border-radius: 5px;">الرئيسية</a>
        </div>
    '''
