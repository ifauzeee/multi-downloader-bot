<div align="center">
  <h1>Multi-Downloader Bot</h1>
  <p>
    <b>Bot Telegram serbaguna untuk mengunduh media dari berbagai platform sosial media langsung ke chat Anda.</b>
  </p>

  <p>
    <a href="https://github.com/ifauzeee/multi-downloader-bot/stargazers"><img src="https://img.shields.io/github/stars/ifauzeee/multi-downloader-bot?style=for-the-badge&color=ffd000" alt="Stars"></a>
    <a href="https://github.com/ifauzeee/multi-downloader-bot/issues"><img src="https://img.shields.io/github/issues/ifauzeee/multi-downloader-bot?style=for-the-badge&color=ff6252" alt="Issues"></a>
    <a href="https://github.com/ifauzeee/multi-downloader-bot/blob/main/LICENSE"><img src="https://img.shields.io/github/license/ifauzeee/multi-downloader-bot?style=for-the-badge&color=00aeff" alt="License"></a>
  </p>
</div>

---

## 📖 Tentang Proyek Ini

**Multi-Downloader Bot** adalah sebuah bot Telegram yang dirancang untuk menjadi asisten andal dalam mengunduh konten media dari internet. Dibuat dengan Python, bot ini mampu memproses link dari berbagai platform populer dan mengirimkan hasilnya langsung ke pengguna, baik dalam chat pribadi maupun grup.

Bot ini menggunakan `yt-dlp` dan `gallery-dl`, dua *powerful engine* di belakang layar, untuk memastikan kompatibilitas yang luas dan keandalan dalam mengunduh.

> **Ingin mencoba bot ini?**
>
> Anda bisa bergabung ke grup diskusi dan mencoba botnya langsung di sana:
>
> **[➡️ Join Ryzeeen Universe](https://t.me/RyzeeenUniverse)**

---

## ✨ Fitur Utama

- **Dukungan Multi-Platform**:
  - 🎬 **YouTube**: Unduh video dengan pilihan resolusi dan info ukuran file.
  - 📸 **Instagram**: Unduh foto, video, dan postingan *carousel* (galeri).
  - 🐦 **Twitter / X**: Unduh video dan gambar dari tweet.
  - 📘 **Facebook**: Unduh video dari postingan publik.
  - 🎵 **TikTok**: Unduh video tanpa *watermark*.
- **Antarmuka Interaktif**:
  - Tombol *inline* untuk memilih resolusi video YouTube.
  - Pesan status yang informatif (menganalisis, mengunduh, mengunggah).
- **Performa Tangguh**:
  - Didesain untuk berjalan 24/7 di server menggunakan **PM2**.
  - Auto-restart jika terjadi *crash* atau setelah server reboot.
- **Cerdas di Grup**:
  - Hanya merespons pesan yang berisi link, tidak mengganggu percakapan lain.
  - Mampu mengirim balasan di **topic** yang benar dalam grup.
- **Keamanan**:
  - Pembersihan file otomatis setelah berhasil diunggah untuk menghemat ruang disk.
  - Penanganan error yang baik untuk memberi tahu pengguna jika terjadi masalah.

---

## 🚀 Instalasi & Konfigurasi

Untuk menjalankan bot ini di server Anda (direkomendasikan Ubuntu/Debian):

### 1. **Clone Repositori**
```bash
git clone [https://github.com/ifauzeee/multi-downloader-bot.git](https://github.com/ifauzeee/multi-downloader-bot.git)
cd multi-downloader-bot
```

### 2. **Instal Kebutuhan**
Pastikan Anda memiliki Python 3.8+ dan Node.js.

- **Install library Python:**
  ```bash
  pip install -r requirements.txt
  ```
- **Install PM2 (Process Manager):**
  ```bash
  sudo npm install pm2 -g
  ```

### 3. **Buat File Konfigurasi**
Bot ini memerlukan beberapa file konfigurasi yang tidak termasuk dalam repositori demi keamanan.

- **Buat file `.env`** dan isi dengan token bot Anda:
  ```
  BOT_TOKEN="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
  ```
- **(Opsional) Buat file cookie** jika Anda perlu mengunduh konten privat. Ekspor cookie dari browser Anda setelah login ke situs terkait:
  - `yt_cookies.txt` (untuk YouTube)
  - `instagram.com_cookies.txt` (dideteksi otomatis oleh `gallery-dl`)

---

## ▶️ Menjalankan Bot

Gunakan PM2 untuk menjalankan bot di latar belakang dan memastikannya selalu hidup.

1.  **Mulai Bot:**
    ```bash
    pm2 start bot.py --name "multi-downloader" --interpreter python3
    ```

2.  **Simpan Proses agar Otomatis Berjalan saat Reboot:**
    ```bash
    pm2 startup
    # Salin dan jalankan perintah yang disarankan oleh PM2
    pm2 save
    ```

3.  **Perintah PM2 Berguna Lainnya:**
    - `pm2 list`: Melihat status semua aplikasi.
    - `pm2 logs multi-downloader`: Melihat log *real-time* dari bot.
    - `pm2 restart multi-downloader`: Me-restart bot (misalnya setelah mengubah kode).
    - `pm2 stop multi-downloader`: Menghentikan bot.

---

## 🛠️ Teknologi yang Digunakan

- **[Python](https://www.python.org/)**: Bahasa pemrograman utama.
- **[python-telegram-bot](https://python-telegram-bot.org/)**: Kerangka kerja untuk berinteraksi dengan API Telegram.
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)**: *Engine* utama untuk mengunduh video, khususnya dari YouTube.
- **[gallery-dl](https://github.com/gallery-dl/gallery-dl)**: *Engine* andal untuk mengunduh galeri gambar dan video dari sosial media.
- **[PM2](https://pm2.keymetrics.io/)**: Process manager untuk menjaga bot tetap berjalan di lingkungan produksi.

---

## 🤝 Kontribusi

Kontribusi, isu, dan permintaan fitur sangat diterima! Jangan ragu untuk membuat *issue* atau *pull request*.

1.  Fork Project
2.  Buat Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit Perubahan Anda (`git commit -m 'Add some AmazingFeature'`)
4.  Push ke Branch (`git push origin feature/AmazingFeature`)
5.  Buka sebuah Pull Request

---

## 📄 Lisensi

Didistribusikan di bawah Lisensi MIT. Lihat `LICENSE` untuk informasi lebih lanjut.

---

<div align="center">
  © All rights reserved - Muhammad Ibnu Fauzi
</div>
