from flask import Blueprint, render_template_string

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    return '''
        <div style="font-family: Tahoma; direction: rtl; text-align: center; margin-top: 30px; background: #f9f9f9; padding: 20px; border-radius: 10px; width: 80%; margin-right: auto; margin-left: auto;">
            <h1 style="color: #2c3e50;">لوحة التحكم الأكاديمية - منصة حكيم</h1>
            <p style="font-size: 18px; color: #555;">مرحباً بك في بوابة الطلاب والأقسام الدراسية.</p>
            <hr style="border: 0; border-top: 1px solid #ccc; margin: 20px 0;">
            
            <h3 style="color: #007bff;">الخطط الدراسية والأقسام المتاحة:</h3>
            <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-top: 20px;">
                <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); width: 250px;">
                    <h4 style="color: #333;">الخطّة الدراسية (Plan A)</h4>
                    <p style="font-size: 14px; color: #666;">المقررات الأساسية وتفاصيل الفصل الدراسي الأول.</p>
                </div>
                <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); width: 250px;">
                    <h4 style="color: #333;">الخطّة الدراسية (Plan B)</h4>
                    <p style="font-size: 14px; color: #666;">المقررات المتقدمة والأنشطة الأكاديمية.</p>
                </div>
                <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); width: 250px;">
                    <h4 style="color: #333;">مسار قانون الإعلام</h4>
                    <p style="font-size: 14px; color: #666;">المراجع والمواد الخاصة بقانون الإعلام والتنظيم.</p>
                </div>
            </div>
            <br><br>
            <a href="/" style="padding: 10px 20px; background: #6c757d; color: white; text-decoration: none; border-radius: 5px;">العودة للرئيسية</a>
        </div>
    '''
