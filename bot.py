import os
import asyncio
from dotenv import load_dotenv
import logging
import shutil
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)
import yt_dlp

# --- KONFIGURASI ---
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable belum diset di file .env!")

MAX_FILE_SIZE = 49 * 1024 * 1024
DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
YT_COOKIES_FILE = 'yt_cookies.txt'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
video_info_cache = {}

# --- FUNGSI BANTU ---
def format_size(size_bytes):
    if size_bytes is None: return "N/A"
    if size_bytes == 0: return "0 B"
    import math
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

# --- HANDLER UTAMA ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '👋 Halo! Kirimkan saya link dari YouTube, Instagram, Twitter/X, Facebook, atau TikTok untuk diunduh.'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    message_text = update.message.text.strip()
    if not message_text.lower().startswith('http'): return
    url = message_text
    
    if 'youtube.com' in url or 'youtu.be' in url:
        await handle_youtube_link(update, context, url)
    elif 'instagram.com/' in url:
        await handle_generic_link_with_gallery_dl(update, context, url, "Instagram")
    elif 'twitter.com/' in url or 'x.com/' in url:
        await handle_generic_link_with_gallery_dl(update, context, url, "Twitter/X")
    elif 'facebook.com/' in url or 'fb.watch/' in url:
        await handle_generic_link_with_gallery_dl(update, context, url, "Facebook")
    elif 'tiktok.com/' in url:
        await handle_generic_link_with_gallery_dl(update, context, url, "TikTok")
    else:
        await update.message.reply_text('❌ Maaf, link dari situs tersebut belum didukung.')

# --- LOGIKA GENERIK DENGAN GALLERY-DL ---
async def handle_generic_link_with_gallery_dl(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, platform: str):
    chat_id = update.effective_chat.id
    message_thread_id = update.message.message_thread_id
    status_message = await update.message.reply_text(f'⏳ Mengunduh dari {platform}...')
    download_path = os.path.join(DOWNLOAD_DIR, f"gallery_{chat_id}_{update.message.message_id}")
    os.makedirs(download_path, exist_ok=True)
    command = ['gallery-dl', '-D', download_path, url]

    try:
        process = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            error_output = stderr.decode('utf-8', errors='ignore').strip()
            logger.error(f"gallery-dl gagal untuk {platform}: {error_output}")
            raise RuntimeError(f"Proses gallery-dl gagal")
        downloaded_files = os.listdir(download_path)
        if not downloaded_files: raise ValueError("Tidak ada file yang diunduh.")
        await status_message.edit_text(f'🚀 Mengunggah {len(downloaded_files)} media...')
        for filename in downloaded_files:
            file_path = os.path.join(download_path, filename)
            if os.path.getsize(file_path) > MAX_FILE_SIZE:
                await context.bot.send_message(chat_id=chat_id, text=f"⚠️ Media '{filename}' terlalu besar.", message_thread_id=message_thread_id)
                continue
            with open(file_path, 'rb') as f:
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    await context.bot.send_photo(chat_id=chat_id, photo=f, message_thread_id=message_thread_id)
                else:
                    await context.bot.send_video(chat_id=chat_id, video=f, message_thread_id=message_thread_id)
        await status_message.delete()
    except Exception as e:
        logger.error(f"Gagal download {platform} dengan gallery-dl: {e}")
        await status_message.edit_text(f"❌ Gagal mengunduh dari {platform}. Pastikan link publik.")
    finally:
        if os.path.isdir(download_path): shutil.rmtree(download_path)

