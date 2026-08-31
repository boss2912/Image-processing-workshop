# Image Processing Workshop — Client/Server ด้วย REST API

Workshop ท้าย **Lecture 9 — Edge and Corner Detection** วิชา 310-3311 Image Processing

รับไฟล์ภาพจากเครื่องผู้ใช้ → ส่งไปประมวลผลที่เครื่องเซิร์ฟเวอร์ด้วย OpenCV → ส่งภาพผลลัพธ์กลับมาแสดง
โดยคุยกันผ่าน REST API (Flask + CORS ตามสไลด์หน้า 84-89)

## โจทย์ต้นทาง

จาก `docs/reference/Lecture 9 - Edge and Corner Detection (Workshop).pdf` หน้า 90

1. สร้าง Image Processing server Backend ขึ้นมา 1 เครื่อง และ Frontend 1 เครื่อง
2. เขียน Service ที่รับไฟล์ภาพจาก Client แล้วนำมาประมวลผลที่ฝั่ง Server
3. ส่งภาพผลลัพธ์ที่ได้จากการประมวลผลย้อนกลับไปให้ Client
4. ทำงานโดยใช้ REST API หรือ FAST API

> **หมายเหตุเรื่องข้อ 4**: REST API คือ*รูปแบบสถาปัตยกรรม* ส่วน FastAPI คือ*ไลบรารีตัวหนึ่ง*ที่ใช้สร้าง REST API
> โปรเจกต์นี้ใช้ **Flask** สร้าง REST API ซึ่งตรงกับคู่มือที่อาจารย์ให้ไว้ในสไลด์หน้า 86-89 (`request.files`, `CORS(app)`, `python app.py`)

## ทีมผู้จัดทำ

| รหัสนักศึกษา | ชื่อ | ส่วนที่รับผิดชอบ |
|---|---|---|
| 6710301001 | Mr. Tshering Dorji | Edge Detection — Canny + Sobel |
| 6710301006 | นาย พงศภัค เทียบพิมพ์ | Corner Detection + Region Labeling — Harris + Bounding box |
| 6710301022 | นาย เจตน์ - | Flask Backend + Frontend + Integration |

## Operation ที่มีให้เลือก

| Operation | ทำอะไร | อ้างอิงสไลด์ |
|---|---|---|
| Canny Edge Detection | หาขอบวัตถุ 5 ขั้นตอนของ Canny | หน้า 9-22 |
| Sobel Gradient Magnitude | ความแรงของ gradient (ขั้นที่ 2 ของ Canny) | หน้า 11-12 |
| Harris Corner Detection | หามุมของวัตถุ | หน้า 24-31 |
| Harris + Non-maximum Suppression | ลดจุดมุมซ้ำในรัศมีที่กำหนด | หน้า 30 |
| Region Labeling + Bounding Box | นับวัตถุและตีกรอบ | หน้า 37-43 |

---

## วิธีรัน

### กรณีที่ 1 — ทดสอบบนเครื่องเดียว

**หน้าต่างที่ 1: Backend**

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

จะเห็นข้อความ `Running on http://0.0.0.0:5000`

**หน้าต่างที่ 2: Frontend**

```powershell
cd frontend
python -m http.server 8000
```

เปิดเบราว์เซอร์ที่ **http://localhost:8000** — หน้าเว็บจะเชื่อมต่อ `http://127.0.0.1:5000` ให้อัตโนมัติ

---

### กรณีที่ 2 — เดโม 2 เครื่องจริง (ตามโจทย์ข้อ 1)

**บนเครื่องเซิร์ฟเวอร์**

```powershell
cd backend
python app.py
```

หา IP ของเครื่องนี้:

```powershell
ipconfig
```

ดูบรรทัด **IPv4 Address** เช่น `192.168.1.100`

จากนั้น **เปิดพอร์ต 5000 ใน Windows Firewall** (ถ้าไม่ทำ เครื่องอื่นจะต่อไม่ติดแม้โค้ดถูกทุกอย่าง)
เปิด PowerShell แบบ **Run as Administrator** แล้วรัน:

