# Hakim Leave / Request System
نظام مستقل لتسجيل طلبات الإجازة/الغياب والتحقق منها.

## التشغيل
pip install -r requirements.txt
uvicorn app.main:app --reload

## المسارات
/lookup — استعلام الطالب
/verify/{token} — التحقق عبر QR
/admin/dashboard — لوحة المشرف
/admin/requests/new — إنشاء طلب

ملاحظة: النظام يثبت تسجيل الطلب داخل منصة حكيم ولا يمثل إجازة أو تقريرًا طبيًا رسميًا.
