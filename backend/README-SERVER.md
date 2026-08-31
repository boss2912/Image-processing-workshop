# เครื่องเซิร์ฟเวอร์ (Backend) — วิธีรันจาก VS Code Terminal

โฟลเดอร์นี้คือ**ทั้งหมด**ที่เครื่องเซิร์ฟเวอร์ต้องมี — สมองของระบบอยู่ที่นี่ที่เดียว

```
backend/
├── app.py                  Flask REST API (3 endpoint)
├── requirements.txt        รายการไลบรารีที่ต้องติดตั้ง
├── start-server.bat        ดับเบิลคลิกรันแบบไม่ต้องพิมพ์
├── README-SERVER.md        ไฟล์นี้
└── processing/
    ├── __init__.py         ทะเบียน OPERATIONS
    ├── edge.py             canny() + sobel()
    └── corner.py           harris() + harris_nms() + contour_boxes()
```

**ไม่มีไฟล์หน้าเว็บอยู่ในนี้เลย** — `index.html` / `app.js` / `style.css` อยู่ในโฟลเดอร์ `frontend/` ซึ่งส่งไปให้อีกเครื่อง

---

## รันจาก VS Code Terminal (PowerShell)

เปิด VS Code แล้วกด **Ctrl + `** เพื่อเปิด terminal จากนั้นทำทีละคำสั่ง

### คำสั่งที่ 1 — เข้าโฟลเดอร์ backend

```powershell
cd "C:\Users\pongs\Desktop\Computer_3\310-3311_Image_Processing\Image-processing-workshop_V1\Image-processing-workshop\backend"
```

### คำสั่งที่ 2 — สร้าง virtual environment (ทำครั้งเดียวตลอดชีวิตโปรเจกต์)

```powershell
python -m venv .venv
```

> ถ้ามีโฟลเดอร์ `.venv` อยู่แล้ว ข้ามข้อนี้ไปได้เลย

### คำสั่งที่ 3 — ติดตั้งไลบรารี (ทำครั้งเดียว)

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

> เรียก `python.exe` ในโฟลเดอร์ `.venv` ตรงๆ แบบนี้ **ไม่ต้อง activate ก่อน**
> ปลอดภัยกว่าเพราะไม่มีทางเผลอติดตั้งลง Python ของเครื่องโดยไม่รู้ตัว

ถ้าอยาก activate จริงๆ ใช้
```powershell
.\.venv\Scripts\Activate.ps1
```
แล้วถ้าเจอ error `running scripts is disabled on this system` ให้รันบรรทัดนี้ก่อนหนึ่งครั้ง
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### คำสั่งที่ 4 — หา IP ของเครื่องนี้ (เอาไปบอกเครื่องเพื่อน)

```powershell
ipconfig | Select-String "IPv4"
```

ดูบรรทัดที่เป็นวง LAN จริง เช่น `172.20.56.133` — **ห้ามใช้เลขที่ขึ้นต้นด้วย `169.254.`** เพราะเป็นเลขที่ Windows แจกเองตอนต่อเน็ตไม่ได้ ใช้งานไม่ได้จริง

### คำสั่งที่ 5 — เปิดพอร์ต 5000 ใน Firewall (ทำครั้งเดียว ต้องเป็น Administrator)

เปิด VS Code ด้วยการคลิกขวา → **Run as administrator** แล้วรัน

```powershell
New-NetFirewallRule -DisplayName "Image Processing Backend 5000" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow -Profile Any
```

เช็คว่าสร้างสำเร็จ
```powershell
Get-NetFirewallRule -DisplayName "Image Processing Backend 5000" | Select-Object DisplayName, Enabled, Action
```

### คำสั่งที่ 6 — สตาร์ทเซิร์ฟเวอร์

```powershell
$env:FLASK_DEBUG="0"; $env:FLASK_HOST="0.0.0.0"; $env:FLASK_PORT="5000"; .\.venv\Scripts\python.exe app.py
```

ต้องเห็นข้อความแบบนี้ **สองบรรทัด**

```
 * Running on http://127.0.0.1:5000
 * Running on http://172.20.56.133:5000
```

> **ถ้าเห็นแค่บรรทัด `127.0.0.1` บรรทัดเดียว = เครื่องอื่นต่อไม่ได้แน่นอน**
> แปลว่า `FLASK_HOST` ไม่ได้เป็น `0.0.0.0` ให้ตั้ง env var ใหม่แล้วรันอีกครั้ง

**ปล่อยหน้าต่างนี้เปิดค้างไว้ตลอดตอนเดโม** ปิดเมื่อไหร่เซิร์ฟเวอร์ดับทันที (กด `Ctrl + C` เพื่อหยุด)

---

## ทดสอบก่อนเรียกเพื่อน

เปิด terminal **อีกหน้าต่างหนึ่ง** (กดเครื่องหมาย `+` ใน VS Code) แล้วลอง

```powershell
curl.exe http://127.0.0.1:5000/api/health
curl.exe http://172.20.56.133:5000/api/health
```

> ต้องใช้ `curl.exe` ไม่ใช่ `curl` เฉยๆ เพราะใน PowerShell คำว่า `curl` เป็นชื่อเล่นของ
> `Invoke-WebRequest` ซึ่งรับ argument คนละแบบ

ทั้งสองคำสั่งต้องได้
```json
{"service":"Image Processing Backend","status":"ok"}
```

ถ้าอันแรกผ่านแต่อันที่สองไม่ผ่าน = ผูก host ผิด กลับไปดูคำสั่งที่ 6

ดูรายชื่อ operation ทั้งหมด
```powershell
curl.exe http://127.0.0.1:5000/api/operations
```

ทดสอบส่งภาพจริงโดยไม่ต้องใช้หน้าเว็บ
```powershell
curl.exe -X POST -F "image=@C:\path\to\photo.jpg" -F "operation=canny" http://127.0.0.1:5000/api/process
```

---

## แก้ปัญหา

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ModuleNotFoundError: No module named 'cv2'` | ลืมใช้ python ใน `.venv` | ใช้ `.\.venv\Scripts\python.exe app.py` ไม่ใช่ `python app.py` |
| `Address already in use` / พอร์ตไม่ว่าง | มีเซิร์ฟเวอร์ตัวเก่าค้างอยู่ | `Get-NetTCPConnection -LocalPort 5000` แล้ว `Stop-Process -Id <PID>` |
| เห็นแค่ `Running on http://127.0.0.1:5000` | `FLASK_HOST` ไม่ใช่ `0.0.0.0` | ตั้ง env var ตามคำสั่งที่ 6 |
| เครื่องเพื่อน ping ไม่เจอ | คนละวง Wi-Fi หรือ Wi-Fi เปิด AP isolation | ใช้ฮอตสปอตมือถือแทน ให้ทั้งสองเครื่องต่อฮอตสปอตเดียวกัน |
| ping ผ่านแต่เว็บต่อไม่ติด | Firewall บล็อกพอร์ต 5000 | คำสั่งที่ 5 |
| หน้าเว็บขึ้น error แต่ `curl.exe` ผ่าน | CORS | เช็ค `pip list \| findstr flask-cors` และดูว่ามี `CORS(app)` ใน `app.py` |
