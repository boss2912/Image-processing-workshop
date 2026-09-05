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
├── app.js
└── style.css
```

สองโฟลเดอร์นี้แยกกันสมบูรณ์ คัดลอกไปคนละเครื่องได้เลย

---

## รันทั้ง 2 ตัวพร้อมกันบนเครื่องเดียว (ผ่าน VS Code Terminal)

ใช้ตอนพัฒนาหรือตอนซ้อมก่อนเดโม ยังไม่ต้องใช้ 2 เครื่อง
หลักการคือ **เปิด terminal 2 อัน** อันหนึ่งรัน backend อีกอันรัน frontend แล้วปล่อยค้างไว้ทั้งคู่

### ขั้นที่ 1 — เปิด VS Code ที่โฟลเดอร์ `Image-processing-workshop`

ต้องเปิดที่โฟลเดอร์นี้ ไม่ใช่เปิดที่ `backend` หรือ `frontend` อย่างใดอย่างหนึ่ง

### ขั้นที่ 2 — เปิด terminal อันแรก แล้วรัน backend

กด **Ctrl + `** (ปุ่ม backtick ใต้ปุ่ม Esc) เพื่อเปิด terminal

```powershell
cd backend
.\.venv\Scripts\python.exe app.py
```

ต้องเห็น **สองบรรทัด** แบบนี้ แล้วปล่อยค้างไว้ ห้ามปิด

```
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

### ขั้นที่ 3 — แยก terminal อันที่สอง แล้วรัน frontend

กด **Ctrl + Shift + 5** (หรือกดไอคอน Split Terminal มุมขวาบนของ panel)
จะได้ terminal อันที่ 2 โผล่มาข้างๆ อันแรก **อันแรกยังรันอยู่ ไม่ได้ถูกปิด**

```powershell
cd frontend
python -m http.server 8000
```

> ถ้าขึ้นว่าหาโฟลเดอร์ `frontend` ไม่เจอ แปลว่า terminal อันที่ 2 เปิดมาอยู่ในโฟลเดอร์ `backend`
> ให้พิมพ์ `cd ..` ก่อนแล้วค่อย `cd frontend`

### ขั้นที่ 4 — เปิดเบราว์เซอร์

ไปที่ **http://localhost:8000** แล้วกด **เช็คการเชื่อมต่อ (GET)**
ถ้าขึ้น `ต่อได้: Image Processing Backend — status ok` แปลว่าทั้งสองตัวคุยกันได้แล้ว

### สรุปหน้าตาที่ควรได้

| terminal | โฟลเดอร์ | คำสั่ง | ทำหน้าที่ |
|---|---|---|---|
| อันที่ 1 | `backend` | `.\.venv\Scripts\python.exe app.py` | เครื่องเซิร์ฟเวอร์ port 5000 |
| อันที่ 2 | `frontend` | `python -m http.server 8000` | เสิร์ฟหน้าเว็บ port 8000 |

**หยุดการทำงาน** กด `Ctrl + C` ในแต่ละ terminal (ต้องกดทั้ง 2 อัน)

**ข้อควรระวัง** ห้ามรันสองคำสั่งนี้ใน terminal อันเดียวกัน เพราะ `app.py` จะยึด terminal ไว้ไม่คืน
พิมพ์คำสั่งที่สองไม่ได้จนกว่าจะกด Ctrl + C ปิดตัวแรกทิ้ง ซึ่งทำแบบนั้นแล้ว backend จะดับ

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

### 1. รัน

```powershell
cd frontend
python -m http.server 8000
```

เปิดเบราว์เซอร์ที่ **http://localhost:8000**

> ไม่ต้อง `pip install` อะไรเลย เพราะเครื่องนี้ไม่ได้ประมวลผลภาพ
> และ **ห้ามดับเบิลคลิก `index.html` เปิดตรงๆ** จะได้ URL แบบ `file://` ซึ่งเบราว์เซอร์จะบล็อกการเรียก backend

### 2. ใช้งาน

