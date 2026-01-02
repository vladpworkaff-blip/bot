# Quick Start: Local Bot API Server

## Prerequisites Check

Before starting, make sure you have:

1. ✅ Docker Desktop installed and running
2. ✅ API_ID and API_HASH in your `.env` file
3. ✅ LOCAL_BOT_API_SERVER set to `http://localhost:8081` in `.env`

## Start the Local Server

### Step 1: Start Docker Container

```bash
docker-compose up -d
```

**What this does:**
- Downloads `aiogram/telegram-bot-api` image (first time only)
- Starts the container in background (`-d` = detached mode)
- Creates persistent storage for Telegram data

### Step 2: Verify It's Running

```bash
docker ps
```

You should see:
```
CONTAINER ID   IMAGE                              STATUS         PORTS
xxxxx          aiogram/telegram-bot-api:latest    Up 10 seconds  0.0.0.0:8081->8081/tcp
```

### Step 3: Check Logs (Optional)

```bash
docker logs telegram-bot-api
```

Wait for this message:
```
Server is listening on port 8081
```

### Step 4: Run Your Bot

```bash
python video_parser_bot.py
```

Expected output:
```
INFO - Using local Bot API server: http://localhost:8081
INFO - Max file size: 2000 MB (2 GB limit)
INFO - Bot started successfully!
```

## Common Issues

### Issue: "Cannot connect to Docker daemon"

**Solution:**
- Open Docker Desktop application
- Wait for it to fully start (green icon in system tray)
- Try again

### Issue: "Port 8081 is already in use"

**Solution 1** - Stop existing container:
```bash
docker stop telegram-bot-api
docker rm telegram-bot-api
docker-compose up -d
```

**Solution 2** - Use different port:
1. Edit `docker-compose.yml`:
   ```yaml
   ports:
     - "8082:8081"
   ```
2. Edit `.env`:
   ```env
   LOCAL_BOT_API_SERVER=http://localhost:8082
   ```
3. Restart:
   ```bash
   docker-compose up -d
   ```

### Issue: "Invalid API_ID or API_HASH"

**Check your credentials:**
```bash
docker logs telegram-bot-api
```

If you see authentication errors:
1. Go to https://my.telegram.org
2. Verify your API_ID and API_HASH
3. Update `.env` file
4. Restart container:
   ```bash
   docker-compose restart
   ```

### Issue: Bot still shows "50 MB limit"

**This means the local server isn't being used.**

Check:
1. Is Docker container running? `docker ps`
2. Is `LOCAL_BOT_API_SERVER` set in `.env`?
3. Did you restart the bot after editing `.env`?

## Stop the Local Server

When you're done or want to stop the server:

```bash
docker-compose down
```

To also remove stored data:
```bash
docker-compose down -v
```

## Daily Usage

Once everything is set up, you only need:

1. **Start Docker Desktop** (if not already running)
2. **Start container:**
   ```bash
   docker-compose up -d
   ```
3. **Run bot:**
   ```bash
   python video_parser_bot.py
   ```

That's it! The bot will now upload files up to 2 GB without compression.

## Monitoring

**View real-time logs:**
```bash
docker logs -f telegram-bot-api
```

**Check container status:**
```bash
docker ps -a
```

**Restart if needed:**
```bash
docker-compose restart
```
