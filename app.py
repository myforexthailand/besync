import requests
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify
import openai
from dotenv import load_dotenv
from discord_bot import send_to_discord
from utils import format_trade_signal

# โหลด ENV และตั้งค่า Flask
load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# ------------------------- FUNCTION -------------------------

def log_trade_result(result, entry, target):
    pips = int(abs(target - entry) * 100)
    if result == "SL":
        pips = -pips

    new_log = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "round": get_today_trade_round(),
        "result": result,
        "entry": entry,
        "target": target,
        "pips": pips
    }

    try:
        with open("trade_log.json", "r") as f:
            logs = json.load(f)
    except:
        logs = []

    logs.append(new_log)
    with open("trade_log.json", "w") as f:
        json.dump(logs, f, indent=2)


def is_previous_trade_closed():
    if not os.path.exists("trade_status.json"):
        return True
    with open("trade_status.json", "r") as f:
        data = json.load(f)
        return data.get("status") in ["closed", "cancelled"]


def get_today_trade_round():
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = "round_tracker.txt"

    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
        if data.get("date") == today:
            data["round"] += 1
        else:
            data = {"date": today, "round": 1}
    else:
        data = {"date": today, "round": 1}

    with open(filepath, "w") as f:
        json.dump(data, f)

    return data["round"]


def get_gold_price():
    url = "https://www.goldapi.io/api/XAU/USD"
    headers = {
        "x-access-token": "goldapi-547aqsmazexmhx-io",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    data = response.json()

    if "ask" in data:
        return float(data["ask"])
    elif "price" in data:
        return float(data["price"])
    else:
        raise ValueError(f"❌ ไม่พบราคาทองใน response: {data}")

# ------------------------- ROUTE -------------------------

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    # 🧠 สร้าง Prompt ส่ง GPT
    prompt = f"""
    วิเคราะห์ข้อมูลกราฟทองคำจาก TradingView โดยใช้หลัก SMC/ICT:
    Symbol: XAUUSD
    TF: {data.get('tf', 'M15')}
    Bias: {data.get('bias', 'bullish')}
    CHoCH: {data.get('choch')}
    Order Block: {data.get('orderblock')}
    Entry: {data['entry']}
    SL: {data['sl']}
    TP1: {data['tp1']}
    TP2: {data['tp2']}
    TP3: {data['tp3']}

    สรุปออกมาเป็นเหตุผลในการเข้าเทรด (3 บรรทัด)
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

    # 📅 เวลาปัจจุบัน
    now = datetime.now()
    thai_time = now.strftime("%d %b %Y")
    clock = now.strftime("%H:%M")

    signal_data = {
        "round": data.get("round", "1"),
        "date": thai_time,
        "time": clock,
        "side": data.get("side", "buy"),
        "entry": data["entry"],
        "sl": data["sl"],
        "tp1": data["tp1"],
        "tp2": data["tp2"],
        "tp3": data["tp3"],
        "sl_pips": round(abs(data["entry"] - data["sl"]) * 1000),
        "tp1_pips": round(abs(data["tp1"] - data["entry"]) * 1000),
        "tp2_pips": round(abs(data["tp2"] - data["entry"]) * 1000),
        "tp3_pips": round(abs(data["tp3"] - data["entry"]) * 1000),
        "reason": reason
    }

    # 🧾 สร้างข้อความส่ง Discord
    signal_message = format_trade_signal(signal_data)
    send_to_discord(signal_message)

    return jsonify({"status": "success", "message": "Signal sent!"})


# ------------------------- MAIN -------------------------

if __name__ == '__main__':
    app.run(port=5050)
