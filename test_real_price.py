import os
import json
import random
from datetime import datetime
from app import (
    get_gold_price,
    openai,
    format_trade_signal,
    send_to_discord,
    get_today_trade_round,
    is_previous_trade_closed
)

# 📁 โหลด trade_status.json
try:
    with open("trade_status.json", "r") as f:
        trade = json.load(f)
except FileNotFoundError:
    trade = {"status": "closed"}  # ถ้าไม่มีไฟล์ถือว่าซิกก่อนหน้าปิดแล้ว

# 🛑 หยุดถ้ายังไม่ closed หรือ cancelled
if trade["status"] not in ["closed", "cancelled"]:
    print("⛔ ซิกก่อนหน้ายังไม่จบ หยุดส่งซิกใหม่")
    exit()

# 🛑 หากซิกก่อนหน้ายังเปิดอยู่ ให้หยุดส่งซิกใหม่

# โหลด trade_status.json ให้ตัวแปร trade มีค่า
with open("trade_status.json", "r") as f:
    trade = json.load(f)

if trade["status"] not in ["closed", "cancelled"]:
    print("⛔ ซิกก่อนหน้ายังไม่จบ หยุดส่งซิกใหม่")
    exit()


# 📆 เวลาปัจจุบัน
now = datetime.now()
thai_date = now.strftime("%d %b %Y")
clock = now.strftime("%H:%M")
round_number = get_today_trade_round()
current_price = get_gold_price()

# 🎯 สุ่มฝั่งและสร้าง RR 1:2
side = random.choice(["buy", "sell"])
rr = 2
risk = 5  # ระยะ SL

if side == "buy":
    entry = round(current_price - 3, 2)
    sl = round(entry - risk, 2)
    tp1 = round(entry + (risk * 1), 2)
    tp2 = round(entry + (risk * rr), 2)
    tp3 = round(entry + (risk * rr * 2), 2)
else:
    entry = round(current_price + 3, 2)
    sl = round(entry + risk, 2)
    tp1 = round(entry - (risk * 1), 2)
    tp2 = round(entry - (risk * rr), 2)
    tp3 = round(entry - (risk * rr * 2), 2)

# 💬 สร้าง Prompt วิเคราะห์โดย GPT
prompt = f"""
ราคาทองคำล่าสุด: {current_price}

นายคือ Michael J. Huddleston เจ้าของระบบ ICT 
วิเคราะห์ด้วยแนวคิด ICT วิเคราะห์แนวโน้มตลาดทองคำใน Timeframe M5/M15/H1 ว่าควร Buy หรือ Sell
และสรุปเหตุผลในการเข้าออเดอร์แบบสั้น กระชับ

**ห้ามเขียนเกิน 3 บรรทัด และไม่ใส่คำอธิบายยาว**
"""

response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "คุณคือผู้ช่วยเทรดเดอร์มืออาชีพ ใช้แนวคิด SMC/ICT เท่านั้น"},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7
)
reason = response.choices[0].message.content.strip()

# 💾 บันทึก trade_status.json
trade_status = {
    "date": now.strftime("%Y-%m-%d"),
    "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
    "round": round_number,
    "status": "open",
    "side": side,
    "entry": entry,
    "tp1": tp1,
    "tp2": tp2,
    "tp3": tp3,
    "sl": sl
}
with open("trade_status.json", "w") as f:
    json.dump(trade_status, f, indent=2)

# 📦 เตรียมข้อมูลส่งข้อความ
signal_data = {
    "round": round_number,
    "current_price": current_price,
    "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
    "date": thai_date,
    "time": clock,
    "side": side,
    "entry": entry,
    "sl": sl,
    "tp1": tp1,
    "tp2": tp2,
    "tp3": tp3,
    "sl_pips": round(abs(entry - sl) * 100),
    "tp1_pips": round(abs(tp1 - entry) * 100),
    "tp2_pips": round(abs(tp2 - entry) * 100),
    "tp3_pips": round(abs(tp3 - entry) * 100),
    "reason": reason
}
signal_message = format_trade_signal(signal_data)

# 📈 สรุปสถิติ

from datetime import datetime
today = datetime.now().strftime("%Y-%m-%d")

# ✅ โหลด log ทั้งหมดก่อนใช้งาน
with open("trade_log.json", "r") as f:
    logs = json.load(f)
    
today_logs = [log for log in logs if log["date"] == today]
try:
    with open("trade_log.json", "r") as f:
        logs = json.load(f)
        last = logs[-1]
        last_result = f"รอบก่อนหน้า: {'✅ ' if last['result'].startswith('TP') else '❌'} {last['result']} ({last['pips']} จุด)"
        tp_count = sum(1 for r in today_logs if r["result"].startswith("TP"))
        sl_count = sum(1 for r in today_logs if r["result"] == "SL")
        net_pips = sum(r["pips"] for r in today_logs)
        stat_summary = f"TP = {tp_count} ครั้ง | 🟥 SL = {sl_count} ครั้ง | 🎉 กำไรสุทธิ = {net_pips:+} จุด"
except:
    last_result = "ยังไม่มีสถิติ"
    stat_summary = ""

# 📤 ส่งข้อความเข้า Discord
signal_message += f"\n\n⏪ {last_result}\n🟦 {stat_summary}"
send_to_discord(signal_message)
print("✅ ส่งซิกใหม่เรียบร้อยแล้ว")