```powershell
New-NetFirewallRule -DisplayName "Image Processing Backend 5000" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

**บนเครื่องผู้ใช้**

คัดลอกโฟลเดอร์ `frontend/` มาไว้ที่เครื่องนี้ แล้วรัน:

```powershell
cd frontend
python -m http.server 8000
```

เปิด **http://localhost:8000** แล้วแก้ช่อง **Backend URL** เป็น IP ของเครื่องเซิร์ฟเวอร์:

```
http://192.168.1.100:5000
```

กด **เชื่อมต่อ** → เลือก operation → เลือกภาพ → กด **ประมวลผล**

> เครื่องทั้งสองต้องอยู่ในวง Wi-Fi / LAN เดียวกัน

---

## แก้ปัญหาที่เจอบ่อย

| อาการ | สาเหตุที่เป็นไปได้มากที่สุด | วิธีแก้ |
|---|---|---|
| หน้าเว็บขึ้น "เชื่อมต่อไม่ได้" แต่เปิด URL เดียวกันในเบราว์เซอร์ตรงๆ เห็น JSON ปกติ | CORS ไม่ทำงาน | เช็คว่า `pip install flask-cors` แล้ว และมี `CORS(app)` ใน `app.py` |
| ต่อจากอีกเครื่องไม่ติดเลย ทั้งที่เครื่อง server เปิดอยู่ | Windows Firewall บล็อกพอร์ต 5000 | รันคำสั่ง `New-NetFirewallRule` ข้างบน |
| ต่อไม่ติด และ ping IP นั้นก็ไม่ผ่าน | คนละวงเครือข่าย | ต่อ Wi-Fi ตัวเดียวกัน หรือปิด AP isolation ที่ router |
| กดประมวลผลแล้วขึ้น 501 | operation นั้นยังเป็น stub รอเจ้าของเขียน | ดู `docs/TASK_CHECKLIST.md` ว่าเป็นงานของใคร |
| อัปโหลดภาพใหญ่แล้วขึ้น 413 | ไฟล์เกิน 15 MB | ย่อภาพก่อน หรือแก้ `MAX_CONTENT_LENGTH` (ต้องแจ้งทีม) |
| `ModuleNotFoundError: No module named 'cv2'` | ลืม activate venv หรือยังไม่ได้ install | `.venv\Scripts\activate` แล้ว `pip install -r requirements.txt` |

---

## โครงสร้างโปรเจกต์

```
backend/
├── app.py                  Flask + CORS + 3 endpoint
├── requirements.txt
└── processing/
    ├── __init__.py         ทะเบียน OPERATIONS (จุดต่อของ 3 คน)
    ├── edge.py             Canny + Sobel
    └── corner.py           Harris + NMS + Bounding box

frontend/
├── index.html              ช่อง Backend URL + operation list + upload
├── app.js                  เรียก REST API (ไม่ประมวลผลภาพเอง)
└── style.css

docs/
├── ARCHITECTURE.md         ทำไมโครงสร้างเป็นแบบนี้
├── API_CONTRACT.md         สัญญาระหว่างงานของ 3 คน
├── TEAM_AND_WORKFLOW.md    งานของแต่ละคน + git workflow (main/develop/feature)
├── TASK_CHECKLIST.md       เช็คลิสต์รายคน
└── reference/              สไลด์ Lecture 9 ที่ใช้เป็นโจทย์
```

## REST API โดยย่อ

| Method | Endpoint | หน้าที่ |
|---|---|---|
| GET | `/api/health` | เช็คว่า backend ทำงานอยู่ |
| GET | `/api/operations` | รายชื่อ operation + พารามิเตอร์ (frontend ใช้สร้าง dropdown) |
| POST | `/api/process` | รับภาพ + operation + พารามิเตอร์ → คืนภาพผลลัพธ์ |

รายละเอียดเต็มอยู่ใน [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md)

## เอกสารทีม

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — ทำไมประมวลผลที่ server ไม่ใช่ที่เบราว์เซอร์
- [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md) — จุดต่อระหว่างงานของ 3 คน
- [`docs/TEAM_AND_WORKFLOW.md`](docs/TEAM_AND_WORKFLOW.md) — งานของแต่ละคน + git workflow
- [`docs/TASK_CHECKLIST.md`](docs/TASK_CHECKLIST.md) — เช็คลิสต์ก่อนบอกว่าเสร็จ
