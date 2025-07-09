import os
import asyncio
from dotenv import load_dotenv
import logging
import shutil
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
INFO_TIMEOUT = 60.0
DOWNLOAD_TIMEOUT = 600.0

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- SISTEM ANTRIAN & CACHE ---
download_queue = asyncio.Queue()
job_cache = {}
queue_ticket_counter = 0
counter_lock = asyncio.Lock()

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

def run_blocking_yt_dlp(opts, url):
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=False)

def run_blocking_yt_dlp_download(opts, url):
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

# --- HANDLER UTAMA ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '👋 Halo! Kirimkan saya link dari YouTube, Instagram, Twitter/X, Facebook, atau TikTok untuk diunduh.'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global queue_ticket_counter
    if not update.message or not update.message.text: return
    message_text = update.message.text.strip()
    if not message_text.lower().startswith('http'): return
    
    url = message_text
    job = {
        "type": "initial_link",
        "url": url,
        "chat_id": update.effective_chat.id,
        "message_thread_id": update.message.message_thread_id,
        "user_message_id": update.message.message_id,
        "context": context
    }
    
    async with counter_lock:
        queue_ticket_counter += 1
        ticket_number = queue_ticket_counter

    await download_queue.put(job)
    await update.message.reply_text(f"✅ Link Anda telah ditambahkan ke antrian (Tiket #{ticket_number}).")

# --- HANDLER TOMBOL (UNTUK YOUTUBE) ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global queue_ticket_counter
    query = update.callback_query; await query.answer()
    try:
        source, action, data = query.data.split('|', 2)
    except ValueError: return
    if source != 'yt': return

    chat_id = query.message.chat_id
    original_job_info = job_cache.get(chat_id)
    if not original_job_info:
        await query.edit_message_text('⚠️ Sesi telah berakhir, silakan kirim ulang link.')
        return
        
    new_job = {
        "type": f"yt_{action}",
        "url": original_job_info["url"],
        "title": original_job_info["title"],
        "format_id": data,
        "chat_id": chat_id,
        "message_thread_id": query.message.message_thread_id,
        "status_message": query.message,
        "context": context
    }

    async with counter_lock:
        queue_ticket_counter += 1
        ticket_number = queue_ticket_counter

    await download_queue.put(new_job)
    await query.edit_message_text(f"✅ Oke! Permintaan unduhan Anda ditambahkan ke antrian (Tiket #{ticket_number}).")
    if chat_id in job_cache:
        del job_cache[chat_id]

# --- PEKERJA ANTRIAN (QUEUE WORKER) ---
async def download_worker(app: Application):
    global queue_ticket_counter
    logger.info("Worker antrian dimulai...")
    while True:
        try:
            job = await download_queue.get()
            job_type = job.get("type")

            if job_type == "initial_link":
                await process_initial_link(job)
            elif job_type == "yt_video_dl":
                await process_youtube_video_download(job)
            elif job_type == "yt_audio_dl":
                await process_youtube_audio_download(job)
            
            async with counter_lock:
                if queue_ticket_counter > 0:
                    queue_ticket_counter -= 1
            
            download_queue.task_done()
        except Exception as e:
            logger.error(f"Error kritis di dalam worker: {e}")
            if 'job' in locals() and not download_queue.empty():
                download_queue.task_done()
            async with counter_lock:
                if queue_ticket_counter > 0:
                    queue_ticket_counter -= 1

# --- PROSESOR TUGAS ---
async def process_initial_link(job):
    url = job["url"]
    context = job["context"]
    chat_id = job["chat_id"]
    
    status_message = await context.bot.send_message(
        chat_id=chat_id, text="⏳ Memproses link Anda dari antrian...", reply_to_message_id=job["user_message_id"]
    )

    if 'youtube.com' in url or 'youtu.be' in url:
        # Langsung proses sebagai video tunggal
        await process_youtube_initial(status_message, context, job)
    elif any(domain in url for domain in ['instagram.com', 'twitter.com', 'x.com', 'facebook.com', 'fb.watch', 'tiktok.com']):
        platform = "Instagram"
        if "twitter.com" in url or "x.com" in url: platform = "Twitter/X"
        if "facebook.com" in url or "fb.watch" in url: platform = "Facebook"
        if "tiktok.com" in url: platform = "TikTok"
        await process_generic_link(status_message, context, job, platform)
    else:
        await status_message.edit_text('❌ Maaf, link dari situs tersebut belum didukung.')

