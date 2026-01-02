# Quick Start Guide

## 1. Install FFmpeg

**Windows (using Chocolatey - easiest):**
```bash
choco install ffmpeg
```

**Or see [INSTALL_FFMPEG.md](INSTALL_FFMPEG.md) for other methods**

Verify:
```bash
ffmpeg -version
```

## 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## 3. Configure Bot

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
WEBSITE_URL=https://your-website.com
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=@your_channel
ADMIN_ID=your_chat_id
CHECK_INTERVAL=7200
```

### Getting Credentials:

**Bot Token:**
1. Message [@BotFather](https://t.me/botfather)
2. Send `/newbot`
3. Follow instructions
4. Copy the token

**Channel ID:**
- Public channel: `@channelname`
- Private channel: Forward a message to [@userinfobot](https://t.me/userinfobot)

**Admin ID (Your Chat ID):**
- Message [@userinfobot](https://t.me/userinfobot)
- Send any message
- Copy your ID

**Important:** Add your bot as channel admin with "Post Messages" permission!

## 4. Run the Bot

```bash
python video_parser_bot.py
```

## 5. First Run Behavior

- Bot will save the latest video ID **without processing it**
- Only **new videos after this** will be downloaded and uploaded
- You'll receive a startup message in your admin chat

## What Happens Next?

1. Bot checks for new videos every 2 hours (configurable)
2. Downloads new videos
3. **Compresses videos >50 MB** (using FFmpeg)
4. Uploads to your Telegram channel
5. Sends you status updates

## Compression Stats Example

```
🗜️ Compressing video
🆔 Video ID: 47408
📦 Original Size: 159.64 MB
⚙️ This may take 1-3 minutes...

✅ Video uploaded successfully!
🆔 Video ID: 47408
📦 Original: 159.64 MB → Compressed: 42.31 MB
📉 Reduction: 73.5%
```

## Adjusting Compression Quality

Edit line 32 in `video_parser_bot.py`:

```python
TARGET_BITRATE_KBPS = 800  # Default: good balance
```

- **Lower (500-600)**: Smaller files, lower quality
- **Higher (1000-1200)**: Better quality, larger files

## Troubleshooting

**Bot not sending to channel?**
- Make sure bot is channel admin
- Bot must have "Post Messages" permission
- Use `python test_telegram.py` to diagnose

**FFmpeg not found?**
- Install FFmpeg (see step 1)
- Make sure it's in your PATH
- Run `ffmpeg -version` to verify

**Videos still too large?**
- Reduce `TARGET_BITRATE_KBPS` to 600 or 500
- Very long videos need lower bitrates

**Need help?**
- Check [README.md](README.md) for detailed documentation
- Check [INSTALL_FFMPEG.md](INSTALL_FFMPEG.md) for FFmpeg installation help