พิมพ์ IP ของเครื่องเซิร์ฟเวอร์ใส่ช่อง **Backend URL** เช่น `http://172.20.56.133:5000`
แล้วกด **เช็คการเชื่อมต่อ (GET)** ก่อน ถ้าขึ้น `ต่อได้: Image Processing Backend` แปลว่าต่อถึงแล้ว

จากนั้นเลือกรูป → กด **ประมวลผล (POST)** → ภาพซ้ายคือต้นฉบับ ภาพขวาคือผลลัพธ์ที่เครื่องเซิร์ฟเวอร์ส่งกลับมา

---

## REST API

| Method | Endpoint | รับ | คืน |
|---|---|---|---|
| GET | `/api/health` | — | JSON `{"status": "ok", "service": "Image Processing Backend"}` |
| POST | `/api/process` | `multipart/form-data` field ชื่อ `image` | JSON `{"success": true, "image": "data:image/png;base64,..."}` |

กรณีผิดพลาดคืน `{"success": false, "error": "..."}` พร้อม HTTP 400

## ปุ่มไหน เรียกโค้ดตัวไหน

| ปุ่มในหน้าเว็บ | ไฟล์ frontend | HTTP | `def` ใน `backend/app.py` |
|---|---|---|---|
| เช็คการเชื่อมต่อ (GET) | `app.js` ส่วนที่ 2 | GET `/api/health` | `health_check()` |
| ประมวลผล (POST) | `app.js` ส่วนที่ 4 | POST `/api/process` | `process()` |
| — (`process()` เรียกต่อเอง) | — | — | `find_edges_with_canny()` |

`backend/app.py` มี 3 `def` เท่านี้ ไม่มีตัวไหนที่เขียนทิ้งไว้เฉยๆ

---

## ต่อไม่ติด

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ping <ip>` ไม่ผ่าน | คนละวง Wi-Fi หรือ Wi-Fi เปิด AP isolation | ใช้ฮอตสปอตมือถือ ให้ทั้งสองเครื่องต่ออันเดียวกัน |
| ping ผ่าน แต่หน้าเว็บต่อไม่ติด | Windows Firewall บล็อกพอร์ต 5000 | รันคำสั่ง `New-NetFirewallRule` ข้างบน |
| หน้าเว็บ error แต่เปิด URL ตรงๆ ได้ | CORS | เช็คว่ามี `CORS(app)` และติดตั้ง `flask-cors` แล้ว |
| `ModuleNotFoundError: No module named 'cv2'` | ไม่ได้ใช้ python ใน `.venv` | ใช้ `.\.venv\Scripts\python.exe app.py` |
| ขึ้น `รอเกิน 5 วินาทีแล้ว server ไม่ตอบ` | พิมพ์ IP ผิด หรือยังไม่ได้เปิด `app.py` | เช็ค IP ด้วย `ipconfig` บนเครื่องเซิร์ฟเวอร์ |
| ขึ้น `รอเกิน 60 วินาทีแล้ว server ไม่ตอบ` | รูปใหญ่เกินไปหรือ Wi-Fi ช้ามาก | ลองรูปที่เล็กลง หรือย้ายเข้าใกล้ router |

### เรื่อง timeout

`frontend/app.js` ตั้งเวลารอไว้ไม่เท่ากัน 2 ค่า

| ปุ่ม | รอนานสุด | เหตุผล |
|---|---|---|
| เช็คการเชื่อมต่อ (GET) | 5 วินาที | `/api/health` ตอบแค่ JSON 2 บรรทัด วัดจริงได้ 0.003 วินาที |
| ประมวลผล (POST) | 60 วินาที | รูปมือถือ 22 MB บน localhost ใช้ 1 วินาที ผ่าน Wi-Fi ช้ากว่านี้หลายเท่า |

ถ้าไม่ตั้งไว้ พิมพ์ IP ที่ไม่มีอยู่ในวงแล้วกดปุ่ม หน้าเว็บจะค้างที่ `กำลังเช็ค ...` เป็นนาที