async def process_generic_link(status_message, context, job, platform):
    chat_id = job["chat_id"]
    message_thread_id = job["message_thread_id"]
    url = job["url"]
    await status_message.edit_text(f'⏳ Mengunduh dari {platform}...')
    download_path = os.path.join(DOWNLOAD_DIR, f"gallery_{chat_id}_{status_message.message_id}")
    os.makedirs(download_path, exist_ok=True)
    command = ['gallery-dl', '-D', download_path, url]
    try:
        process = await asyncio.wait_for(asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE), timeout=DOWNLOAD_TIMEOUT)
        stdout, stderr = await process.communicate()
        if process.returncode != 0: raise RuntimeError(stderr.decode('utf-8', errors='ignore').strip())
        downloaded_files = os.listdir(download_path)
        if not downloaded_files: raise ValueError("Tidak ada file yang diunduh.")
        await status_message.edit_text(f'🚀 Mengunggah {len(downloaded_files)} media...')
        for filename in downloaded_files:
            file_path = os.path.join(download_path, filename)
            caption_text = os.path.basename(filename)
            if os.path.getsize(file_path) > MAX_FILE_SIZE:
                await context.bot.send_message(chat_id=chat_id, text=f"⚠️ Media '{filename}' terlalu besar.", message_thread_id=message_thread_id)
                continue
            with open(file_path, 'rb') as f:
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    await context.bot.send_photo(chat_id=chat_id, photo=f, caption=caption_text, message_thread_id=message_thread_id)
                else:
                    await context.bot.send_video(chat_id=chat_id, video=f, caption=caption_text, message_thread_id=message_thread_id)
        await status_message.delete()
    except asyncio.TimeoutError: await status_message.edit_text(f"❌ Waktu mengunduh dari {platform} habis.")
    except Exception as e:
        logger.error(f"Gagal download {platform}: {e}")
        await status_message.edit_text(f"❌ Gagal mengunduh dari {platform}.")
    finally:
        if os.path.isdir(download_path): shutil.rmtree(download_path)

async def process_youtube_initial(status_message, context, job):
    """Menganalisis link YouTube dan langsung menampilkan pilihan format."""
    url = job["url"]
    chat_id = job["chat_id"]
    ydl_opts = {'quiet': True, 'skip_download': True}
    if os.path.isfile(YT_COOKIES_FILE): ydl_opts['cookiefile'] = YT_COOKIES_FILE
    try:
        info = await asyncio.wait_for(asyncio.to_thread(run_blocking_yt_dlp, ydl_opts, url), timeout=INFO_TIMEOUT)
        job_cache[chat_id] = {"url": url, "title": info.get("title", "Video Tanpa Judul")}
        await show_youtube_format_options(status_message, url, info)
    except Exception as e:
        error_str = str(e)
        logger.error(f"Gagal mengambil info YouTube awal: {error_str}")
        if "429" in error_str or "Too Many Requests" in error_str:
            await status_message.edit_text('❌ Gagal: Terlalu banyak permintaan ke YouTube. Coba lagi nanti atau perbarui cookie.')
        else:
            await status_message.edit_text('❌ Gagal menganalisis link YouTube (Playlist Not Support).')

