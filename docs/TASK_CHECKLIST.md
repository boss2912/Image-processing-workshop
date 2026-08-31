# เช็คลิสต์รายคน

ติ๊กเมื่อ **ทดสอบผ่านหน้าเว็บจริงแล้ว** ไม่ใช่แค่รันฟังก์ชันใน Python ตรงๆ

---

## Tshering Dorji — `backend/processing/edge.py`

### canny() — เขียนไว้ให้แล้ว ต้องตรวจและทดลอง

- [ ] เปิดหน้าเว็บ เลือก "Canny Edge Detection" อัปโหลดภาพ แล้วได้ผลออกมาจริง
- [ ] ผลลัพธ์หน้าตาใกล้เคียง `docs/reference/canny-expected-output-slide-p17.png` (พื้นดำ ขอบขาว เส้นบาง)
- [ ] ตั้ง `blur_ksize` เป็นเลขคู่ (เช่น 2, 4) แล้ว server ไม่ crash
- [ ] ตั้ง `blur_ksize = 31` แล้วเห็นว่าเส้นขอบลดลงชัดเจนเทียบกับ 5
- [ ] ตั้ง `low = high` แล้วอธิบายได้ว่าทำไมผลถึงแย่ลง
- [ ] ทดสอบครบ 3 ภาพ: ภาพถ่ายทั่วไป / ภาพลายเส้น / ภาพที่มี noise

### sobel() — ต้องเขียนเอง

- [ ] แปลงเป็น grayscale
- [ ] เบลอด้วย Gaussian ก่อน (ใช้ `_to_odd(blur_ksize)`)
- [ ] `cv2.Sobel` แกน x และ y โดยใช้ `cv2.CV_64F` (ไม่ใช่ uint8)
- [ ] หา magnitude ด้วย `np.sqrt(gx**2 + gy**2)` หรือ `cv2.magnitude`
- [ ] `cv2.normalize(..., 0, 255, cv2.NORM_MINMAX).astype(np.uint8)`
- [ ] ลบ `raise NotImplementedError` ออก แล้ว `return` ผลลัพธ์
- [ ] เรียกผ่านหน้าเว็บได้ ไม่ขึ้น 501 อีกต่อไป
- [ ] ผลที่ได้เป็นภาพเทาที่ขอบสว่าง **ไม่ใช่** ภาพขาวดำเส้นบางแบบ Canny (ถ้าเหมือน Canny แปลว่าทำผิด)

### สำหรับรายงาน

- [ ] เก็บภาพเปรียบเทียบผลของ `blur_ksize` อย่างน้อย 3 ค่า
- [ ] เก็บภาพเปรียบเทียบผลของ `low`/`high` อย่างน้อย 3 คู่
- [ ] เก็บภาพเปรียบเทียบ Canny กับ Sobel บนภาพเดียวกัน แล้วอธิบายว่าต่างกันเพราะอะไร

---

## พงศภัค เทียบพิมพ์ — `backend/processing/corner.py`

### harris() — เขียนไว้ให้แล้ว ต้องตรวจและทดลอง

- [ ] เปิดหน้าเว็บ เลือก "Harris Corner Detection" อัปโหลดภาพที่มีมุมชัด แล้วได้จุดแดงจริง
- [ ] เห็นด้วยตาว่าจุดแดงเกาะเป็น **กระจุก** ต่อ 1 มุม (นี่คือปัญหาที่ `harris_nms` ต้องแก้)
- [ ] ปรับ `threshold` 0.001 → 0.01 → 0.1 แล้วเห็นจำนวนจุดลดลง
- [ ] ปรับ `k` 0.04 → 0.15 แล้วอธิบายได้ว่าทำไมจุดถึงลดลง
- [ ] ลองภาพที่มีแต่เส้นตรงยาวๆ (ไม่มีมุม) แล้วยืนยันว่าไม่ควรได้จุดมาก

### harris_nms() — ต้องเขียนเอง

- [ ] เรียก `_corner_response()` ที่มีอยู่แล้ว (ไม่ copy โค้ด cornerHarris มาเขียนซ้ำ)
- [ ] สร้าง kernel วงกลม `cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*radius+1, 2*radius+1))`
- [ ] `local_max = cv2.dilate(response, kernel)`
- [ ] `mask = (response == local_max) & (response > threshold * response.max())`
- [ ] `ys, xs = np.nonzero(mask)` แล้ววาดด้วย `cv2.circle(output, (int(x), int(y)), ...)`
- [ ] **ตรวจลำดับ x/y ให้ถูก** — numpy เป็น (y, x) แต่ cv2.circle รับ (x, y)
      ถ้าสลับผิด จุดจะไปโผล่ผิดตำแหน่งแบบพลิกแนวทแยง
- [ ] ลบ `raise NotImplementedError` ออก
- [ ] จำนวนจุดน้อยกว่า `harris()` อย่างชัดเจนบนภาพเดียวกัน
- [ ] ปรับ `radius` 3 → 10 → 30 แล้วจุดลดลงเรื่อยๆ ตามที่คาด

