import os
os.system("pip install tgcrypto")
import json
import logging
import asyncio
import re
import requests
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait, PeerIdInvalid
from fastapi import FastAPI
from uvicorn import Config, Server
import threading

# ----- LOGGING -----
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("group_bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ----- CONFIG VALUES (from Environment Variables) -----
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "selfbot")
PORT = int(os.getenv("PORT", 8000))  # Render provides PORT, default to 8000 for local testing

# Validate environment variables
if not API_ID or not API_HASH:
    logger.error("TELEGRAM_API_ID and TELEGRAM_API_HASH must be set in environment variables.")
    raise ValueError("Missing TELEGRAM_API_ID or TELEGRAM_API_HASH")

# ----- BOT CLIENT -----
app = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH)

# ----- FASTAPI APP -----
web_app = FastAPI()

@web_app.get("/")
async def health_check():
    return {"status": "Bot is running"}

# ----- MAIN TELEGRAM HANDLER -----
@app.on_message(filters.outgoing & filters.text)
async def handle_trigger(client, message):
    text = message.text.strip()

    if text.startswith(".chk"):
        number = text[4:].strip()
        if not number.isdigit():
            await client.send_message(message.chat.id, "❌ Please enter a valid number after `.chk`")
            await client.delete_messages(message.chat.id, message.id)
            return

        url = f"https://decryptkarnrwalebkl.wasmer.app/?key=lodalelobaby&term={number}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise error for bad status codes
            raw_response = response.text
            logger.info(f"Raw server response: {raw_response}")

            # Strip any trailing non-JSON data (e.g., "by @ffloveryt")
            json_str = re.sub(r'\n*by @ffloveryt\n*$', '', raw_response).strip()
            try:
                json_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e} - Cleaned response: {json_str}")
                await client.send_message(message.chat.id, "❌ Could not parse server response as JSON. Check logs.")
                await client.delete_messages(message.chat.id, message.id)
                return

            if isinstance(json_data, dict) and json_data.get("message") == "No records found":
                await client.send_message(message.chat.id, "No Records")
                await client.delete_messages(message.chat.id, message.id)
                return

            if isinstance(json_data, dict) and "data" in json_data and isinstance(json_data["data"], list):
                for record in json_data["data"]:
                    msg = (
                        "====\n"
                        "📱 MOBILE INFORMATION\n"
                        "====\n"
                        f"ID: {record.get('id', '')}\n"
                        f"👤Name: {record.get('name', '')}\n"
                        f"👥Father's Name: {record.get('fname', '')}\n"
                        f"📱Mobile: {record.get('mobile', '')}\n"
                        f"👉Alternate Mobile: {record.get('alt_mobile', '')}\n"
                        f"🦥Circle: {record.get('circle', '')}\n"
                        f"✍️ID Number: {record.get('id_number', '')}\n"
                        f"📩Email: {record.get('email', '')}\n"
                        f"🏫Address: {record.get('address', '')}\n"
                        "========\n"
                        "by @iownpy"
                    )
                    await client.send_message(message.chat.id, msg)
                await client.delete_messages(message.chat.id, message.id)
                return

            await client.send_message(message.chat.id, "⚠️ Unexpected response format.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in .chk handler (network): {e}")
            await client.send_message(message.chat.id, "❌ Failed to fetch number details. Check your connection.")
        except Exception as e:
            logger.error(f"Error in .chk handler: {e}")
            await client.send_message(message.chat.id, "❌ Failed to fetch number details.")
        await client.delete_messages(message.chat.id, message.id)
        return

# ----- HANDLE UPDATES TO IGNORE PEER ID ERRORS -----
@app.on_raw_update()
async def handle_raw_update(client, update, users, chats):
    try:
        # Ignore all updates since we only care about outgoing messages
        pass
    except PeerIdInvalid as e:
        logger.debug(f"Ignoring PeerIdInvalid: {e}")
    except Exception as e:
        logger.error(f"Error in raw update handler: {e}")

# ----- OVERRIDE MESSAGE HANDLER TO SKIP INVALID PEERS -----
@app.on_message()
async def message_handler(client, message):
    try:
        # Only process outgoing messages (already handled by filters.outgoing)
        if message.outgoing:
            await handle_trigger(client, message)
    except PeerIdInvalid as e:
        logger.debug(f"Ignoring PeerIdInvalid in message handler: {e}")
    except Exception as e:
        logger.error(f"Error in message handler: {e}")

# ----- RUN BOT AND WEB SERVER -----
async def run_bot():
    try:
        logger.info("🚀 Bot started. Command: .chk")
        await app.start()
        await app.idle()  # Keep the bot running
    except FloodWait as e:
        logger.warning(f"FloodWait: Sleeping for {e.value} seconds")
        await asyncio.sleep(e.value)
        await run_bot()
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

def run_web_server():
    logger.info(f"Starting web server on port {PORT}")
    config = Config(web_app, host="0.0.0.0", port=PORT)
    server = Server(config)
    server.run()

if __name__ == "__main__":
    # Start the web server in a separate thread
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    # Run the bot in the main thread
    asyncio.run(run_bot())
