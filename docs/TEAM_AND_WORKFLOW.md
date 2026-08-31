# การแบ่งงาน 3 คน — Image Processing Workshop

> **อ่าน [`API_CONTRACT.md`](API_CONTRACT.md) ให้จบก่อนเริ่มเขียนโค้ด** โดยเฉพาะหัวข้อ 1 (หน้าตาของฟังก์ชัน)
> และหัวข้อ 2 (การลงทะเบียน operation) เพราะเป็นจุดเดียวที่งานของ 3 คนมาบรรจบกัน

โครงสร้างทั้งหมด **มีอยู่แล้วและรันได้จริง** — งานของแต่ละคนคือทำของตัวเองให้ครบและทดสอบจริง ไม่ใช่เริ่มจากศูนย์

## ภาพรวม

| คน | รหัสนักศึกษา | หัวข้อ | ไฟล์หลัก (ไม่ชนกันเลย) | Branch |
|---|---|---|---|---|
| **Tshering Dorji** | 6710301001 | Edge Detection (Canny + Sobel) | `backend/processing/edge.py` | `feat/edge-detection` |
| **พงศภัค เทียบพิมพ์** | 6710301006 | Corner + Region (Harris + Bounding box) | `backend/processing/corner.py` | `feat/corner-detection` |
| **เจตน์** | 6710301022 | Flask backend + Frontend + Integration | `backend/app.py`, `frontend/*` | `feat/backend-frontend` |

**ไฟล์เดียวที่ทั้ง 3 คนแตะ** คือ `backend/processing/__init__.py` (ทะเบียน `OPERATIONS`) — แต่แก้กันคนละ block
ถ้า conflict ก็แก้ง่ายมากเพราะเป็น dict ที่แยกบรรทัดชัดเจน

**สถานะตั้งต้นของแต่ละฟังก์ชัน**

| ฟังก์ชัน | สถานะ | เจ้าของ |
|---|---|---|
| `edge.canny()` | เขียนแล้ว ทดสอบผ่าน | Tshering (ต้องทดลองพารามิเตอร์ต่อ) |
| `edge.sobel()` | stub — `NotImplementedError` | Tshering |
| `corner.harris()` | เขียนแล้ว ทดสอบผ่าน | บอส (ต้องทดลองพารามิเตอร์ต่อ) |
| `corner.harris_nms()` | stub — `NotImplementedError` | บอส |
| `corner.contour_boxes()` | stub — `NotImplementedError` | บอส |

---

## Tshering Dorji — Edge Detection

**ไฟล์ที่แก้**: `backend/processing/edge.py` (+ block `"canny"` / `"sobel"` ใน `__init__.py`)
**อ้างอิง**: สไลด์หน้า 6-22 · `docs/reference/canny-expected-output-slide-p17.png` คือหน้าตาผลลัพธ์ที่ควรได้

### งานที่ต้องทำ

1. **ตรวจ `canny()` ที่มีอยู่ว่ารันได้จริง** — เปิดหน้าเว็บ เลือก "Canny Edge Detection" อัปโหลดภาพ
   ผลที่ควรได้: พื้นดำ ขอบขาว เส้นบาง 1 พิกเซล เทียบกับภาพตัวอย่างจากสไลด์หน้า 17

2. **เขียน `sobel()`** — ขั้นตอนละเอียด 7 ข้ออยู่ใน docstring ของฟังก์ชันนั้นแล้ว
   จุดที่คนพลาดบ่อยที่สุดคือต้องใช้ `cv2.CV_64F` ไม่ใช่ `uint8` เพราะ gradient ติดลบได้
   ถ้าใช้ `uint8` ค่าลบจะถูกตัดเป็น 0 หมด แล้วขอบด้านหนึ่งจะหายไปเลย

3. **ทดลองพารามิเตอร์แล้วจดผล** (สไลด์หน้า 18-21) — อันนี้คือเนื้อหาที่ต้องเอาไปใส่รายงาน:
   - เปลี่ยน `blur_ksize` 1 → 5 → 15 → 31 ด้วยภาพเดิม เส้นขอบหายไปเรื่อยๆ อย่างไร
   - ใช้ภาพที่มี noise (ถ่ายในที่มืด/ISO สูง) เทียบกับภาพสะอาด แล้วอธิบายว่าทำไม Gaussian ถึงจำเป็น
   - ขยับ `low`/`high` ขึ้นพร้อมกัน ดูว่าขอบอ่อนหายไปตอนไหน (hysteresis หน้า 21)
   - ลองตั้ง `low` เท่ากับ `high` แล้วอธิบายว่าทำไมผลถึงแย่ลง (เพราะ hysteresis ใช้ไม่ได้แล้ว)

