# DramaBot - Deployment Guide

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t dramabot:latest .
```

### Run with Docker

```bash
# Create .env file first
cp sample.env .env
# Edit .env dengan credentials Anda

# Run container
docker run -d \
  --name dramabot \
  --env-file .env \
  --restart unless-stopped \
  dramabot:latest
```

### View Logs

```bash
docker logs -f dramabot
```

### Stop & Remove

```bash
docker stop dramabot
docker rm dramabot
```

---

## 🚀 Heroku Deployment

### Method 1: Deploy Button

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

### Method 2: Heroku CLI

```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-dramabot

# Set stack to container
heroku stack:set container -a your-dramabot

# Set environment variables
heroku config:set API_ID=your_api_id -a your-dramabot
heroku config:set API_HASH=your_api_hash -a your-dramabot
heroku config:set BOT_TOKEN=your_bot_token -a your-dramabot
heroku config:set MONGO_URL=your_mongo_url -a your-dramabot
heroku config:set LOGGER_ID=your_logger_id -a your-dramabot
heroku config:set OWNER_ID=your_owner_id -a your-dramabot
heroku config:set SESSION=your_session_string -a your-dramabot

# Deploy
git push heroku main
```

---

## 📦 Manual Deployment (VPS)

### 1. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+
sudo apt install python3 python3-pip -y

# Install FFmpeg
sudo apt install ffmpeg -y
```

### 2. Clone & Setup

```bash
# Clone repository
git clone https://github.com/yourusername/dramabot.git
cd dramabot

# Install Python dependencies
pip3 install -r requirements.txt

# Setup environment
cp sample.env .env
nano .env  # Edit dengan credentials Anda
```

### 3. Generate Session String

```bash
python3 -c "from pyrogram import Client; Client(':memory:', api_id=YOUR_API_ID, api_hash='YOUR_API_HASH').start()"
# Follow prompts and copy session string
```

### 4. Run Bot

```bash
# Run directly
python3 -m drama

# Or use screen/tmux for persistent session
screen -S dramabot
python3 -m drama
# Press Ctrl+A then D to detach
```

### 5. Create Systemd Service (Recommended)

```bash
sudo nano /etc/systemd/system/dramabot.service
```

Paste configuration:

```ini
[Unit]
Description=DramaBot - Telegram Drama Streaming
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/dramabot
ExecStart=/usr/bin/python3 -m drama
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable & start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable dramabot
sudo systemctl start dramabot

# Check status
sudo systemctl status dramabot

# View logs
sudo journalctl -u dramabot -f
```

---

## 🔧 Environment Variables

Required:
- `API_ID` - From https://my.telegram.org
- `API_HASH` - From https://my.telegram.org
- `BOT_TOKEN` - From @BotFather
- `MONGO_URL` - MongoDB connection string
- `LOGGER_ID` - Log channel/group ID
- `OWNER_ID` - Your Telegram user ID
- `SESSION` - Pyrogram session string

Optional:
- `SESSION2`, `SESSION3` - Additional userbot sessions
- `SUPPORT_CHAT` - Support chat link
- `SUPPORT_CHANNEL` - Channel link
- `QUEUE_LIMIT` - Max queue size (default: 20)
- `VIDEO_PLAY` - Enable video (default: True)

---

## 📝 Post-Deployment

1. **Add Bot to Group:**
   - Add bot to your Telegram group
   - Promote as admin with voice chat permissions

2. **Test Commands:**
   - `/start` - Check if bot responds
   - `/ping` - Check bot status
   - `/trending` - Test API connectivity

3. **Monitor Logs:**
   - Check for errors
   - Verify API calls working
   - Test voice chat streaming

---

## 🐛 Troubleshooting

**Bot Not Starting:**
- Check all environment variables set correctly
- Verify MongoDB connection
- Check session string validity

**API Errors:**
- Verify DramaBox API is accessible
- Check network connectivity
- Review error logs

**Streaming Issues:**
- Ensure FFmpeg installed
- Check voice chat permissions
- Verify userbot in group

---

## 💡 Tips

- Use multiple SESSION strings for load balancing
- Monitor MongoDB storage usage
- Keep logs for debugging
- Regular bot updates recommended

