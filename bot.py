import os
import subprocess
import asyncio
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
DOWNLOAD_FOLDER = "videos"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

GOFILE_API = "https://api.gofile.io/uploadFile"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! لینک m3u8 یا اینستاگرام رو بفرست تا برات دانلود و تبدیل کنم."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id

    if "instagram.com" in url:
        await download_instagram_video(update, url, chat_id)
    elif url.endswith(".m3u8"):
        await download_m3u8_video(update, url, chat_id)
    else:
        await update.message.reply_text("لینک معتبر نیست یا پشتیبانی نمیشه.")

async def download_instagram_video(update, url, chat_id):
    msg = await update.message.reply_text("🚀 شروع دانلود ویدیو اینستاگرام...")

    output_path = os.path.join(DOWNLOAD_FOLDER, f"{chat_id}_insta.mp4")

    cmd = [
        "yt-dlp",
        "-f",
        "mp4",
        "-o",
        output_path,
        url,
    ]

    proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    while True:
        line = await proc.stderr.readline()
        if not line:
            break
        # می‌تونی اینجا پیشرفت رو parse کنی و پیام ویرایش کنی

    await proc.wait()

    if proc.returncode != 0:
        await msg.edit_text("❌ خطا در دانلود ویدیو اینستاگرام.")
        return

    await msg.edit_text("✅ دانلود انجام شد! در حال آپلود فایل...")

    try:
        with open(output_path, "rb") as f:
            files = {"file": (f"{chat_id}_insta.mp4", f)}
            response = requests.post(GOFILE_API, files=files)
            data = response.json()

        if data["status"] == "ok":
            download_link = data["data"]["downloadPage"]
            await update.message.reply_video(video=open(output_path, "rb"), caption=f"✅ دانلود شد!\n🔗 لینک دانلود: {download_link}")
        else:
            await update.message.reply_text("❌ خطا در آپلود به GoFile")

    except Exception as e:
        await update.message.reply_text(f"❌ خطا در آپلود: {e}")

    finally:
        if os.path.exists(output_path):
            os.remove(output_path)

async def download_m3u8_video(update, url, chat_id):
    ts_path = os.path.join(DOWNLOAD_FOLDER, f"{chat_id}.ts")
    mp4_path = os.path.join(DOWNLOAD_FOLDER, f"{chat_id}.mp4")

    msg = await update.message.reply_text("🚀 شروع دانلود چند رشته‌ای...")

    # دانلود با aria2c (16 رشته)
    cmd_dl = [
        "aria2c",
        "-x", "16",
        "-s", "16",
        "-o", ts_path,
        url
    ]

    proc_dl = await asyncio.create_subprocess_exec(*cmd_dl, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    while True:
        line = await proc_dl.stderr.readline()
        if not line:
            break
        # می‌تونی اینجا پیشرفت دانلود رو parse کنی و پیام ویرایش کنی اگر خواستی
    await proc_dl.wait()

    if proc_dl.returncode != 0:
        await msg.edit_text("❌ خطا در دانلود فایل با aria2.")
        return

    await msg.edit_text("✅ دانلود تمام شد! شروع تبدیل سریع با ffmpeg...")

    # تبدیل سریع با ffmpeg -preset ultrafast
    cmd_ffmpeg = [
        "ffmpeg",
        "-i", ts_path,
        "-c", "copy",
        "-preset", "ultrafast",
        mp4_path
    ]

    proc_ff = await asyncio.create_subprocess_exec(*cmd_ffmpeg, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    while True:
        line = await proc_ff.stderr.readline()
        if not line:
            break
        # می‌تونی اینجا پیشرفت تبدیل رو extract کنی و به روز کنی
    await proc_ff.wait()

    if proc_ff.returncode != 0:
        await msg.edit_text("❌ خطا در تبدیل فایل با ffmpeg.")
        return

    await msg.edit_text("✅ تبدیل تمام شد! در حال آپلود فایل...")

    try:
        with open(mp4_path, 'rb') as f:
            files = {'file': (f"{chat_id}.mp4", f)}
            response = requests.post(GOFILE_API, files=files)
            data = response.json()

        if data["status"] == "ok":
            download_link = data["data"]["downloadPage"]
            await update.message.reply_video(video=open(mp4_path, 'rb'), caption=f"✅ تبدیل شد!\n🔗 لینک دانلود: {download_link}")
        else:
            await update.message.reply_text("❌ خطا در آپلود به GoFile")

    except Exception as e:
        await update.message.reply_text(f"❌ خطا در آپلود: {e}")

    finally:
        if os.path.exists(ts_path):
            os.remove(ts_path)
        if os.path.exists(mp4_path):
            os.remove(mp4_path)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
app.run_polling()
