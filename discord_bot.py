import os
import requests
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")

def send_to_discord(message):
    url = f"https://discord.com/api/v10/channels/{DISCORD_CHANNEL_ID}/messages"
    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "content": message
    }
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code != 200 and response.status_code != 204:
        print(f"❌ ส่งไม่สำเร็จ: {response.status_code} - {response.text}")
    else:
        print("✅ ข้อความถูกส่งไปยัง Discord แล้ว")