async def show_youtube_format_options(message, url, info):
    formats = [f for f in info.get('formats', []) if f.get('vcodec') != 'none' and f.get('acodec') == 'none' and f.get('ext') == 'mp4']
    if not formats: formats = [f for f in info.get('formats', []) if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4']
    if not formats:
        await message.edit_text('⚠️ Tidak ditemukan format video MP4 yang valid.'); return
    
    keyboard, added_resolutions = [], set()
    sorted_formats = sorted(formats, key=lambda x: x.get('height', 0), reverse=True)
    for f in sorted_formats:
        resolution = f.get('format_note') or f'{f.get("height")}p'
        if resolution in added_resolutions: continue
        added_resolutions.add(resolution)
        file_size = f.get('filesize') or f.get('filesize_approx')
        button_text = f"{resolution} ({format_size(file_size)})"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"yt|video_dl|{f['format_id']}")])
    keyboard.append([InlineKeyboardButton("🎶 Audio Saja (MP3)", callback_data="yt|audio_dl|none")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.edit_text(f'🎬 Silakan pilih resolusi video atau audio:\n\n*{info.get("title","Video")}*', reply_markup=reply_markup, parse_mode='Markdown')

async def process_youtube_video_download(job):
    status_message = job["status_message"]
    await status_message.edit_text(f'⏳ Mengunduh video "{job["title"]}"...')
    ydl_opts = {'format': f'{job["format_id"]}+bestaudio/best', 'merge_output_format': 'mp4', 'quiet': True}
    if os.path.isfile(YT_COOKIES_FILE): ydl_opts['cookiefile'] = YT_COOKIES_FILE
    await download_and_send_yt(job, ydl_opts)

async def process_youtube_audio_download(job):
    status_message = job["status_message"]
    await status_message.edit_text(f'⏳ Mengunduh audio (MP3) untuk "{job["title"]}"...')
    ydl_opts = {'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}], 'quiet': True}
    if os.path.isfile(YT_COOKIES_FILE): ydl_opts['cookiefile'] = YT_COOKIES_FILE
    await download_and_send_yt(job, ydl_opts, is_audio=True)

async def download_and_send_yt(job, ydl_opts, is_audio=False):
    status_message = job["status_message"]
    chat_id = job["chat_id"]
    download_path = os.path.join(DOWNLOAD_DIR, f"yt_{chat_id}_{status_message.message_id}")
    os.makedirs(download_path, exist_ok=True)
    try:
        ydl_opts['outtmpl'] = os.path.join(download_path, '%(title)s.%(ext)s')
        await asyncio.wait_for(asyncio.to_thread(run_blocking_yt_dlp_download, ydl_opts, job["url"]), timeout=DOWNLOAD_TIMEOUT)
        downloaded_files = os.listdir(download_path)
        if not downloaded_files: raise ValueError("Gagal menemukan file.")
        target_file_path = os.path.join(download_path, downloaded_files[0])
        if is_audio:
            for f in downloaded_files:
                if f.lower().endswith('.mp3'): target_file_path = os.path.join(download_path, f); break
        if os.path.getsize(target_file_path) > MAX_FILE_SIZE:
            await status_message.edit_text(f'⚠️ File terlalu besar (batas 50MB).'); return
        await status_message.edit_text('🚀 Mengunggah...')
        with open(target_file_path, 'rb') as f:
            if is_audio:
                await job["context"].bot.send_audio(chat_id=chat_id, audio=f, title=job["title"], message_thread_id=job["message_thread_id"])
            else:
                await job["context"].bot.send_document(chat_id=chat_id, document=f, caption=job["title"], message_thread_id=job["message_thread_id"])
        await status_message.delete()
    except Exception as e:
        logger.error(f"Gagal download/kirim YouTube: {e}")
        await status_message.edit_text('❌ Gagal memproses file YouTube.')
    finally:
        if os.path.isdir(download_path): shutil.rmtree(download_path)

# --- FUNGSI UTAMA & INISIALISASI ---
async def post_init_callback(application: Application):
    asyncio.create_task(download_worker(application))

def main():
    logger.info("Memulai bot...")
    app = Application.builder().token(TOKEN).post_init(post_init_callback).connect_timeout(30).read_timeout(30).write_timeout(30).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    logger.info("✅ Bot serbaguna dengan sistem antrian berjalan!")
    app.run_polling()

if __name__ == '__main__':
    main()
