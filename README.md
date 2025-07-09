# Telegram Multi-Downloader Bot

Bot Telegram serbaguna untuk mengunduh media dari berbagai platform sosial media. Bot ini dibuat untuk berjalan 24/7 di server dan dikelola menggunakan PM2.

## ✨ Fitur

- **YouTube Downloader**:
  - Ditenagai oleh `yt-dlp`.
  - Memberikan pilihan resolusi video.
  - Menampilkan perkiraan ukuran file.
  - Menggabungkan video dan audio secara otomatis untuk kualitas terbaik.
- **Social Media Downloader (Instagram, Twitter/X, Facebook, TikTok)**:
  - Ditenagai oleh `gallery-dl` untuk keandalan maksimal.
  - Mendukung unduhan foto, video, dan postingan galeri (carousel).
  - Penanganan error dan pembersihan file otomatis yang tangguh.
- **Fitur Bot**:
  - Berjalan di latar belakang menggunakan PM2.
  - Responsif di grup (hanya membalas link) dan di chat pribadi.
  - Dapat membalas di *topic* yang benar dalam grup.

## 🚀 Instalasi di Server

1.  **Clone repositori ini:**
    ```bash
    git clone [https://github.com/NAMA_ANDA/NAMA_REPO_ANDA.git](https://github.com/NAMA_ANDA/NAMA_REPO_ANDA.git)
    cd NAMA_REPO_ANDA
    ```

2.  **Instal semua library yang dibutuhkan:**
    ```bash
    pip install -r requirements.txt
    ```
    
3.  **Instal PM2 (jika belum ada):**
    ```bash
    sudo npm install pm2 -g
    ```

## ⚙️ Konfigurasi

Sebelum menjalankan bot, Anda perlu membuat file kredensial. **File-file ini tidak akan diunggah ke GitHub berkat `.gitignore`**.

1.  **Buat file `.env`** dan isi dengan token bot Anda:
    ```
    BOT_TOKEN="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    ```

2.  **(Opsional) Buat file cookie** jika diperlukan untuk mengakses konten privat:
    - `yt_cookies.txt` untuk YouTube.
    - `instagram.com_cookies.txt` untuk Instagram (dideteksi otomatis oleh `gallery-dl`).

## ▶️ Menjalankan Bot dengan PM2

1.  **Mulai bot:**
    Gunakan perintah ini untuk memulai bot di latar belakang dan memberinya nama.
    ```bash
    pm2 start bot.py --name "multi-downloader" --interpreter python3
    ```

2.  **Pastikan bot berjalan setelah reboot:**
    ```bash
    pm2 startup
    # Salin dan jalankan perintah yang diberikan oleh PM2
    pm2 save
    ```

3.  **Perintah Berguna Lainnya:**
    - `pm2 list`: Melihat status bot.
    - `pm2 logs multi-downloader`: Melihat log aktivitas/error.
    - `pm2 restart multi-downloader`: Me-restart bot setelah mengubah kode.
