# راهنمای انتشار روی ابر (Render)

این پوشه برای انتشار روی سرویس ابری آماده شده است. سرور توسعه‌ی Flask با **gunicorn** (سرور WSGI تولیدی) جایگزین شده و فایل‌های لازم موجودند:

| فایل | کاربرد |
|---|---|
| `requirements.txt` | کتابخانه‌ها (شامل gunicorn) |
| `Procfile` | دستور اجرا (`gunicorn app:app`) |
| `render.yaml` | تنظیمات آماده برای Render (Blueprint) |
| `.python-version` | نسخه‌ی پایتون (۳.۱۲.۸) |
| `Dockerfile` | برای سرویس‌های مبتنی بر کانتینر (Cloud Run، Azure، AWS، Fly.io) |
| `/health` | مسیر بررسی سلامت سرویس |

## مراحل با Render و GitHub
1. در github.com حساب بساز و یک **New repository** بساز (مثلاً `medical-ai-demo`).
2. در صفحه‌ی مخزن: **Add file ← Upload files**؛ همه‌ی فایل‌ها و پوشه‌های داخل `medical_ai_project` را (نه خود پوشه را) بکش و رها کن، سپس **Commit changes**. فایل‌های مخفی مثل `.python-version` را هم حتماً اضافه کن.
3. در render.com با همان حساب GitHub وارد شو.
4. **New ← Blueprint** را بزن، مخزن را انتخاب کن و تأیید کن (تنظیمات از `render.yaml` خوانده می‌شود).
   اگر Blueprint نخواستی: **New ← Web Service**، مخزن را انتخاب کن و این مقادیر را بزن:
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
   - Instance Type: **Free**
   - Environment: `PYTHON_VERSION` = `3.12.8`
5. چند دقیقه صبر کن تا ساخت و اجرا تمام شود. آدرس نهایی شبیه `https://medical-ai-demo.onrender.com` است.
6. بررسی: آدرس را باز کن و `/health` را هم امتحان کن؛ باید `{"status":"ok"}` ببینی.

## نکته‌های پلن رایگان
- سرویس رایگان بعد از ۱۵ دقیقه بی‌استفاده بودن به خواب می‌رود و اولین درخواست بعدی چند ده ثانیه طول می‌کشد. قبل از ارائه یک بار صفحه را باز کن.
- فایل‌های نوشته‌شده روی دیسک ماندگار نیستند (این پروژه چیزی ذخیره نمی‌کند، پس مشکلی نیست).

## اجرای کانتینری (اختیاری)
```
docker build -t medical-ai .
docker run -p 8080:8080 medical-ai
```
سپس `http://localhost:8080` را باز کن. همین ایمیج را می‌توان روی Google Cloud Run، Azure Container Apps، AWS App Runner یا Fly.io اجرا کرد.
