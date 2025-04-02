from telethon import TelegramClient
import asyncio
import random
from datetime import datetime
from keep_alive import keep_alive

api_id = 29644284
api_hash = "2bb2b9ebc9846d5b205ea96caf5e7569"
session_name = "forwarder"

channel_a = -1002253462298
channel_b = -1002238054330

client = TelegramClient(session_name, api_id, api_hash)
last_sent_ids = []

async def fetch_all_grouped_ids():
    grouped_map = {}
    async for msg in client.iter_messages(channel_a):
        if msg.grouped_id:
            grouped_map.setdefault(msg.grouped_id, []).append(msg.id)
    return grouped_map

async def post_random_forward():
    global last_sent_ids
    grouped_map = await fetch_all_grouped_ids()
    if not grouped_map:
        print("Geen albums gevonden.")
        return

    chosen_group = random.choice(list(grouped_map.values()))
    if not chosen_group:
        print("Gekozen album is leeg.")
        return

    chosen_group.sort()

    if last_sent_ids:
        try:
            await client.delete_messages(channel_b, last_sent_ids)
            print("Vorige album verwijderd.")
        except Exception as e:
            print("Fout bij verwijderen:", e)
    last_sent_ids.clear()

    try:
        sent = await client.forward_messages(
            entity=channel_b,
            messages=chosen_group,
            from_peer=channel_a
        )
        if isinstance(sent, list):
            last_sent_ids.extend([m.id for m in sent])
        else:
            last_sent_ids.append(sent.id)

        print(f"Nieuw album geforward om {datetime.now()}")

    except Exception as e:
        print(f"Fout bij forwarden: {e}")

async def loop():
    while True:
        await post_random_forward()
        await asyncio.sleep(60)

async def main():
    keep_alive()
    await client.start()
    print("Bot draait...")
    await loop()

if __name__ == '__main__':
    asyncio.run(main())
