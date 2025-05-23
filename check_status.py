import json
from app import get_gold_price

with open("trade_status.json", "r") as f:
    status = json.load(f)

if status["status"] == "closed":
    exit()

price = get_gold_price()

if status["side"] == "buy":
    if price >= status["tp1"] or price <= status["sl"]:
        status["status"] = "closed"

elif status["side"] == "sell":
    if price <= status["tp1"] or price >= status["sl"]:
        status["status"] = "closed"


if status["status"] == "closed":
    # ส่งข้อความไป Discord
    from discord_bot import send_to_discord
    send_to_discord(f"✅ ซิกจบรอบที่ {status['round']} แล้ว ({status['side'].upper()})")

    with open("trade_status.json", "w") as f:
        json.dump(status, f)
