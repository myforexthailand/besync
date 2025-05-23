# บันทึกผลลัพธ์ไว้ใน log
log_data = {
    "date": trade["date"],
    "round": trade["round"],
    "result": "TP1",
    "pips": tp1_pips
}

# โหลด log เดิม (หรือเริ่มใหม่)
try:
    with open("trade_log.json", "r") as f:
        logs = json.load(f)
except:
    logs = []

logs.append(log_data)

with open("trade_log.json", "w") as f:
    json.dump(logs, f, indent=2)
