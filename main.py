@app.route('/student/plan')
@login_required
def student_plan():
    # جلب المواد الخاصة حصرياً بخطة الطالب (A أو B) المسجلة في حسابه
    materials = Material.query.filter_by(plan_type=current_user.plan_type).all()
    return render_template_string('''
        <div style="font-family:Tahoma; direction:rtl; padding:25px; background:#f8fafc; max-width:800px; margin:auto;">
            <h2 style="color:#0284c7;">بيئة الخطة التمهيدية الفعلية (خطة {{ current_user.plan_type }})</h2>
            <p>المقررات الدراسية المعتمدة لحسابك والمزودة بالمحاضرات والمصادر:</p>
            <hr>
            {% for mat in materials %}
                <div style="background:white; padding:15px; margin-bottom:15px; border-radius:8px; border:1px solid #e2e8f0;">
                    <h3 style="color:#0f172a; margin:0 0 10px 0;">{{ mat.name }}</h3>
                    <p style="color:#64748b;">{{ mat.description }}</p>
                    <a href="/material/{{ mat.id }}" style="background:#0284c7; color:white; padding:6px 12px; text-decoration:none; border-radius:4px; font-size:14px;">الدخول إلى تفاصيل المقرر والمحاضرات</a>
                </div>
            {% endfor %}
            <br><a href="/student" style="color:#475569; text-decoration:none;">&larr; العودة للرئيسية</a>
        </div>
    ''', materials=materials, current_user=current_user)

@app.route('/material/<int:mat_id>')
@login_required
def material_view(mat_id):
    material = Material.query.get_or_404(mat_id)
    lectures = Lecture.query.filter_by(material_id=mat_id).all()
    return render_template_string('''
        <div style="font-family:Tahoma; direction:rtl; padding:25px; max-width:800px; margin:auto;">
            <h2 style="color:#0f172a;">مقرر: {{ material.name }}</h2>
            <p style="color:#64748b;">{{ material.description }}</p>
            <hr>
            <h3>المحاضرات والمحتوى الأكاديمي المرتبط:</h3>
            {% if lectures %}
                <ul>
                    {% for lec in lectures %}
                        <li style="margin-bottom:10px;">
                            <b>الأسبوع {{ lec.week_number }}:</b> {{ lec.title }} 
                            <span style="color:#059669; font-size:13px;">({{ lec.date_time.strftime('%Y-%m-%d %H:%M') }})</span>
                            <br><a href="{{ lec.file_url }}" target="_blank" style="color:#0284c7; font-size:13px;">تحميل الملفات والمراجع المرتبطة</a>
                        </li>
                    {% endfor %}
                </ul>
            {% else %}
                <p style="color:#94a3b8;">جاري إضافة المحاضرات والملفات لهذا المقرر من قِبل المشرفين.</p>
            {% endif %}
            <br><a href="/student/plan" style="color:#0284c7; text-decoration:none;">&larr; العودة للمقررات</a>
        </div>
    ''', material=material, lectures=lectures)

@app.route('/student/smart-schedule')
@login_required
def smart_schedule():
    # جلب الجدول الذكي الخاص بالطالب
    schedule_items = SmartScheduleItem.query.filter_by(user_id=current_user.id).all()
    return render_template_string('''
        <div style="font-family:Tahoma; direction:rtl; padding:25px; max-width:800px; margin:auto;">
            <h2 style="color:#0284c7;">الجدول الذكي ونظام «ماذا أفعل الآن؟»</h2>
            <div style="background:#eff6ff; border-right:4px solid #3b82f6; padding:15px; margin-bottom:20px; border-radius:4px;">
                <h4 style="margin:0 0 5px 0; color:#1e40af;">المهمة الحالية المقترحة:</h4>
                <p style="margin:0; color:#1e3a8a;">مراجعة أحدث المحاضرات المضافة وتثبيت المواعيد الأسبوعية بدقة.</p>
            </div>
            <h3>جدولك الأسبوعي المدار تلقائياً:</h3>
            <table border="1" style="width:100%; border-collapse:collapse; text-align:right; background:white;">
                <tr style="background:#f1f5f9;">
                    <th style="padding:10px;">اليوم</th>
                    <th style="padding:10px;">الوقت</th>
                    <th style="padding:10px;">المهمة / المحاضرة</th>
                    <th style="padding:10px;">الحالة</th>
                </tr>
                {% for item in schedule_items %}
                <tr>
                    <td style="padding:10px;">{{ item.day_of_week }}</td>
                    <td style="padding:10px;">{{ item.time_slot }}</td>
                    <td style="padding:10px;">{{ item.title }}</td>
                    <td style="padding:10px; color:#059669;"><b>{{ item.status }}</b></td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="4" style="padding:15px; text-align:center; color:#64748b;">لا توجد مواعيد مضافة في جدولك حالياً.</td>
                </tr>
                {% endfor %}
            </table>
            <br><a href="/student" style="color:#0284c7; text-decoration:none;">&larr; العودة للوحة الطالب</a>
        </div>
    ''', schedule_items=schedule_items)
