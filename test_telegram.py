import asyncio
import os
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
ADMIN_ID = os.getenv('ADMIN_ID')

async def test_bot():
    """Test Telegram bot connection and permissions"""

    print("=" * 50)
    print("TELEGRAM BOT CONNECTION TEST")
    print("=" * 50)

    # Check environment variables
    print("\n1. Checking environment variables...")
    print(f"   BOT_TOKEN: {'✅ Set' if TELEGRAM_BOT_TOKEN else '❌ Not set'}")
    print(f"   CHANNEL_ID: {TELEGRAM_CHANNEL_ID if TELEGRAM_CHANNEL_ID else '❌ Not set'}")
    print(f"   ADMIN_ID: {ADMIN_ID if ADMIN_ID else '❌ Not set'}")

    if not TELEGRAM_BOT_TOKEN:
        print("\n❌ ERROR: TELEGRAM_BOT_TOKEN is not set in .env file")
        return

    if not TELEGRAM_CHANNEL_ID:
        print("\n❌ ERROR: TELEGRAM_CHANNEL_ID is not set in .env file")
        return

    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)

        # Test 1: Get bot info
        print("\n2. Testing bot connection...")
        me = await bot.get_me()
        print(f"   ✅ Bot connected successfully!")
        print(f"   Bot username: @{me.username}")
        print(f"   Bot name: {me.first_name}")
        print(f"   Bot ID: {me.id}")

        # Test 2: Send message to admin (if set)
        if ADMIN_ID:
            print("\n3. Testing admin message...")
            try:
                await bot.send_message(
                    chat_id=ADMIN_ID,
                    text="🧪 <b>Test Message to Admin</b>\n\nThis is a test message from your bot!",
                    parse_mode='HTML',
                    read_timeout=30,
                    write_timeout=30,
                    connect_timeout=30
                )
                print(f"   ✅ Admin message sent successfully to {ADMIN_ID}")
            except TelegramError as e:
                print(f"   ❌ Failed to send admin message: {e}")
                print(f"   Possible reasons:")
                print(f"      - Admin ID is incorrect")
                print(f"      - User hasn't started a chat with the bot")
                print(f"      - User blocked the bot")
        else:
            print("\n3. Skipping admin test (ADMIN_ID not set)")

        # Test 3: Send message to channel
        print("\n4. Testing channel message...")
        try:
            message = await bot.send_message(
                chat_id=TELEGRAM_CHANNEL_ID,
                text="🧪 <b>Test Message to Channel</b>\n\nThis is a test message from your video parser bot!",
                parse_mode='HTML',
                read_timeout=30,
                write_timeout=30,
                connect_timeout=30
            )
            print(f"   ✅ Channel message sent successfully!")
            print(f"   Message ID: {message.message_id}")
            print(f"   Channel/Chat ID: {message.chat.id}")
            if message.chat.username:
                print(f"   Channel username: @{message.chat.username}")
        except TelegramError as e:
            print(f"   ❌ Failed to send channel message: {e}")
            print(f"\n   Possible reasons:")
            print(f"      1. Channel ID is incorrect")
            print(f"      2. Bot is not added to the channel")
            print(f"      3. Bot is not an ADMIN of the channel")
            print(f"      4. Bot doesn't have 'Post Messages' permission")
            print(f"\n   How to fix:")
            print(f"      1. Go to your channel settings")
            print(f"      2. Add @{me.username} as an administrator")
            print(f"      3. Enable 'Post Messages' permission")
            print(f"      4. If using username, make sure it starts with @ (e.g., @mychannel)")
            print(f"      5. If using chat ID, make sure it's correct (usually starts with -100)")

        # Test 4: Get chat info
        print("\n5. Getting channel info...")
        try:
            chat = await bot.get_chat(chat_id=TELEGRAM_CHANNEL_ID)
            print(f"   ✅ Channel found!")
            print(f"   Type: {chat.type}")
            print(f"   Title: {chat.title if hasattr(chat, 'title') else 'N/A'}")
            if hasattr(chat, 'username') and chat.username:
                print(f"   Username: @{chat.username}")

            # Check bot permissions
            try:
                admins = await bot.get_chat_administrators(chat_id=TELEGRAM_CHANNEL_ID)
                bot_admin = next((admin for admin in admins if admin.user.id == me.id), None)

                if bot_admin:
                    print(f"\n   ✅ Bot is an administrator!")
                    print(f"   Can post messages: {bot_admin.can_post_messages if hasattr(bot_admin, 'can_post_messages') else 'N/A'}")
                    print(f"   Can edit messages: {bot_admin.can_edit_messages if hasattr(bot_admin, 'can_edit_messages') else 'N/A'}")
                    print(f"   Can delete messages: {bot_admin.can_delete_messages if hasattr(bot_admin, 'can_delete_messages') else 'N/A'}")
                else:
                    print(f"\n   ❌ Bot is NOT an administrator of this channel!")
                    print(f"   Please add @{me.username} as an admin with 'Post Messages' permission")
            except TelegramError as e:
                print(f"\n   ⚠️ Could not check admin status: {e}")

        except TelegramError as e:
            print(f"   ❌ Could not get channel info: {e}")

        print("\n" + "=" * 50)
        print("TEST COMPLETED")
        print("=" * 50)

    except TelegramError as e:
        print(f"\n❌ ERROR: {e}")
        print("\nPossible issues:")
        print("   - Bot token is invalid")
        print("   - Network connection issues")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_bot())
