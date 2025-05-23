import json
from datetime import datetime

# ตั้งค่าข้อมูลเริ่มต้นใหม่
reset_data = {
    "date": datetime.now().strftime("%Y-%m-%d"),
    "round": 0,
    "status": "closed"
}

# เขียนทับไฟล์
with open("trade_status.json", "w") as f:
    json.dump(reset_data, f, indent=2)

print("✅ รีเซ็ตรอบเป็น 0 แล้ว พร้อมเริ่มรอบที่ 1 ใหม่")