### contour_boxes() — ต้องเขียนเอง

- [ ] `cv2.threshold` แปลงเป็นภาพ binary
- [ ] ลองทั้ง `THRESH_BINARY` และ `THRESH_BINARY_INV` แล้วเลือกอันที่ถูกกับภาพทดสอบ
- [ ] `cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)`
- [ ] กรอง contour ที่ `cv2.contourArea(c) < min_area` ทิ้ง
- [ ] วาดกรอบด้วย `cv2.boundingRect` + `cv2.rectangle`
- [ ] เขียนจำนวนวัตถุลงบนภาพด้วย `cv2.putText`
- [ ] ลบ `raise NotImplementedError` ออก
- [ ] หาภาพที่นับวัตถุด้วยตาได้ แล้วจำนวนกล่องตรงกับที่นับ

### สำหรับรายงาน

- [ ] ภาพเปรียบเทียบ `harris` กับ `harris_nms` บนภาพเดียวกัน พร้อมจำนวนจุดของทั้งคู่
- [ ] ภาพเปรียบเทียบผลของ `radius` อย่างน้อย 3 ค่า
- [ ] ภาพผลลัพธ์ `contour_boxes` พร้อมคำอธิบายว่าเลือก THRESH แบบไหนและทำไม

---

## เจตน์ — `backend/app.py` + `frontend/*`

### Endpoint

- [ ] `curl http://127.0.0.1:5000/api/health` ได้ `{"status":"ok","service":"Image Processing Backend"}`
- [ ] `curl http://127.0.0.1:5000/api/operations` ได้ครบทั้ง 5 operation
- [ ] `POST /api/process` ด้วย canny แล้วได้ภาพกลับมาจริง

### Error path (ต้องได้ JSON ทุกเคส ไม่ใช่หน้า HTML error ของ Flask)

- [ ] ไม่แนบไฟล์ → 400 `No image uploaded`
- [ ] `operation=blur` (ไม่มีจริง) → 400 `Unknown operation`
- [ ] `low=999` (เกิน max 255) → 400 พร้อมบอกช่วงที่ถูกต้อง
- [ ] อัปโหลดไฟล์ .txt → 400 `Cannot decode image`
- [ ] อัปโหลดไฟล์เกิน 15 MB → 413
- [ ] เลือก operation ที่ยังเป็น stub → 501 พร้อมชื่อเจ้าของงาน

### Frontend

- [ ] กด "เชื่อมต่อ" ด้วย URL ถูก → ขึ้นข้อความสีเขียวพร้อมจำนวน operation
- [ ] กด "เชื่อมต่อ" ด้วย URL ผิด → ขึ้นข้อความสีแดง ไม่ค้าง
- [ ] เปลี่ยน operation ใน dropdown แล้วช่องกรอกพารามิเตอร์เปลี่ยนตาม
- [ ] เลือกไฟล์แล้วภาพต้นฉบับขึ้นทันที (ยังไม่ต้องกดประมวลผล)
- [ ] กดประมวลผลแล้วภาพผลลัพธ์ขึ้นทางขวา พร้อมเวลาไป-กลับเป็น ms
- [ ] ปุ่ม "บันทึกภาพผลลัพธ์" ดาวน์โหลดไฟล์ .png ได้จริง
- [ ] เปิด F12 → Console ไม่มี error สีแดง (ยกเว้นตอนตั้งใจทดสอบ error)
- [ ] **ยืนยันว่าใน `app.js` ไม่มีโค้ดประมวลผลภาพเลย** (ถ้ามี = ผิดโจทย์ข้อ 2)

### เดโม 2 เครื่อง (สำคัญที่สุด)

- [ ] เครื่อง A: `python app.py` แล้วเห็น `Running on http://0.0.0.0:5000`
- [ ] เครื่อง A: `ipconfig` จด IPv4 Address ไว้
- [ ] เครื่อง A: เปิดพอร์ต 5000 ขาเข้าใน Windows Firewall แล้ว
- [ ] เครื่อง B: `python -m http.server 8000` ในโฟลเดอร์ `frontend/`
- [ ] เครื่อง B: เปิด `http://localhost:8000` แล้วกรอก backend URL เป็น IP ของเครื่อง A
- [ ] เครื่อง B: อัปโหลดภาพแล้วได้ผลลัพธ์กลับมาจริง
- [ ] **ทั้งสองเครื่องอยู่วง Wi-Fi/LAN เดียวกัน** (ถ้าคนละวงจะต่อไม่ติดแน่นอน)

### ก่อนส่งงาน

- [ ] merge งานของทั้ง 3 คนเข้า `develop` แล้วทดสอบซ้ำทั้งหมด
- [ ] operation ทั้ง 5 ตัวขึ้นใน dropdown และเรียกได้ครบ
- [ ] PR จาก `develop` เข้า `main`
- [ ] README ตรงกับของจริง (คำสั่ง คัดลอกไปวางแล้วรันได้เลย)
