# Installing FFmpeg on Windows

FFmpeg is required for video compression. Follow these steps to install it:

## Method 1: Using Chocolatey (Recommended - Easiest)

1. **Install Chocolatey** (if not already installed):
   - Open PowerShell as Administrator
   - Run:
     ```powershell
     Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
     ```

2. **Install FFmpeg**:
   ```powershell
   choco install ffmpeg
   ```

3. **Verify installation**:
   ```bash
   ffmpeg -version
   ```

## Method 2: Manual Installation

1. **Download FFmpeg**:
   - Go to [ffmpeg.org](https://ffmpeg.org/download.html#build-windows)
   - Click "Windows builds from gyan.dev"
   - Download "ffmpeg-release-essentials.zip"

2. **Extract the archive**:
   - Extract to `C:\ffmpeg` (or any location you prefer)

3. **Add to PATH**:
   - Open "Environment Variables":
     - Press `Win + X` → System → Advanced system settings → Environment Variables
   - Under "System variables", find and select "Path" → Click "Edit"
   - Click "New" and add: `C:\ffmpeg\bin`
   - Click "OK" on all dialogs

4. **Verify installation**:
   - Open a **new** Command Prompt or PowerShell window
   - Run:
     ```bash
     ffmpeg -version
     ```
   - You should see FFmpeg version information

## Method 3: Using Scoop

1. **Install Scoop** (if not already installed):
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   irm get.scoop.sh | iex
   ```

2. **Install FFmpeg**:
   ```bash
   scoop install ffmpeg
   ```

3. **Verify installation**:
   ```bash
   ffmpeg -version
   ```

## Troubleshooting

**"ffmpeg is not recognized" error:**
- Make sure you added FFmpeg to PATH (Method 2, step 3)
- Open a **NEW** terminal window after adding to PATH
- Restart your computer if the issue persists

**Permission denied:**
- Run Command Prompt or PowerShell as Administrator
- Make sure antivirus isn't blocking FFmpeg

**Still not working?**
- Check if `ffmpeg.exe` exists in `C:\ffmpeg\bin\`
- Try running FFmpeg with full path: `C:\ffmpeg\bin\ffmpeg.exe -version`
- If this works, your PATH is not configured correctly

## Next Steps

After installing FFmpeg:
1. Verify it's working: `ffmpeg -version`
2. Run the bot: `python video_parser_bot.py`
3. The bot will automatically compress videos >50 MB before uploading to Telegram