4. **Error handling** — ตั้ง `blur_ksize=2` (เลขคู่) แล้วต้องไม่ crash
   (มี `_to_odd()` กันไว้แล้ว ให้ยืนยันว่าทำงานจริง)

### สิ่งที่ส่งมอบ
`canny` และ `sobel` ใช้งานได้ครบผ่านหน้าเว็บ · มีภาพเปรียบเทียบผลของการปรับพารามิเตอร์อย่างน้อย 3 ชุดสำหรับรายงาน

### ระวัง
- **ห้ามแก้ `corner.py`** (ของบอส) และ **ห้ามแก้ `app.py`** (ของเจตน์)
- ถ้าอยากเพิ่มพารามิเตอร์ใหม่ ต้องเพิ่ม 2 ที่: ตัวฟังก์ชัน **และ** block `params` ใน `__init__.py` ชื่อต้องตรงกันเป๊ะ

---

## พงศภัค เทียบพิมพ์ — Corner Detection + Region Labeling

**ไฟล์ที่แก้**: `backend/processing/corner.py` (+ block `"harris"` / `"harris_nms"` / `"contour_boxes"` ใน `__init__.py`)
**อ้างอิง**: สไลด์หน้า 24-31 (Harris) และหน้า 37-43 (Region labeling / Bounding box)

### งานที่ต้องทำ

1. **ตรวจ `harris()` ที่มีอยู่** — เลือก "Harris Corner Detection" อัปโหลดภาพที่มีมุมชัดๆ
   (ตึก, กระดานหมากรุก, กล่อง)
   ผลที่ควรได้: จุดแดงเกาะตามมุม **เป็นกระจุก** ไม่ใช่จุดเดียว — นี่คือปัญหาที่ข้อ 2 ต้องแก้

2. **เขียน `harris_nms()`** — non-maximum suppression รัศมี 10 พิกเซล ตามสไลด์หน้า 30
   วิธี dilate trick มีขั้นตอนครบ 7 ข้อใน docstring แล้ว
   แนวคิดหลักที่ต้องเข้าใจ: `cv2.dilate` แทนค่าทุกพิกเซลด้วย "ค่าสูงสุดในละแวก" ดังนั้นพิกเซลที่
   `response == local_max` ก็คือพิกเซลที่แรงที่สุดในละแวกของตัวเอง
   จุดพลาดบ่อย: numpy ใช้ `(แถว, คอลัมน์) = (y, x)` แต่ `cv2.circle` รับ `(x, y)` สลับกัน

3. **เขียน `contour_boxes()`** — ตอบคำถามในสไลด์หน้า 37 ว่า *"จะบอกคอมพิวเตอร์ยังไงว่าภาพนี้มี 9 วัตถุ"*
   ขั้นตอนครบ 6 ข้ออยู่ใน docstring
   จุดที่ต้องตัดสินใจเอง: `THRESH_BINARY` หรือ `THRESH_BINARY_INV` ขึ้นกับว่าวัตถุในภาพเข้มหรือสว่างกว่าพื้นหลัง
   **ต้องลองทั้งสองแบบแล้วอธิบายในรายงานได้ว่าทำไมเลือกแบบนั้น**

4. **ทดลองแล้วจดผลสำหรับรายงาน**:
   - `harris` เทียบ `harris_nms` ด้วยภาพเดียวกัน จำนวนจุดลดลงเท่าไหร่
   - ปรับ `radius` 3 → 10 → 30 จุดหายไปตามที่คาดไหม
   - ปรับ `k` 0.04 → 0.15 จำนวนมุมเปลี่ยนไปทางไหน (k สูง = เข้มงวดขึ้น)
   - `contour_boxes` กับภาพที่นับวัตถุด้วยตาได้ จำนวนกล่องตรงกับที่นับไหม ถ้าไม่ตรงเพราะอะไร

### สิ่งที่ส่งมอบ
`harris`, `harris_nms`, `contour_boxes` ใช้งานได้ครบผ่านหน้าเว็บ · มีภาพเปรียบเทียบก่อน/หลังทำ NMS ·
ตอบได้ว่าภาพทดสอบมีกี่วัตถุ

