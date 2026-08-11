from flask import Blueprint, render_template_string

resources_bp = Blueprint('resources', __name__)

@resources_bp.route('/resources')
def resources():
    return '''
        <div style="font-family: Tahoma; direction: rtl; text-align: center; margin-top: 30px; background: #fff; padding: 20px; border-radius: 10px; width: 80%; margin-right: auto; margin-left: auto; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
            <h1 style="color: #2c3e50;">بنك الملفات والمراجع الأكاديمية</h1>
            <p style="font-size: 16px; color: #666;">مستودع الكتب، الملخصات، والمراجع الخاصة بجميع المسارات الدراسية.</p>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
            
            <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-top: 20px;">
                <div style="background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; border-radius: 8px; width: 280px; text-align: right;">
                    <h4 style="color: #007bff; margin-top: 0;">📚 مرجع Plan A الأساسي</h4>
                    <p style="font-size: 14px; color: #555;">ملفات الشرح والكتب المقررة للفصل الدراسي الأول.</p>
                    <a href="#" style="color: #007bff; text-decoration: none; font-size: 14px;">⬇️ تحميل الملفات (قريباً)</a>
                </div>
                
                <div style="background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; border-radius: 8px; width: 280px; text-align: right;">
                    <h4 style="color: #28a745; margin-top: 0;">📘 مرجع Plan B المتقدم</h4>
                    <p style="font-size: 14px; color: #555;">التمارين العملية والملخصات الخاصة بالمقرر.</p>
                    <a href="#" style="color: #28a745; text-decoration: none; font-size: 14px;">⬇️ تحميل الملفات (قريباً)</a>
                </div>

                <div style="background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; border-radius: 8px; width: 280px; text-align: right;">
                    <h4 style="color: #dc3545; margin-top: 0;">⚖️ مراجع قانون الإعلام</h4>
                    <p style="font-size: 14px; color: #555;">اللوائح التنظيمية، المواد القانونية، والأبحاث المقررة.</p>
                    <a href="#" style="color: #dc3545; text-decoration: none; font-size: 14px;">⬇️ تحميل الملفات (قريباً)</a>
                </div>
            </div>
            
            <br><br>
            <a href="/dashboard" style="padding: 10px 20px; background: #17a2b8; color: white; text-decoration: none; border-radius: 5px; margin-left: 10px;">لوحة التحكم</a>
            <a href="/" style="padding: 10px 20px; background: #6c757d; color: white; text-decoration: none; border-radius: 5px;">الرئيسية</a>
        </div>
    '''
