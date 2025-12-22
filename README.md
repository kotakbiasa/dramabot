# 🎬 DramaBot

Bot Telegram untuk streaming drama/series ke voice chat grup. Powered by **DramaBox API**.

## ✨ Fitur

- 📺 Streaming drama ke voice chat Telegram
- 🔥 Browse drama trending & terbaru
- 🔍 Cari drama favorit
- 📋 Queue management untuk episode
- ⚙️ Playback controls (pause/resume/skip/stop)
- 👥 Multi-session userbot support
- 🎬 Video streaming support

## 📋 Requirements

- Python 3.10+
- MongoDB
- Telegram API credentials
- Telegram Bot Token
- Telegram Userbot Session (minimal 1)

## 🚀 Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/dramabot.git
cd dramabot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Environment

Copy `sample.env` ke `.env` dan isi dengan credentials Anda:

```bash
cp sample.env .env
nano .env
```

Required variables:
- `API_ID` - Dapatkan dari https://my.telegram.org
- `API_HASH` - Dapatkan dari https://my.telegram.org
- `BOT_TOKEN` - Dapatkan dari [@BotFather](https://t.me/BotFather)
- `MONGO_URL` - MongoDB connection string
- `SESSION` - Pyrogram session string untuk userbot
- `LOGGER_ID` - Chat ID untuk logs (bisa private/group)
- `OWNER_ID` - Your Telegram user ID

Optional:
- `SESSION2`, `SESSION3` - Additional userbot sessions
- `SUPPORT_CHAT`, `SUPPORT_CHANNEL` - Support links

### 4. Generate Session String

```bash
python -m drama.core.userbot
```

### 5. Run Bot

```bash
python -m drama
```

## 📝 Commands

### Browse Drama
- `/trending` - Lihat drama trending
- `/latest` - Lihat drama terbaru  
- `/search <query>` - Cari drama

### Playback
- `/play <book_id> <episode>` - Play episode
- `/pause` - Pause playback
- `/resume` - Resume playback
- `/skip` - Skip ke episode berikutnya
- `/stop` - Stop dan clear queue

### Queue
- `/queue` - Lihat antrian episode

### Info & Settings
- `/ping` - Cek bot status
- `/settings` - Lihat pengaturan grup
- `/playmode` - Toggle admin-only mode
- `/delcmd` - Toggle auto delete commands

### Admin Commands
- `/auth <user>` - Authorize user
- `/unauth <user>` - Unauthorize user
- `/reload` - Reload admin cache

### Sudo Commands (Owner Only)
- `/stats` - Bot statistics
- `/active` - Active voice chats
- `/broadcast` - Broadcast message
- `/restart` - Restart bot
- `/addsudo <user>` - Add sudo user
- `/rmsudo <user>` - Remove sudo user
- `/blacklist <user>` - Blacklist user
- `/unblacklist <user>` - Remove from blacklist

## 🔧 Configuration

Edit `config.py` untuk custom configuration:

- `QUEUE_LIMIT` - Maximum queue size (default: 20)
- `AUTO_END` - Auto end when queue is empty
- `AUTO_LEAVE` - Auto leave after inactivity
- `VIDEO_PLAY` - Enable video streaming

## 🎯 Usage

1. Tambahkan bot ke grup Telegram Anda
2. Beri bot akses admin (untuk manage voice chat)
3. Start voice chat di grup
4. Browse drama dengan `/trending` atau `/latest`
5. Klik drama yang ingin ditonton
6. Enjoy streaming! 🍿

## 📊 Tech Stack

- [Pyrofork](https://github.com/Mayuri-Chan/pyrofork) - Telegram MTProto framework
- [Py-TgCalls](https://github.com/pytgcalls/pytgcalls) - Voice chat integration
- [MongoDB](https://www.mongodb.com/) - Database
- [DramaBox API](https://dramabox.sansekai.my.id/) - Drama streaming source

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License.

## ⚠️ Disclaimer

Bot ini dibuat untuk tujuan edukasi. Pastikan Anda memiliki hak untuk streaming konten yang Anda gunakan.

## 💬 Support

Jika ada pertanyaan atau issues, silakan buat issue di GitHub atau hubungi support channel.

---

**Made with ❤️ for drama lovers**
