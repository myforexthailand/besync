import os
import json
from datetime import datetime

def is_previous_trade_closed():
    if not os.path.exists("trade_status.json"):
        return True
    with open("trade_status.json", "r") as f:
        data = json.load(f)
        return data.get("status") == "closed"


def format_trade_signal(data):
    return f"""
📢 สัญญาณเทรดคู่ ทองคำ (GOLD)
[ รอบที่ {data['round']} - ประจำวันที่ {data['date']} เวลา {data['time']} น. ]

{'🔴' if data['side'] == 'sell' else '🟢'} {data['side'].capitalize()} Price = {data['entry']}
(รอให้ราคาย่อตัวกลับ{'ขึ้น' if data['side'] == 'buy' else 'ลง'}มาทดสอบโซนก่อนกลับตัว{'ขึ้น' if data['side'] == 'buy' else 'ลง'})

❌ Stop Loss = {data['sl']} ( - {data['sl_pips']} จุด )
✅ TP 1 = {data['tp1']} ( + {data['tp1_pips']} จุด )
✅ TP 2 = {data['tp2']} ( + {data['tp2_pips']} จุด )
✅ TP 3 = {data['tp3']} ( + {data['tp3_pips']} จุด )

📌 เหตุผลในการเข้าออเดอร์:
{data['reason']}
""".strip()