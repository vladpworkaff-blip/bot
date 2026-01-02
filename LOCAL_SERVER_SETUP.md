# Local Telegram Bot API Server Setup

This guide shows how to bypass the 50 MB upload limit by running your own Telegram Bot API server locally using Docker.

## Why Use Local Server?

- **Default Telegram Bot API**: 50 MB file upload limit
- **Local Bot API Server**: 2 GB file upload limit (without compression!)

## Prerequisites

1. **Docker Desktop** installed on Windows
   - Download from: https://www.docker.com/products/docker-desktop/
   - Install and restart your computer

2. **Telegram API Credentials**
   - You need `API_ID` and `API_HASH` from https://my.telegram.org

## Step 1: Get Telegram API Credentials

1. Go to https://my.telegram.org
2. Log in with your phone number
3. Click "API development tools"
4. Fill out the form:
   - **App title**: Video Parser Bot
   - **Short name**: videobot
   - **Platform**: Other
5. Click "Create application"
6. Copy your **App api_id** and **App api_hash**

## Step 2: Configure Environment Variables

Edit your `.env` file and add:

```env
# Telegram API Credentials
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=your_api_hash_here

# Enable local server
LOCAL_BOT_API_SERVER=http://localhost:8081
```

## Step 3: Start the Local Bot API Server

**IMPORTANT**: Before running the bot with the local server, you MUST start the Docker container first!

Open terminal in the project directory and run:

```bash
docker-compose up -d
```

This will:
- Download the Telegram Bot API Docker image
- Start the server on port 8081
- Create a persistent volume for data

Wait 10-20 seconds for the server to fully start, then verify it's running:

```bash
docker logs telegram-bot-api
```

You should see logs indicating the server is ready.

## Step 4: Verify Server is Running

Check if the container is running:

```bash
docker ps
```

You should see `telegram-bot-api` in the list.

Check logs:

```bash
docker logs telegram-bot-api
```

## Step 5: Run Your Bot

Now run your video parser bot as normal:

```bash
python video_parser_bot.py
```

You should see in the logs:
```
Using local Bot API server: http://localhost:8081
Max file size: 2000 MB (2 GB limit)
```

## Testing Large File Upload

The bot will now be able to upload files up to 2 GB without compression!

Example output:
```
INFO - Video size: 159.64 MB
INFO - Preparing to upload file (159.64 MB) to Telegram
INFO - Uploading video (159.64 MB)...
INFO - Video uploaded successfully to Telegram
```

## Managing the Docker Container

**Stop the server:**
```bash
docker-compose down
```

**Restart the server:**
```bash
docker-compose restart
```

**View logs:**
```bash
docker logs -f telegram-bot-api
```

**Remove everything (including data):**
```bash
docker-compose down -v
```

## Troubleshooting

### Error: "Cannot connect to local server"

1. Check if Docker is running:
   ```bash
   docker ps
   ```

2. Check container logs:
   ```bash
   docker logs telegram-bot-api
   ```

3. Verify the server is listening on port 8081:
   ```bash
   curl http://localhost:8081
   ```

### Error: "Invalid API_ID or API_HASH"

- Double-check your credentials at https://my.telegram.org
- Make sure you copied them correctly to `.env`
- Restart the Docker container:
  ```bash
  docker-compose restart
  ```

### Port 8081 already in use

Edit `docker-compose.yml` and change the port:
```yaml
ports:
  - "8082:8081"  # Use 8082 instead
```

Then update `.env`:
```env
LOCAL_BOT_API_SERVER=http://localhost:8082
```

### Files still failing to upload

1. Check file size limit:
   - Local server supports up to 2 GB
   - If file is >2 GB, it will still fail

2. Check timeout settings in `video_parser_bot.py`:
   - Increase `read_timeout`, `write_timeout`, `connect_timeout` if needed

3. Check Docker container resources:
   - Open Docker Desktop → Settings → Resources
   - Increase memory limit if needed

## Performance Notes

- **Upload speed**: Depends on your internet connection
- **First upload**: May take longer while the local server authenticates
- **Subsequent uploads**: Much faster
- **159 MB file**: Typically uploads in 2-5 minutes (depending on connection)

## Security

- The local server runs only on `localhost` (127.0.0.1)
- It's not accessible from the internet
- Data is stored in a Docker volume: `telegram-bot-api-data`
- To backup data, export the Docker volume

## Switching Back to Default Telegram Servers

To go back to the 50 MB limit (without local server):

1. Edit `.env`:
   ```env
   LOCAL_BOT_API_SERVER=
   ```

2. Stop the Docker container:
   ```bash
   docker-compose down
   ```

The bot will automatically use default Telegram servers (50 MB limit).

## Additional Resources

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api#using-a-local-bot-api-server)
- [aiogram/telegram-bot-api Docker Image](https://github.com/aiogram/telegram-bot-api)
- [How to bypass Telegram bot 50 MB file limit](https://medium.com/@khudoyshukur/how-to-bypass-telegram-bot-50-mb-file-limit-3a4d9b1788ae)
- [How I Self-Hosted the Telegram Bot API with Docker](https://dev.to/joybtw/how-i-self-hosted-the-telegram-bot-api-with-docker-to-bypass-50mb-upload-limits-483a)
