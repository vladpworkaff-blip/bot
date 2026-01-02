# Video Parser Telegram Bot

A bot that automatically parses new videos from a website and uploads them to your Telegram channel every 2-3 hours.

> **Quick Start:** See [QUICK_START.md](QUICK_START.md) for a step-by-step setup guide!

## Solution to the 50 MB Problem

The main challenge was that videos are 10-30 minutes long and exceed Telegram's 50 MB limit for bot API uploads.

**Solution Implemented:**
- Self-host **Local Telegram Bot API server** using Docker
- Bypasses the 50 MB limit → Upload files up to **2 GB**
- **No compression** - videos maintain original quality
- Automatic video metadata extraction (duration, resolution)
- Automatic thumbnail generation for video preview
- Videos display properly with duration and preview poster

## Features

- Automatically checks for new videos every 2-3 hours
- Parses video elements based on specific HTML structure
- Tracks last processed video ID to avoid duplicates
- **Uploads files up to 2 GB** without compression (using local Bot API server)
- **Automatic video metadata extraction** (duration, width, height)
- **Automatic thumbnail generation** for video preview/poster
- Videos display properly with duration and preview in Telegram
- Processes only the newest video on each check (one video every 2 hours)
- Automatic retry on failure
- Comprehensive logging

## Requirements

- Python 3.8+
- **Docker Desktop** (for uploading files >50 MB via local Bot API server)
- Telegram Bot Token
- Telegram Channel
- Telegram API credentials (API_ID and API_HASH from https://my.telegram.org)

## Installation

1. **Install Docker Desktop** (required for files >50 MB):
   - Download from https://www.docker.com/products/docker-desktop/
   - Install and restart your computer

2. Clone or download this repository

3. Install Python dependencies (includes OpenCV for video metadata extraction):
```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the example:
```bash
cp .env.example .env
```

5. Edit `.env` and configure your settings:
```env
WEBSITE_URL=https://your-website.com
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_CHANNEL_ID=@your_channel_username
ADMIN_ID=your_chat_id
CHECK_INTERVAL=7200
```

## Getting Telegram Credentials

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the instructions to set a name and username
4. Copy the **bot token** and paste it in `.env` as `TELEGRAM_BOT_TOKEN`

### 2. Create a Telegram Channel

1. Create a new channel in Telegram
2. Add your bot as an administrator to the channel
3. Use the channel username (with @) or chat ID in `.env` as `TELEGRAM_CHANNEL_ID`

## Usage

Run the bot:
```bash
python video_parser_bot.py
```

The bot will:
1. Check the website for new videos every 2-3 hours (configurable)
2. Download new videos
3. Automatically compress videos larger than 50 MB
4. Upload them to your Telegram channel
5. Save the last processed video ID to avoid duplicates

## How It Works

### Parsing Process

1. **Find video container**: Locates `ul.videos_ul` on the main page
2. **Find video blocks**: Gets all `li.video_block` elements
3. **Extract video IDs**: Stores IDs to prevent duplicate downloads
4. **Follow video links**: Clicks on `a.image` href to go to video page
5. **Extract video source**: Navigates `div.col_video` → `div.player-wrapper` → `video` tag and gets `src`
6. **Download video**: Downloads the video file
7. **Compress if needed**: If video > 50 MB, compress using FFmpeg with optimized settings
8. **Upload to Telegram**: Upload as video to your channel

### Video Compression Process

```python
if file_size_mb > 50:
    # Compress video using FFmpeg
    # H.264 codec, 800 kbps bitrate, AAC audio
    compress_video(input_path, output_path)
    upload_to_telegram(compressed_path)
else:
    # Upload original video (no compression needed)
    upload_to_telegram(original_path)
```

### Adjusting Compression Quality

Edit [video_parser_bot.py:32](video_parser_bot.py#L32) to change compression settings:

```python
TARGET_BITRATE_KBPS = 800  # Increase for better quality, decrease for smaller file size
```

**Bitrate recommendations:**
- `500-600 kbps`: Smaller files, acceptable quality
- `800 kbps` (default): Good balance of quality and size
- `1000-1200 kbps`: Better quality, larger files
- `1500+ kbps`: High quality, may still exceed 50 MB for long videos

## Configuration

Edit `.env` to customize:

- `WEBSITE_URL`: The website to parse videos from
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `TELEGRAM_CHANNEL_ID`: Your channel username or chat ID
- `CHECK_INTERVAL`: How often to check for new videos (in seconds)
  - Default: 7200 (2 hours)
  - For 3 hours: 10800

## Logs

The bot provides detailed logging:
- Video parsing status
- Download progress and file sizes
- **Compression statistics** (original size → compressed size, % reduction)
- Upload status
- Error messages
- Next check countdown

## Troubleshooting

**FFmpeg not found:**
- Error: `FFmpeg is not installed. Cannot compress video.`
- Solution: Install FFmpeg (see Installation section) and verify with `ffmpeg -version`
- Make sure FFmpeg is added to your system PATH

**Bot doesn't upload to channel:**
- Make sure the bot is an administrator of the channel
- Check that `TELEGRAM_CHANNEL_ID` is correct (use @ for public channels)
- Bot must have "Post Messages" permission

**Videos not found:**
- Verify the website URL is correct
- Check that the HTML structure matches the selectors in the code
- Review logs for parsing errors

**Compression takes too long:**
- Normal compression time: 1-3 minutes for a 10-30 minute video
- If it takes >10 minutes, it will timeout
- Try reducing `TARGET_BITRATE_KBPS` for faster compression

**Compressed video still too large:**
- Reduce `TARGET_BITRATE_KBPS` (e.g., from 800 to 600)
- Very long videos (>30 minutes) may need lower bitrates

**Video quality is poor:**
- Increase `TARGET_BITRATE_KBPS` (e.g., from 800 to 1000)
- Keep in mind this will increase file size

## License

MIT License
