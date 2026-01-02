import os
import time
import json
import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv
import logging
import cv2
from PIL import Image
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
WEBSITE_URL = os.getenv('WEBSITE_URL')  # Base URL of the website
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
ADMIN_ID = os.getenv('ADMIN_ID')  # Admin chat ID for status messages
LOCAL_BOT_API_SERVER = os.getenv('LOCAL_BOT_API_SERVER')  # Local Bot API server URL (optional)
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 7200))  # Default: 2 hours in seconds
LAST_VIDEO_ID_FILE = 'last_video_id.json'
MAX_VIDEO_SIZE_MB = 2000 if LOCAL_BOT_API_SERVER else 50  # 2GB with local server, 50MB with default

# Browser headers to bypass 403 Forbidden errors
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Referer': WEBSITE_URL if WEBSITE_URL else ''
}

class VideoParserBot:
    def __init__(self):
        # Initialize bot with local server if configured
        if LOCAL_BOT_API_SERVER:
            # Format: http://localhost:8081/bot{token} is constructed by the library
            # We just provide the base URL without /bot path
            base_url = LOCAL_BOT_API_SERVER.rstrip('/')
            self.bot = Bot(token=TELEGRAM_BOT_TOKEN, base_url=f"{base_url}/bot")
            logger.info(f"Using local Bot API server: {base_url}")
            logger.info(f"Max file size: {MAX_VIDEO_SIZE_MB} MB (2 GB limit)")
        else:
            self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
            logger.info("Using default Telegram Bot API servers")
            logger.info(f"Max file size: {MAX_VIDEO_SIZE_MB} MB")

        self.website_url = WEBSITE_URL
        self.channel_id = TELEGRAM_CHANNEL_ID
        self.admin_id = ADMIN_ID
        self.last_video_id = self.load_last_video_id()

    def load_last_video_id(self):
        """Load the ID of the last processed video from file"""
        try:
            if os.path.exists(LAST_VIDEO_ID_FILE):
                with open(LAST_VIDEO_ID_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('last_id', None)
        except Exception as e:
            logger.error(f"Error loading last video ID: {e}")
        return None

    def save_last_video_id(self, video_id):
        """Save the ID of the last processed video to file"""
        try:
            with open(LAST_VIDEO_ID_FILE, 'w') as f:
                json.dump({'last_id': video_id}, f)
            logger.info(f"Saved last video ID: {video_id}")
        except Exception as e:
            logger.error(f"Error saving last video ID: {e}")

    async def send_admin_message(self, message, parse_mode=None):
        """Send a status message to the admin with retry logic"""
        if not self.admin_id:
            logger.warning("ADMIN_ID not set, skipping admin notification")
            return False

        max_retries = 3
        for attempt in range(max_retries):
            try:
                await self.bot.send_message(
                    chat_id=self.admin_id,
                    text=message,
                    parse_mode=parse_mode,
                    read_timeout=30,
                    write_timeout=30,
                    connect_timeout=30
                )
                logger.debug("Admin notification sent successfully")
                return True
            except Exception as e:
                logger.warning(f"Failed to send admin notification (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)  # Wait 2 seconds before retry
                else:
                    logger.error(f"Failed to send admin notification after {max_retries} attempts")
                    return False

    def get_latest_video_id(self):
        """Get the ID of the latest (first) video on the page without processing it"""
        try:
            response = requests.get(self.website_url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the videos container
            videos_ul = soup.find('ul', class_='videos_ul')
            if not videos_ul:
                logger.warning("Could not find ul.videos_ul element")
                return None

            # Find the first video block (latest video)
            first_video = videos_ul.find('li', class_='video_block')
            if first_video:
                video_id = first_video.get('id')
                logger.info(f"Latest video ID on website: {video_id}")
                return video_id

            return None

        except Exception as e:
            logger.error(f"Error fetching latest video ID: {e}")
            return None

    def get_new_videos(self):
        """Parse the main page and get new video links (starts from first/newest video)"""
        try:
            response = requests.get(self.website_url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the videos container
            videos_ul = soup.find('ul', class_='videos_ul')
            if not videos_ul:
                logger.warning("Could not find ul.videos_ul element")
                return []

            # Find all video blocks
            video_blocks = videos_ul.find_all('li', class_='video_block')
            new_videos = []

            for block in video_blocks:
                video_id = block.get('id')
                if not video_id:
                    continue

                # If this is the last processed video, stop here
                if video_id == self.last_video_id:
                    break

                # Find the link to the video page
                link_elem = block.find('a', class_='image')
                if link_elem and link_elem.get('href'):
                    video_url = link_elem['href']
                    # Make absolute URL if needed
                    if not video_url.startswith('http'):
                        video_url = self.website_url.rstrip('/') + '/' + video_url.lstrip('/')

                    new_videos.append({
                        'id': video_id,
                        'url': video_url
                    })

            # Process videos in order (first/newest first)
            # No need to reverse - process from beginning of container
            return new_videos

        except Exception as e:
            logger.error(f"Error fetching new videos: {e}")
            return []

    def get_video_download_url(self, video_page_url):
        """Get the direct video download URL from the video page"""
        try:
            response = requests.get(video_page_url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Navigate: div.col_video → div.player-wrapper → video
            col_video = soup.find('div', class_='col_video')
            if not col_video:
                logger.warning("Could not find div.col_video")
                return None

            player_wrapper = col_video.find('div', class_='player-wrapper')
            if not player_wrapper:
                logger.warning("Could not find div.player-wrapper")
                return None

            video_tag = player_wrapper.find('video')
            if not video_tag:
                logger.warning("Could not find video tag")
                return None

            video_src = video_tag.get('src')
            if not video_src:
                logger.warning("Video tag has no src attribute")
                return None

            # Make absolute URL if needed
            if not video_src.startswith('http'):
                video_src = self.website_url.rstrip('/') + '/' + video_src.lstrip('/')

            return video_src

        except Exception as e:
            logger.error(f"Error getting video download URL: {e}")
            return None

    def download_video(self, video_url, save_path):
        """Download video from URL"""
        try:
            logger.info(f"Downloading video from {video_url}")
            response = requests.get(video_url, headers=HEADERS, stream=True, timeout=60)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            logger.info(f"Video size: {total_size / (1024*1024):.2f} MB")

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info(f"Video downloaded successfully to {save_path}")
            return True

        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return False

    def get_video_metadata(self, video_path):
        """
        Extract video metadata (duration, width, height) using OpenCV
        """
        try:
            logger.info("Extracting video metadata with OpenCV...")

            # Open video file
            cap = cv2.VideoCapture(video_path)

            if not cap.isOpened():
                logger.warning("Could not open video file for metadata extraction")
                return None

            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Calculate duration
            if fps > 0:
                duration = int(frame_count / fps)
            else:
                duration = None

            cap.release()

            if duration and width and height:
                logger.info(f"Video metadata: {width}x{height}, duration: {duration}s ({duration/60:.1f} min)")
                return {
                    'duration': duration,
                    'width': width,
                    'height': height
                }

            return None

        except Exception as e:
            logger.warning(f"Error getting video metadata: {e}")
            return None

    def generate_thumbnail(self, video_path, thumbnail_path):
        """
        Generate a thumbnail from the video using OpenCV
        """
        try:
            logger.info("Generating video thumbnail with OpenCV...")

            # Open video file
            cap = cv2.VideoCapture(video_path)

            if not cap.isOpened():
                logger.warning("Could not open video file for thumbnail generation")
                return None

            # Set position to 10 seconds into the video
            cap.set(cv2.CAP_PROP_POS_MSEC, 10000)  # 10 seconds = 10000 milliseconds

            # Read frame
            success, frame = cap.read()

            if not success:
                # If 10 seconds fails, try first frame
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                success, frame = cap.read()

            cap.release()

            if not success:
                logger.warning("Could not extract frame from video")
                return None

            # Resize frame to thumbnail size (320px width)
            height, width = frame.shape[:2]
            new_width = 320
            new_height = int((new_width / width) * height)
            resized = cv2.resize(frame, (new_width, new_height))

            # Convert BGR to RGB (OpenCV uses BGR)
            rgb_frame = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

            # Save as JPEG using PIL
            img = Image.fromarray(rgb_frame)
            img.save(thumbnail_path, 'JPEG', quality=85)

            logger.info(f"Thumbnail generated: {thumbnail_path}")
            return thumbnail_path

        except Exception as e:
            logger.warning(f"Error generating thumbnail: {e}")
            return None

    async def upload_to_telegram(self, video_path):
        """
        Upload video to Telegram channel with metadata and thumbnail.
        Uses local Bot API server if configured to support files up to 2GB.
        """
        thumbnail_file = None
        try:
            file_size = os.path.getsize(video_path)
            file_size_mb = file_size / (1024 * 1024)

            logger.info(f"Preparing to upload file ({file_size_mb:.2f} MB) to Telegram")

            # Check if file exceeds limit
            if file_size_mb > MAX_VIDEO_SIZE_MB:
                error_msg = f"File is {file_size_mb:.2f} MB (> {MAX_VIDEO_SIZE_MB} MB limit)"
                if not LOCAL_BOT_API_SERVER:
                    error_msg += "\nTo upload files >50MB, set up local Bot API server (see LOCAL_SERVER_SETUP.md)"
                logger.error(error_msg)
                return False

            # Extract video metadata (duration, width, height)
            metadata = self.get_video_metadata(video_path)

            # Generate thumbnail
            thumbnail_path = video_path.replace('.mp4', '_thumb.jpg')
            thumbnail = self.generate_thumbnail(video_path, thumbnail_path)

            # Prepare video upload parameters
            duration = metadata['duration'] if metadata else None
            width = metadata['width'] if metadata else None
            height = metadata['height'] if metadata else None

            # Upload the video with metadata and thumbnail
            with open(video_path, 'rb') as video_file:
                # Open thumbnail file if it was generated
                if thumbnail and os.path.exists(thumbnail):
                    thumbnail_file = open(thumbnail, 'rb')

                logger.info(f"Uploading video ({file_size_mb:.2f} MB)...")
                if duration:
                    logger.info(f"Duration: {duration}s ({duration/60:.1f} min), Resolution: {width}x{height}")

                await self.bot.send_video(
                    chat_id=self.channel_id,
                    video=video_file,
                    thumbnail=thumbnail_file if thumbnail_file else None,
                    caption=f"📹 New video uploaded\n\n📦 Size: {file_size_mb:.2f} MB",
                    duration=duration,
                    width=width,
                    height=height,
                    read_timeout=600,
                    write_timeout=600,
                    connect_timeout=600,
                    supports_streaming=True
                )

            logger.info("Video uploaded successfully to Telegram")

            # Clean up thumbnail file
            if thumbnail and os.path.exists(thumbnail):
                try:
                    os.remove(thumbnail)
                    logger.info(f"Removed thumbnail file: {thumbnail}")
                except Exception as e:
                    logger.warning(f"Could not remove thumbnail: {e}")

            return True

        except TelegramError as e:
            logger.error(f"Telegram error uploading video: {e}")
            return False
        except Exception as e:
            logger.error(f"Error uploading video: {e}")
            return False
        finally:
            # Make sure thumbnail file handle is closed
            if thumbnail_file:
                thumbnail_file.close()

    async def process_video(self, video_info):
        """Process a single video: download and upload to Telegram"""
        video_id = video_info['id']
        video_page_url = video_info['url']

        logger.info(f"Processing video ID: {video_id}")
        logger.info(f"Video page URL: {video_page_url}")

        # Notify admin about new video processing
        await self.send_admin_message(
            f"🔄 <b>Processing new video</b>\n"
            f"🆔 Video ID: <code>{video_id}</code>",
            parse_mode='HTML'
        )

        # Get video download URL
        video_download_url = self.get_video_download_url(video_page_url)
        if not video_download_url:
            logger.error(f"Could not get download URL for video {video_id}")
            await self.send_admin_message(
                f"❌ <b>Error:</b> Could not get download URL\n"
                f"🆔 Video ID: <code>{video_id}</code>",
                parse_mode='HTML'
            )
            return False

        # Download video
        temp_video_path = f"temp_video_{video_id}.mp4"
        if not self.download_video(video_download_url, temp_video_path):
            logger.error(f"Could not download video {video_id}")
            await self.send_admin_message(
                f"❌ <b>Error:</b> Failed to download video\n"
                f"🆔 Video ID: <code>{video_id}</code>",
                parse_mode='HTML'
            )
            return False

        # Get file size
        file_size_mb = os.path.getsize(temp_video_path) / (1024 * 1024)

        # Notify about upload
        await self.send_admin_message(
            f"⬆️ <b>Uploading to channel</b>\n"
            f"🆔 Video ID: <code>{video_id}</code>\n"
            f"📦 Size: {file_size_mb:.2f} MB",
            parse_mode='HTML'
        )

        # Upload to Telegram
        upload_success = await self.upload_to_telegram(temp_video_path)

        if upload_success:
            await self.send_admin_message(
                f"✅ <b>Video uploaded successfully!</b>\n"
                f"🆔 Video ID: <code>{video_id}</code>\n"
                f"📦 Size: {file_size_mb:.2f} MB",
                parse_mode='HTML'
            )
        else:
            await self.send_admin_message(
                f"❌ <b>Error:</b> Failed to upload video\n"
                f"🆔 Video ID: <code>{video_id}</code>",
                parse_mode='HTML'
            )

        # Clean up temporary file
        try:
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
                logger.info(f"Removed temporary file: {temp_video_path}")
        except Exception as e:
            logger.warning(f"Could not remove temporary file: {e}")

        return upload_success

    async def send_startup_message(self):
        """Send a startup status message to admin"""
        last_id_display = f"<code>{self.last_video_id}</code>" if self.last_video_id else "<i>None (first run)</i>"
        startup_msg = (
            "🤖 <b>Video Parser Bot Started!</b>\n\n"
            f"📡 <b>Website:</b> {self.website_url}\n"
            f"🔄 <b>Check Interval:</b> {CHECK_INTERVAL} seconds ({CHECK_INTERVAL // 60} minutes)\n"
            f"📊 <b>Last Processed Video:</b> {last_id_display}\n\n"
            "✅ Bot is running and monitoring for new videos..."
        )
        return await self.send_admin_message(startup_msg, parse_mode='HTML')

    async def run(self):
        """Main loop to check for new videos periodically"""
        logger.info("Starting Video Parser Bot")
        logger.info(f"Website: {self.website_url}")
        logger.info(f"Telegram Channel: {self.channel_id}")
        logger.info(f"Check interval: {CHECK_INTERVAL} seconds")

        # If this is the first run (no saved video ID), get the latest video ID
        # and save it without processing, so only new videos after this will be processed
        is_first_run = self.last_video_id is None
        if is_first_run:
            logger.info("First run detected - will fetch only the latest video ID without processing")
            latest_id = self.get_latest_video_id()
            if latest_id:
                self.save_last_video_id(latest_id)
                self.last_video_id = latest_id
                logger.info(f"Saved latest video ID: {latest_id}. Future runs will only process new videos after this one.")
            else:
                logger.warning("Could not get latest video ID on first run")

        logger.info(f"Last processed video ID: {self.last_video_id}")

        # Send startup test message immediately
        await self.send_startup_message()

        while True:
            try:
                logger.info("Checking for new videos...")
                new_videos = self.get_new_videos()

                if new_videos:
                    # Only process the first video (newest one)
                    video_info = new_videos[0]

                    if len(new_videos) > 1:
                        logger.info(f"Found {len(new_videos)} new video(s), processing only the first one")
                        await self.send_admin_message(
                            f"🎬 <b>Found {len(new_videos)} new video(s)!</b>\n"
                            f"Processing the newest one (ID: <code>{video_info['id']}</code>)...",
                            parse_mode='HTML'
                        )
                    else:
                        logger.info(f"Found 1 new video")
                        await self.send_admin_message(
                            f"🎬 <b>Found 1 new video!</b>\n"
                            f"Starting download and upload process...",
                            parse_mode='HTML'
                        )

                    # Process only the first (newest) video
                    success = await self.process_video(video_info)

                    if success:
                        # Update last video ID after successful processing
                        self.save_last_video_id(video_info['id'])
                        self.last_video_id = video_info['id']
                    else:
                        logger.error(f"Failed to process video {video_info['id']}, will retry next time")
                        # Don't update last_video_id so we retry this video next time
                else:
                    logger.info("No new videos found")

            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await self.send_admin_message(
                    f"⚠️ <b>Error in main loop:</b>\n"
                    f"<code>{str(e)}</code>",
                    parse_mode='HTML'
                )

            # Wait before next check
            next_check_time = time.strftime('%H:%M:%S', time.localtime(time.time() + CHECK_INTERVAL))
            logger.info(f"Waiting {CHECK_INTERVAL} seconds before next check...")
            await self.send_admin_message(
                f"⏳ <b>Next check at:</b> {next_check_time}\n"
                f"💤 Sleeping for {CHECK_INTERVAL // 60} minutes...",
                parse_mode='HTML'
            )
            await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    bot = VideoParserBot()
    asyncio.run(bot.run())