# --- LOGIKA KHUSUS YOUTUBE ---
async def handle_youtube_link(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
    chat_id = update.effective_chat.id
    status_message = await update.message.reply_text('⏳ Menganalisis link YouTube...')
    ydl_opts = {'quiet': True, 'skip_download': True}
    if os.path.isfile(YT_COOKIES_FILE): ydl_opts['cookiefile'] = YT_COOKIES_FILE
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: info = ydl.extract_info(url, download=False)
        formats = [f for f in info.get('formats', []) if f.get('vcodec') != 'none' and f.get('acodec') == 'none' and f.get('ext') == 'mp4']
        if not formats: formats = [f for f in info.get('formats', []) if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4']
        if not formats:
            await status_message.edit_text('⚠️ Tidak ditemukan format video MP4 yang valid.'); return
        video_info_cache[chat_id] = {'url': url, 'title': info.get('title', 'Video'), 'formats': formats}
        keyboard, added_resolutions = [], set()
        sorted_formats = sorted(formats, key=lambda x: x.get('height', 0), reverse=True)
        for f in sorted_formats:
            resolution = f.get('format_note') or f'{f.get("height")}p'
            if resolution in added_resolutions: continue
            added_resolutions.add(resolution)
            file_size = f.get('filesize') or f.get('filesize_approx')
            button_text = f"{resolution} ({format_size(file_size)})"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"yt|{f['format_id']}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await status_message.edit_text(f'🎬 Silakan pilih resolusi untuk:\n\n*{info.get("title","Video")}*', reply_markup=reply_markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Gagal mengambil info YouTube: {e}")
        error_message = '❌ Gagal mengambil info video. Pastikan link benar dan publik.'
        if 'confirm you’re not a bot' in str(e): error_message += '\n\nPS: YouTube meminta verifikasi.'
        await status_message.edit_text(error_message)

# --- HANDLER TOMBOL (YOUTUBE) ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    source, format_id = query.data.split('|', 1)
    if source != 'yt': return
    chat_id = query.message.chat_id; status_message = query.message
    message_thread_id = query.message.message_thread_id
    if chat_id not in video_info_cache:
        await status_message.edit_text('⚠️ Sesi unduhan sudah kedaluwarsa.'); return
    info = video_info_cache[chat_id]; url, title = info['url'], info['title']
    
    # --- PERBAIKAN DI SINI ---
    # Membuat folder unik untuk unduhan YouTube
    download_path_yt = os.path.join(DOWNLOAD_DIR, f"yt_{chat_id}_{query.id}")
    os.makedirs(download_path_yt, exist_ok=True)

    try:
        await status_message.edit_text(f'⏳ Mengunduh "{title}"...')
        ydl_opts = {
            'outtmpl': os.path.join(download_path_yt, '%(title)s.%(ext)s'), # Simpan di folder unik
            'format': f'{format_id}+bestaudio/best',
            'merge_output_format': 'mp4',
            'quiet': True,
        }
        if os.path.isfile(YT_COOKIES_FILE): ydl_opts['cookiefile'] = YT_COOKIES_FILE
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        downloaded_files = os.listdir(download_path_yt)
        if not downloaded_files: raise ValueError("Gagal menemukan file setelah diunduh.")
        
        # Ambil file pertama dari folder unik
        downloaded_file = os.path.join(download_path_yt, downloaded_files[0])

        if os.path.getsize(downloaded_file) > MAX_FILE_SIZE:
            await status_message.edit_text('⚠️ Video terlalu besar untuk dikirim (batas 50MB).'); return

        await status_message.edit_text('🚀 Mengunggah ke Telegram...')
        with open(downloaded_file, 'rb') as f:
            await context.bot.send_document(chat_id=chat_id, document=f, message_thread_id=message_thread_id)
        await status_message.delete()
    except Exception as e:
        logger.error(f"Error saat download atau kirim file YouTube: {e}")
        await status_message.edit_text('❌ Gagal memproses video. Silakan coba lagi.')
    finally:
        # --- PERBAIKAN DI SINI ---
        # Selalu hapus folder unik beserta isinya, apa pun yang terjadi
        if os.path.isdir(download_path_yt): shutil.rmtree(download_path_yt)
        if chat_id in video_info_cache: del video_info_cache[chat_id]

# --- FUNGSI UTAMA ---
def main():
    logger.info("Memulai bot...")
    app = Application.builder().token(TOKEN).connect_timeout(30).read_timeout(30).write_timeout(30).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    logger.info("✅ Bot serbaguna berjalan!")
    app.run_polling()

if __name__ == '__main__':
    main()
