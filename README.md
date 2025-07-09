<div align="center">
  <h1>Zee Downloader Bot</h1>
  <p>
    <b>Bot Telegram serbaguna dan tangguh untuk mengunduh media dari berbagai platform sosial media, dibangun dengan sistem antrian untuk stabilitas maksimal.</b>
  </p>
  <p>
    <a href="https://github.com/ifauzeee/zee-downloader-bot/stargazers"><img src="https://img.shields.io/github/stars/ifauzeee/zee-downloader-bot?style=for-the-badge&color=ffd000" alt="Stars"></a>
    <a href="https://github.com/ifauzeee/zee-downloader-bot/issues"><img src="https://img.shields.io/github/issues/ifauzeee/zee-downloader-bot?style=for-the-badge&color=ff6252" alt="Issues"></a>
    <a href="https://github.com/ifauzeee/zee-downloader-bot/blob/main/LICENSE"><img src="https://img.shields.io/github/license/ifauzeee/zee-downloader-bot?style=for-the-badge&color=00aeff" alt="License"></a>
  </p>
</div>

---

## 📖 Tentang Proyek Ini

**Zee Downloader Bot** adalah sebuah bot Telegram yang dirancang untuk menjadi asisten andal dalam mengunduh konten media dari internet. Dibuat dengan Python, bot ini mampu memproses link dari berbagai platform populer dan mengirimkan hasilnya langsung ke pengguna.

Fitur utamanya adalah **sistem antrian (queue)** yang memastikan setiap permintaan diproses satu per satu. Hal ini membuat bot sangat stabil, adil bagi semua pengguna, dan mencegah server dari kelebihan beban atau diblokir oleh platform tujuan.

> **Ingin mencoba bot ini?**
>
> Anda bisa bergabung ke grup diskusi dan mencoba botnya langsung di sana:
>
> **[➡️ Join Ryzeeen Universe](https://t.me/RyzeeenUniverse)**

---

## ✨ Fitur Utama

- **Dukungan Multi-Platform**:
  - 🎬 **YouTube**: Unduh video atau audio (MP3) dengan pilihan resolusi dan info ukuran file.
  - 📸 **Instagram**: Unduh foto, video, dan postingan *carousel* (galeri).
  - 🐦 **Twitter / X**: Unduh video dan gambar dari tweet.
  - 📘 **Facebook**: Unduh video dari postingan publik.
  - 🎵 **TikTok**: Unduh video tanpa *watermark*.
- **Sistem Antrian Cerdas**:
  - Setiap link yang masuk akan diproses secara berurutan, mencegah *server overload*.
  - Memberi notifikasi "tiket" kepada pengguna agar tahu permintaannya sudah diterima.
- **Performa Tangguh**:
  - Didesain untuk berjalan 24/7 di server menggunakan **PM2**.
  - Penanganan proses *blocking* dan *timeout* untuk mencegah bot "tergantung" atau *hang*.
- **Cerdas di Grup**:
  - Hanya merespons pesan yang berisi link.
  - Mampu mengirim balasan di **topic** yang benar dalam grup.

---

## 🚀 Instalasi & Konfigurasi

Untuk menjalankan bot ini di server Anda (direkomendasikan Ubuntu/Debian):

### 1. **Clone Repositori**
```bash
git clone https://github.com/ifauzeee/multi-downloader-bot.git
cd multi-downloader-bot
```

### 2. **Instal Kebutuhan**
- **Install library Python:**
  ```bash
  pip install -r requirements.txt
  ```
- **Install PM2 (Process Manager):**
  ```bash
  sudo npm install pm2 -g
  ```

### 3. **Buat File Konfigurasi**
- **Buat file `.env`** dan isi dengan token bot Anda:
  ```
  BOT_TOKEN="TOKEN_BOT_ANDA_DI_SINI"
  ```
- **(Opsional) Buat file cookie**: `yt_cookies.txt` untuk YouTube jika diperlukan.

---

## ▶️ Menjalankan Bot

Gunakan PM2 untuk menjalankan bot di latar belakang.

1.  **Mulai Bot:**
    ```bash
    pm2 start bot.py --name "zee-downloader" --interpreter python3
    ```

2.  **Simpan Proses agar Otomatis Berjalan saat Reboot:**
    ```bash
    pm2 startup
    # Salin dan jalankan perintah yang disarankan oleh PM2
    pm2 save
    ```

---

## 🛠️ Teknologi yang Digunakan

- **Python** & **asyncio**
- **python-telegram-bot**
- **yt-dlp** & **gallery-dl**
- **PM2**

---

<div align="center">
  © All rights reserved - Muhammad Ibnu Fauzi
</div>
