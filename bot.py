import os
import subprocess
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
DOWNLOAD_FOLDER = "videos"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

GOFILE_API = "https://api.gofile.io/uploadFile"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک m3u8 رو بفرست تا برات تبدیل به mp4 کنم و هم فایل بفرستم، هم لینک مستقیم دانلود.")

async def handle_m3u8(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    filename = f"{chat_id}.mp4"
    video_path = os.path.join(DOWNLOAD_FOLDER, filename)

    await update.message.reply_text("🚀 درحال دانلود و تبدیل... لطفاً صبر کن.")

    try:
        subprocess.run(["ffmpeg", "-i", url, "-preset", "fast", "-c", "copy", video_path], check=True)

        with open(video_path, 'rb') as f:
            files = {'file': (filename, f)}
            response = requests.post(GOFILE_API, files=files)
            data = response.json()

        if data["status"] == "ok":
            download_link = data["data"]["downloadPage"]
            await update.message.reply_video(video=open(video_path, 'rb'), caption=f"✅ تبدیل شد!\n🔗 لینک دانلود: {download_link}")
        else:
            await update.message.reply_text("❌ خطا در آپلود به GoFile")

        os.remove(video_path)

    except Exception as e:
        await update.message.reply_text(f"❌ خطا در تبدیل یا آپلود: {e}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_m3u8))
app.run_polling()
