# สถาปัตยกรรม — Image Processing Workshop

> โจทย์ต้นทาง: `docs/reference/Lecture 9 - Edge and Corner Detection (Workshop).pdf` หน้า 90
> 1. สร้าง Image Processing server Backend 1 เครื่อง และ Frontend 1 เครื่อง
> 2. เขียน Service ที่รับไฟล์ภาพจาก Client แล้วนำมาประมวลผลที่ฝั่ง Server
> 3. ส่งภาพผลลัพธ์ที่ได้จากการประมวลผลย้อนกลับไปให้ Client
> 4. ทำงานโดยใช้ REST API หรือ FAST API

## 1. ภาพรวม 2 เครื่อง

```
เครื่องผู้ใช้ (Client)                          เครื่องเซิร์ฟเวอร์ (Server)
python -m http.server 8000                     python app.py  (พอร์ต 5000)
┌───────────────────────────┐                  ┌────────────────────────────────┐
│ frontend/index.html       │                  │ backend/app.py  (Flask + CORS) │
│  - กรอก Backend URL       │                  │                                │
│  - เลือก operation        │ ①GET /api/health │  GET  /api/health              │
│  - เลือกไฟล์ภาพ           │─────────────────▶│  GET  /api/operations          │
│                           │ ②GET /api/operations                              │
│                           │                  │                                │
│  ภาพต้นฉบับ ──────────────│ ③POST /api/process──▶ cv2.imdecode()             │
│                           │  multipart/form-data │      ↓                     │
│                           │  image + operation   │  processing/edge.py        │
│                           │  + params            │  processing/corner.py      │
│                           │                  │      ↓ ประมวลผลจริงที่นี่      │
│  ภาพผลลัพธ์ ◀─────────────│ ④JSON + base64 PNG   cv2.imencode(".png")        │
└───────────────────────────┘                  └────────────────────────────────┘
```

**จุดสำคัญ: ฝั่ง client ไม่ประมวลผลภาพเองเลยแม้แต่บรรทัดเดียว**
`frontend/app.js` มีหน้าที่แค่ (1) เลือกภาพ (2) เลือก operation (3) ส่ง HTTP (4) แสดงภาพที่ได้กลับมา
ถ้าเผลอเขียนโค้ดประมวลผลภาพลง JS เมื่อไหร่ = ผิดโจทย์ข้อ 2 ทันที

## 2. ทำไมโครงสร้างนี้ไม่เหมือน Image-Segmenter-mini-project

โปรเจกต์เดิม (`../Image-Segmenter-mini-project`) เขียนไว้ใน ARCHITECTURE ของมันเองว่า
*"การประมวลผลภาพทั้งหมดรันในเบราว์เซอร์ด้วย MediaPipe WASM — Flask ไม่ได้รันโมเดลเลย"*

โจทย์รอบนี้กลับด้านกันคนละขั้ว: **ต้องประมวลผลที่ server** ดังนั้น

| | Image Segmenter (ของเดิม) | Workshop นี้ |
|---|---|---|
| ประมวลผลที่ไหน | เบราว์เซอร์ (MediaPipe WASM) | เซิร์ฟเวอร์ (OpenCV + Python) |
| หน้าที่ของ backend | เสิร์ฟหน้าเว็บ + เก็บผลลัพธ์ | **ประมวลผลภาพ** (งานหลักทั้งหมด) |
| งานหนักอยู่ที่ | JavaScript | Python |
| จำนวนเครื่อง | 1 | 2 (โจทย์บังคับ) |

สิ่งที่ยืมมาจากโปรเจกต์เดิมคือ *วิธีทำงานเป็นทีม* (เอกสาร 4 ไฟล์ + แยก branch + ตกลง contract ก่อนเขียนโค้ด)
ไม่ใช่โครงสร้างโค้ด

## 3. โครงสร้างโฟลเดอร์

```
backend/
├── app.py                  Flask + CORS + 3 endpoint  ── เจตน์
├── requirements.txt
└── processing/
    ├── __init__.py         ทะเบียน OPERATIONS (จุดต่อของ 3 คน) ── เจตน์
    ├── edge.py             canny() + sobel()          ── Tshering Dorji
    └── corner.py           harris() + harris_nms() + contour_boxes() ── พงศภัค

frontend/
├── index.html              ช่อง Backend URL + operation list + upload ── เจตน์
├── app.js                  เรียก REST API 3 เส้น       ── เจตน์
└── style.css

docs/
├── ARCHITECTURE.md         ไฟล์นี้
├── API_CONTRACT.md         สัญญาระหว่าง 3 คน (แก้ต้องแจ้งกันก่อน)
├── TEAM_AND_WORKFLOW.md    งานของแต่ละคน + git workflow
├── TASK_CHECKLIST.md       เช็คลิสต์รายคน
└── reference/              สไลด์ Lecture 9 ที่ใช้เป็นโจทย์
```

