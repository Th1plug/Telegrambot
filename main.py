import json
import random
import time
import threading
import os
import requests

from keep_alive import keep_alive
from telegram import Bot, InputMediaPhoto, InputMediaVideo, Update
from telegram.ext import CommandHandler, MessageHandler, filters, ApplicationBuilder, ContextTypes

BOT_TOKEN = "7634314038:AAH5paHoryOOuMVteVIlHKDj54smE44fP64"
CHANNEL_ID = -1002238054330
ALBUMS_FILE = "albums.json"

bot = Bot(BOT_TOKEN)

if not os.path.exists(ALBUMS_FILE):
    with open(ALBUMS_FILE, "w") as f:
        json.dump([], f)

def load_albums():
    with open(ALBUMS_FILE, "r") as f:
        return json.load(f)

def save_album(album):
    albums = load_albums()
    albums.append(album)
    with open(ALBUMS_FILE, "w") as f:
        json.dump(albums, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Stuur mij een album (foto's/video's met caption), ik sla het op!")

async def handle_album(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.media_group_id:
        return

    user_id = update.message.from_user.id
    media_group_id = update.message.media_group_id
    context.user_data.setdefault("albums", {}).setdefault(media_group_id, []).append(update.message)

    await asyncio.sleep(2)

    messages = context.user_data["albums"].pop(media_group_id, [])
    messages.sort(key=lambda m: m.message_id)

    caption = messages[0].caption if messages[0].caption else ""

    album_data = []
    for msg in messages:
        if msg.photo:
            file_id = msg.photo[-1].file_id
            kind = "photo"
        elif msg.video:
            file_id = msg.video.file_id
            kind = "video"
        else:
            continue
        album_data.append({"type": kind, "file_id": file_id})

    save_album({"media": album_data, "caption": caption})
    await update.message.reply_text("Album opgeslagen!")

def post_random_album():
    while True:
        albums = load_albums()
        if not albums:
            time.sleep(60)
            continue
        album = random.choice(albums)
        media_group = []

        for item in album["media"]:
            if item["type"] == "photo":
                media_group.append(InputMediaPhoto(media=item["file_id"]))
            elif item["type"] == "video":
                media_group.append(InputMediaVideo(media=item["file_id"]))

        if media_group:
            media_group[0].caption = album["caption"]
            media_group[0].parse_mode = "HTML"

        try:
            bot.send_media_group(chat_id=CHANNEL_ID, media=media_group)
        except Exception as e:
            print("Fout bij posten:", e)

        time.sleep(60)

def start_posting_thread():
    t = threading.Thread(target=post_random_album)
    t.daemon = True
    t.start()

if __name__ == "__main__":
    import asyncio
    keep_alive()
    start_posting_thread()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handle_album))
    print("Bot draait en wacht op albums...")
    app.run_polling()
