# Image Processing Workshop — Client/Server

Workshop ท้าย Lecture 9 วิชา 310-3311 Image Processing

## โจทย์

1. สร้าง Image Processing server Backend ขึ้นมา 1 เครื่อง และ Frontend 1 เครื่อง
2. เขียน Service ที่รับไฟล์ภาพจาก Client แล้วนำมาประมวลผลที่ฝั่ง Server
3. ส่งภาพผลลัพธ์ที่ได้จากการประมวลผลย้อนกลับไปให้ Client
4. ทำงานโดยใช้ REST API หรือ FAST API

## โครงสร้าง

```
backend/                 รันบนเครื่องเซิร์ฟเวอร์
├── app.py               Flask REST API + Canny Edge Detection
└── requirements.txt

frontend/                รันบนเครื่องผู้ใช้
├── index.html
├── app.js               แก้ BACKEND_URL บรรทัดที่ 15
└── style.css
```

สองโฟลเดอร์นี้แยกกันสมบูรณ์ คัดลอกไปคนละเครื่องได้เลย

---

## เครื่องเซิร์ฟเวอร์ (backend)

### ติดตั้ง (ทำครั้งเดียว)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### หา IP ของเครื่องนี้

```powershell
ipconfig | Select-String "IPv4"
```

ดูบรรทัดที่เป็นวง LAN จริง เช่น `172.20.56.133` — **ห้ามใช้เลขที่ขึ้นต้นด้วย `169.254.`**

### เปิดพอร์ต 5000 ใน Firewall (ทำครั้งเดียว ต้องเปิด PowerShell แบบ Run as administrator)

```powershell
New-NetFirewallRule -DisplayName "Image Processing Backend 5000" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow -Profile Any
```

### รัน

```powershell
cd backend
.\.venv\Scripts\python.exe app.py
```

ต้องเห็น **สองบรรทัด**

```
 * Running on http://127.0.0.1:5000
 * Running on http://172.20.56.133:5000
```

ถ้าเห็นแค่บรรทัด `127.0.0.1` บรรทัดเดียว เครื่องอื่นจะต่อไม่ได้

ปล่อยหน้าต่างนี้เปิดค้างไว้ กด `Ctrl + C` เพื่อหยุด

---

## เครื่องผู้ใช้ (frontend)

### 1. แก้ IP ของเครื่องเซิร์ฟเวอร์

เปิด `frontend/app.js` แก้บรรทัดที่ 15

```js
const BACKEND_URL = "http://172.20.56.133:5000";
```

### 2. รัน

```powershell
cd frontend
python -m http.server 8000
```

เปิดเบราว์เซอร์ที่ **http://localhost:8000**

> ไม่ต้อง `pip install` อะไรเลย เพราะเครื่องนี้ไม่ได้ประมวลผลภาพ
> และ **ห้ามดับเบิลคลิก `index.html` เปิดตรงๆ** จะได้ URL แบบ `file://` ซึ่งเบราว์เซอร์จะบล็อกการเรียก backend

### 3. ใช้งาน

เลือกรูป → กดประมวลผล → ภาพซ้ายคือต้นฉบับ ภาพขวาคือผลลัพธ์ที่เครื่องเซิร์ฟเวอร์ส่งกลับมา

---

## REST API

| Method | Endpoint | รับ | คืน |
|---|---|---|---|
| POST | `/api/process` | `multipart/form-data` field ชื่อ `image` | JSON `{"success": true, "image": "data:image/png;base64,..."}` |

กรณีผิดพลาดคืน `{"success": false, "error": "..."}` พร้อม HTTP 400 หรือ 500

---

## ต่อไม่ติด

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ping <ip>` ไม่ผ่าน | คนละวง Wi-Fi หรือ Wi-Fi เปิด AP isolation | ใช้ฮอตสปอตมือถือ ให้ทั้งสองเครื่องต่ออันเดียวกัน |
| ping ผ่าน แต่หน้าเว็บต่อไม่ติด | Windows Firewall บล็อกพอร์ต 5000 | รันคำสั่ง `New-NetFirewallRule` ข้างบน |
| หน้าเว็บ error แต่เปิด URL ตรงๆ ได้ | CORS | เช็คว่ามี `CORS(app)` และติดตั้ง `flask-cors` แล้ว |
| `ModuleNotFoundError: No module named 'cv2'` | ไม่ได้ใช้ python ใน `.venv` | ใช้ `.\.venv\Scripts\python.exe app.py` |
