from telethon import TelegramClient, events
import requests
import asyncio
from datetime import datetime, timezone

# ====== Setup ======
sent_at = datetime.now(timezone.utc).isoformat()

# ====== Telegram Config ======
api_id = 28128851
api_hash = 'b613db4e676e00989ec8babc57c07fa0'
client = TelegramClient('multi_channel_listener', api_id, api_hash)

# ====== Supabase Config ======
SUPABASE_URL = 'https://xybpqwvxdsozmyqbcrfz.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh5YnBxd3Z4ZHNvem15cWJjcmZ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU5NzQyNzMsImV4cCI6MjA2MTU1MDI3M30.-JZ2ejXJxS3oDH9vKkJKjzceFo4SdBvOyexbnc43KTQ'

# ====== Channel List ======
channel_usernames = ['XdropHunters', 'airdropfind', 'airdropsultanindonesia', 'getairdrop_id']

# Function to insert data into Supabase using requests
def insert_to_supabase(username, message, sent_at, name, link):
    # Data to insert into Supabase
    data = {
        "username": username,
        "message": message,
        "sent_at": sent_at,
        "name": name,
        "link": link
    }

    # Send data to Supabase using POST request
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/telegram_messages", 
        headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json"
        },
        json=data
    )

    # Check status code for debugging
    if response.status_code == 201:
        print(f"Inserted message from {username} into Supabase.")
    else:
        print(f"Failed to insert data. Status Code: {response.status_code}")
        print(response.text)

# Event handler for new messages
@client.on(events.NewMessage(chats=channel_usernames))
async def handler(event):
    sender = await event.get_sender()
    username = sender.username or "unknown"
    message = event.message.text
    sent_at = datetime.now(timezone.utc).isoformat()
    
    # Get the channel name
    channel_name = event.chat.title if event.chat.title else "unknown channel"
    
    # Construct the post link
    link = f"https://t.me/{event.chat.username}/{event.message.id}" if event.chat.username else "no link available"

    print(f"[{username}] {message} (From: {channel_name}, Link: {link})")
    
    # Insert the message into Supabase using requests
    await asyncio.to_thread(insert_to_supabase, username, message, sent_at, channel_name, link)

# Main entry point to start the client
async def main():
    await client.start()
    print("Listening to channels...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
