import json
from datetime import datetime
from app import get_gold_price, log_trade_result
from discord_bot import send_to_discord

print("\U0001F680 เริ่มต้นเช็กสถานะซิก...")

# ✅ โหลดสถานะซิก
with open("trade_status.json", "r") as f:
    trade = json.load(f)
print("📁 JSON Loaded:", trade)

# ถ้าซิกถูกปิดไปแล้ว
if trade["status"] == "closed":
    print("✅ ซิกนี้ปิดไปแล้ว")
    exit()

# ดึงข้อมูลหลัก
side = trade["side"]
entry = float(trade["entry"])
tp1 = float(trade["tp1"])
sl = float(trade["sl"])
price = get_gold_price()
entry_filled = trade.get("entry_filled", False)

print(f"\U0001F4CA ราคาปัจจุบัน: {price}, Entry: {entry}, TP1: {tp1}, SL: {sl}, Side: {side}")

# ---------- เงื่อนไข: ยังไม่เข้าไม้แต่ราคาชน TP หรือ SL ----------
def is_signal_invalidated(side, entry, sl, tp1, price):
    if side == "buy":
        return price >= tp1 or price <= sl
    elif side == "sell":
        return price <= tp1 or price >= sl
    return False

if not entry_filled and is_signal_invalidated(side, entry, sl, tp1, price):
    print("❌ พลาดจุดเข้า ราคาวิ่งไปก่อน (ยกเลิกซิกนี้)")
    trade["status"] = "cancelled"
    with open("trade_status.json", "w") as f:
        json.dump(trade, f, indent=2)
    exit()

# ---------- เงื่อนไข: ตรวจว่าเข้าไม้หรือยัง ----------
def check_entry_filled(side, entry, price):
    return (side == "buy" and price <= entry) or (side == "sell" and price >= entry)

if not entry_filled and check_entry_filled(side, entry, price):
    print("🟢 เข้าไม้เรียบร้อยแล้ว")
    trade["entry_filled"] = True
    with open("trade_status.json", "w") as f:
        json.dump(trade, f, indent=2)

# ---------- เงื่อนไข: ตรวจ TP/SL หลังเข้าไม้ ----------
result = None
pips = 0

if trade.get("entry_filled"):
    if side == "buy":
        if price >= tp1:
            result = "TP1"
            pips = round((tp1 - entry) * 100)
        elif price <= sl:
            result = "SL"
            pips = round((sl - entry) * 100)
    elif side == "sell":
        if price <= tp1:
            result = "TP1"
            pips = round((entry - tp1) * 100)
        elif price >= sl:
            result = "SL"
            pips = round((entry - sl) * 100)

    if result:
        print(f"✅ ปิดซิกด้วยผลลัพธ์ {result}")
        trade["status"] = "closed"
        with open("trade_status.json", "w") as f:
            json.dump(trade, f, indent=2)

        log_trade_result(result, entry, tp1 if result == "TP1" else sl)

        message = (
            f"------------------ *************** ------------------\n"
            f"\U0001F4CC **สัญญาณปิดออเดอร์ (GOLD)**\n"
            f"📅 วันที่: {trade['date']} | รอบที่ {trade['round']}\n\n"
            f"{'🎉🎉🎉 TP1 +' + str(pips) + ' จุด 🎉🎉🎉' if result == 'TP1' else '❌❌❌ SL ' + str(pips) + ' จุด ❌❌❌'}\n\n"
            f"👉 Entry: {entry}\n"
            f"🔔 ราคาล่าสุด: {price}\n"
            f"------------------ *************** ------------------"
        )
        send_to_discord(message)
else:
    print("🕐 ราคายังไม่ชน TP1 หรือ SL")
