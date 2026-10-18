import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f"أهلاً بك {user.mention_html()}! أرسل لي رابط فيديو وسأقوم بتحميله لك."
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    if not url.startswith("http"):
        return

    status = await update.message.reply_text("⏳ جارٍ تنزيل الفيديو، انتظر قليلًا...")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        await update.message.reply_video(video=open('video.mp4', 'rb'))
        
        if os.path.exists('video.mp4'):
            os.remove('video.mp4')
            
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء التنزيل: {e}")

def main() -> None:
    TOKEN = os.getenv("BOT_TOKEN")
    
    if not TOKEN:
        print("Error: BOT_TOKEN is not set!")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    application.run_polling()

if __name__ == "__main__":
    main()