## 4. ทำไมต้องมี `processing/__init__.py` เป็นทะเบียนกลาง

ถ้า `app.py` เขียนแบบตรงไปตรงมาว่า

```python
if operation == "canny":
    result = edge.canny(img, ...)
elif operation == "harris":
    result = corner.harris(img, ...)
```

ทุกครั้งที่ Tshering หรือบอสเพิ่มฟังก์ชันใหม่ **ต้องไปแก้ `app.py` ซึ่งเป็นไฟล์ของเจตน์** → 3 คนแย่งกันแก้ไฟล์เดียว → merge conflict ทุกรอบ

โครงปัจจุบันแก้ปัญหานี้ด้วยการให้ `app.py` อ่านจาก dict `OPERATIONS` แทน:

```python
op = OPERATIONS[operation]
result = op["func"](img_bgr, **params)
```

`app.py` ไม่รู้จักชื่อ operation ไหนเลยตั้งแต่ต้น — เพิ่ม operation ใหม่ = เพิ่ม 1 entry ใน `__init__.py`
และหน้าเว็บจะขึ้น dropdown ให้เองโดยไม่ต้องแก้ JS (เพราะ frontend ดึงรายชื่อจาก `GET /api/operations`)

## 5. ทำไมส่งภาพกลับเป็น base64 ไม่ใช่ไฟล์ PNG ดิบ

ทางเลือกมี 2 แบบ:

| วิธี | ข้อดี | ข้อเสีย |
|---|---|---|
| `send_file()` ส่ง PNG ดิบ | ขนาดเล็กกว่า ~33% | ตอน error ต้องเปลี่ยน content-type เป็น JSON → ฝั่ง JS ต้องเช็คสองแบบ |
| **JSON + base64 (ที่ใช้อยู่)** | response หน้าตาเดียวกันทั้งสำเร็จและ error, เอาไปใส่ `<img src>` ได้ตรงๆ, แถม metadata (ขนาดภาพ, params ที่ใช้จริง) มาด้วยได้ | ข้อมูลใหญ่ขึ้น ~33% |

งานนี้ภาพไม่เกิน 15 MB และรันในวง LAN ความสะดวกในการ debug สำคัญกว่าขนาดข้อมูล จึงเลือกแบบที่สอง
ถ้าจะเปลี่ยนไปใช้ `send_file()` ต้องแก้ทั้ง `app.py` และ `app.js` พร้อมกัน และต้องแจ้งทั้งทีม

## 6. ทำไม backend ผูกกับ `0.0.0.0` ไม่ใช่ `127.0.0.1`

`127.0.0.1` รับ request ได้จากเครื่องตัวเองเท่านั้น — เครื่องผู้ใช้ที่อยู่คนละเครื่องจะต่อไม่ติด
`0.0.0.0` แปลว่ารับจากทุก network interface เครื่องอื่นในวง LAN ถึงจะเรียกเข้ามาได้ (สไลด์หน้า 89)

ถ้าต่อไม่ติดทั้งที่ตั้งถูกแล้ว มักเป็น **Windows Firewall** บล็อกพอร์ต 5000 ขาเข้า — ดูวิธีแก้ใน README

## 7. ทำไมต้องเปิด CORS

frontend อยู่ที่ `http://<client>:8000` แต่ยิง request ไป `http://<server>:5000` → คนละ origin
เบราว์เซอร์จะบล็อกให้อัตโนมัติ (same-origin policy) ถ้า server ไม่ส่ง header `Access-Control-Allow-Origin` กลับมา
`CORS(app)` จาก `flask-cors` ทำหน้าที่นี้ (สไลด์หน้า 86)

อาการเวลาลืมเปิด: หน้าเว็บขึ้น "เชื่อมต่อไม่ได้" ทั้งที่เปิด URL เดียวกันในเบราว์เซอร์ตรงๆ แล้วเห็น JSON ปกติ