### ระวัง
- **ห้ามแก้ `edge.py`** (ของ Tshering) และ **ห้ามแก้ `app.py`** (ของเจตน์)
- `cv2.cornerHarris` ต้องการภาพแบบ `float32` — `_corner_response()` แปลงให้แล้ว ถ้าเขียนฟังก์ชันใหม่เองอย่าลืม
- ห้าม `print()` หรือ `cv2.imshow()` ในไฟล์นี้ — เครื่อง server ไม่มีจอ และ `imshow` จะทำให้ request ค้าง

---

## เจตน์ — Flask Backend + Frontend + Integration

**ไฟล์ที่แก้**: `backend/app.py`, `backend/processing/__init__.py`, `frontend/index.html`,
`frontend/app.js`, `frontend/style.css`, `README.md`
**อ้างอิง**: สไลด์หน้า 84-89 (REST API + Flask + CORS + วิธีเดโม 2 เครื่อง)

### งานที่ต้องทำ

1. **ตรวจ 3 endpoint ว่าทำงานถูก** — `GET /api/health`, `GET /api/operations`, `POST /api/process`
   ทดสอบด้วย curl ก่อน แล้วค่อยทดสอบผ่านหน้าเว็บ

2. **ทดสอบ error path ให้ครบ** (ต้องตอบ JSON ทุกกรณี ห้ามหลุดเป็นหน้า HTML error ของ Flask):

   | เคส | ควรได้ |
   |---|---|
   | ไม่แนบไฟล์ | 400 `No image uploaded` |
   | `operation` ไม่รู้จัก | 400 `Unknown operation` |
   | พารามิเตอร์เกินช่วง min/max | 400 พร้อมบอกช่วงที่ถูก |
   | อัปโหลดไฟล์ที่ไม่ใช่รูป (เช่น .txt) | 400 `Cannot decode image` |
   | ไฟล์เกิน 15 MB | 413 |
   | เลือก operation ที่ยังเป็น stub | 501 พร้อมชื่อเจ้าของงาน |

3. **เดโม 2 เครื่องจริง** (ข้อนี้สำคัญที่สุดของงานคุณ เพราะเป็นเกณฑ์ของโจทย์ข้อ 1):
   - รัน backend บนเครื่อง A ด้วย `python app.py` แล้วหา IP ด้วย `ipconfig`
   - รัน `python -m http.server 8000` ในโฟลเดอร์ `frontend/` บนเครื่อง B
   - บนเครื่อง B กรอก `http://<IP เครื่อง A>:5000` แล้วอัปโหลดภาพให้ผ่าน
   - **ถ้าต่อไม่ติด ตัวต้องสงสัยอันดับ 1 คือ Windows Firewall ไม่ใช่โค้ด** วิธีเปิดพอร์ตอยู่ใน README

4. **ห้ามแก้ 3 อย่างนี้โดยไม่แจ้งทีม** — เป็นตัวกันพลาดที่ตั้งใจใส่ไว้:
   - `MAX_CONTENT_LENGTH = 15 MB` (กัน RAM หมด)
   - การ validate `min`/`max` ใน `parse_params()` (กัน server crash จากค่าที่ client ส่งมั่ว)
   - `debug` อ่านจาก env var ไม่ใช่ hardcode `True` (Flask debug mode เปิดช่องให้รันโค้ดจากระยะไกลได้)

5. **ตรวจว่า frontend ไม่มีโค้ดประมวลผลภาพ** — ถ้ามีเมื่อไหร่คือผิดโจทย์ข้อ 2 ทันที

6. **Integration** — หลัง Tshering และบอส push แล้ว `git pull` มารวม ทดสอบว่า operation ทั้ง 5 ตัวขึ้นใน dropdown
   และเรียกได้ครบ (dropdown สร้างอัตโนมัติจาก `/api/operations` จึงไม่ต้องแก้ JS)

7. **อัปเดต README** ให้ตรงกับของจริงเสมอ

### สิ่งที่ส่งมอบ
backend รันได้ทันทีด้วย `python app.py` · เดโม 2 เครื่องผ่านจริง · error ทุกเคสตอบ JSON ถูกต้อง ·
เป็นคนสุดท้ายที่ merge แล้วเดโมทั้งระบบ end-to-end ได้

---

## งานร่วมกันของทุกคน

