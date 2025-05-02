from flask import Flask, request, render_template_string, redirect, url_for
from telethon import TelegramClient, events
import requests
import asyncio
from datetime import datetime, timezone
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generates a strong random secret key

# ====== Supabase Config ======
SUPABASE_URL = 'https://xybpqwvxdsozmyqbcrfz.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh5YnBxd3Z4ZHNvem15cWJjcmZ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU5NzQyNzMsImV4cCI6MjA2MTU1MDI3M30.-JZ2ejXJxS3oDH9vKkJKjzceFo4SdBvOyexbnc43KTQ'  # Replace with your actual key

# ====== Channel List ======
channel_usernames = ['XdropHunters', 'airdropfind', 'airdropsultanindonesia', 'getairdrop_id']

# Global variable for Telegram client
client = None

# Function to insert data into Supabase using requests
def insert_to_supabase(username, message, sent_at, name, link):
    data = {
        "username": username,
        "message": message,
        "sent_at": sent_at,
        "name": name,
        "link": link
    }
    
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/telegram_messages", 
        headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json"
        },
        json=data
    )
    
    if response.status_code == 201:
        print(f"Inserted message from {username} into Supabase.")
    else:
        print(f"Failed to insert data. Status Code: {response.status_code}")
        print(response.text)

# Event handler for new messages
async def message_handler():
    global client
    @client.on(events.NewMessage(chats=channel_usernames))
    async def handler(event):
        sender = await event.get_sender()
        username = sender.username or "unknown"
        message = event.message.text
        sent_at = datetime.now(timezone.utc).isoformat()
        channel_name = event.chat.title if event.chat.title else "unknown channel"
        link = f"https://t.me/{event.chat.username}/{event.message.id}" if event.chat.username else "no link available"

        print(f"[{username}] {message} (From: {channel_name}, Link: {link})")
        await asyncio.to_thread(insert_to_supabase, username, message, sent_at, channel_name, link)

async def main(api_id, api_hash, phone_number):
    global client
    client = TelegramClient('multi_channel_listener', api_id, api_hash)
    await client.start(phone=phone_number)

    print("Listening to channels...")
    await message_handler()
    await client.run_until_disconnected()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        api_id = request.form['api_id']
        api_hash = request.form['api_hash']
        phone_number = request.form['phone_number']

        # Start the client
        asyncio.run(main(api_id, api_hash, phone_number))
        return redirect(url_for('status'))

    return render_template_string('''
        <form method="post">
            API ID: <input type="text" name="api_id"><br>
            API Hash: <input type="text" name="api_hash"><br>
            Phone Number: <input type="text" name="phone_number"><br>
            <input type="submit" value="Start Listening">
        </form>
    ''')

@app.route('/status')
def status():
    return "Client is running and listening to channels!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
