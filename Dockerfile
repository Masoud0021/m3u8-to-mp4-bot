# استفاده از ایمیج پایه پایتون سبک
FROM python:3.10-slim

# بروزرسانی و نصب ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# تعیین دایرکتوری کاری
WORKDIR /app

# کپی فایل requirements و نصب پکیج‌ها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کل پروژه
COPY . .

# اجرای ربات
CMD ["python3", "bot.py"]