| งาน | รายละเอียด |
|---|---|
| ทดสอบของตัวเองก่อนเปิด PR | เปิด F12 → Console ไม่มี error สีแดง |
| อัปเดต `API_CONTRACT.md` ถ้า contract เปลี่ยน | เพิ่ม param / เปลี่ยนชื่อฟังก์ชัน / เปลี่ยน element id |
| Review PR ของอีก 2 คน | อย่างน้อยอ่าน diff คร่าวๆ ก่อนกด approve |
| รายงาน/สไลด์นำเสนอ | แต่ละคนเขียนส่วนของตัวเอง: ทฤษฎีจากสไลด์ + ผลการทดลองพารามิเตอร์ + ปัญหาที่เจอและวิธีแก้ |

---

## Git Workflow — main / develop / feature

```
main ──────────────────────────────────●   ส่งงาน/เดโมเท่านั้น ห้าม commit ตรงเข้ามา
                                        ↑ PR (เจตน์เป็นคนกด หลังเดโมผ่าน)
develop ───●────●────●────●────●────●───●   เส้นรวมงานระหว่างทาง ทุก PR เข้าที่นี่ก่อน
           ↑         ↑         ↑
   feat/edge-detection   feat/corner-detection   feat/backend-frontend
      (Tshering)              (บอส)                  (เจตน์)
```

**ทำไมต้องมี `develop` คั่น ไม่ merge เข้า `main` ตรงๆ**
`main` ต้องอยู่ในสภาพที่เปิดมาเดโมได้ทันทีตลอดเวลา ถ้าใครเผลอ merge โค้ดที่ยังพังเข้า `main`
แล้ววันนั้นครูขอดูงานพอดี = จบ ส่วน `develop` พังได้ไม่เป็นไร เพราะยังไม่ใช่ของที่เอาไปโชว์

**เส้นทางของงานหนึ่งชิ้น**

```bash
# 1. เริ่มงาน — แตก branch จาก develop เสมอ ไม่ใช่จาก main
git checkout develop
git pull origin develop
git checkout -b feat/corner-detection

# 2. ทำงาน แล้ว commit ทีละเรื่อง
git add backend/processing/corner.py
git commit -m "feat(corner): เพิ่ม non-maximum suppression รัศมี 10 พิกเซล"

# 3. ก่อน push ดึงของใหม่จาก develop มารวมก่อน แก้ conflict ที่เครื่องตัวเอง
git pull origin develop
git push origin feat/corner-detection

# 4. เปิด PR บน GitHub: feat/corner-detection --> develop
#    ให้อีก 2 คนอ่าน diff แล้ว approve ก่อน merge
```

**ตอนจะส่งงาน** (เจตน์เป็นคนทำคนเดียว หลังเดโม 2 เครื่องผ่านแล้ว)

```bash
# PR: develop --> main
git checkout main
git merge develop
git push origin main
```

**กฎของ branch**

| Branch | ใครแตะได้ | commit ตรงได้ไหม |
|---|---|---|
| `main` | เจตน์ (ผ่าน PR จาก develop เท่านั้น) | ไม่ได้ |
| `develop` | ทุกคน (ผ่าน PR จาก feature branch) | ไม่ควร |
| `feat/*` | เจ้าของ branch นั้นคนเดียว | ได้ |

**รูปแบบ commit message**: `<type>(<scope>): <สรุปสั้นๆ>`

- `feat(edge): เพิ่ม Sobel gradient magnitude`
- `feat(corner): เพิ่ม region labeling + bounding box`
- `fix(backend): ตอบ 501 แทน 500 เมื่อฟังก์ชันยังไม่ได้เขียน`
- `docs(readme): เพิ่มวิธีเปิดพอร์ต 5000 บน Windows Firewall`

---

## ลำดับความสำคัญถ้าเวลาไม่พอ

1. **ต้องมี** — เดโม 2 เครื่องผ่าน (เจตน์) + `canny` ใช้งานได้ (Tshering) + `harris` ใช้งานได้ (บอส)
   ครบ 3 อย่างนี้ = ตอบโจทย์ทั้ง 4 ข้อของ workshop แล้ว
2. **ควรมี** — `sobel` (Tshering) + `harris_nms` (บอส) + ผลการทดลองพารามิเตอร์สำหรับรายงาน
3. **ถ้าเวลาเหลือ** — `contour_boxes` + นับจำนวนวัตถุ + ปรับ UX หน้าเว็บ

ตัดข้อ 3 ก่อนเสมอ **อย่าตัดข้อ 1** เพราะเป็นเกณฑ์ขั้นต่ำที่โจทย์บังคับ
