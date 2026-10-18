import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from aiohttp import web
import yt_dlp

# خادم الويب الخاص بمنصة Render للتثبيت المجاني
async def handle(request):
    return web.Response(text="Bot is running!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# دالة الترحيب عند بدء البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! أرسل لي رابط الفيديو وسأقوم بتحميله لك فوراً.")

# دالة التحميل مع yt-dlp
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"):
        return

    await update.message.reply_text("جاري تحميل الفيديو، انتظر قليلاً...")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        if os.path.exists('video.mp4'):
            await update.message.reply_video(video=open('video.mp4', 'rb'))
            os.remove('video.mp4')
        else:
            await update.message.reply_text("حدث خطأ أثناء تحميل الفيديو.")
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {e}")

async def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("Error: BOT_TOKEN is not set")
        return

    application = ApplicationBuilder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_video))

    # تشغيل خادم الويب ثم البوت
    await web_server()
    print("Bot and Web Server are starting...")
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
