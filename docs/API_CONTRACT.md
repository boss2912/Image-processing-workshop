# API / Interface Contract — ตกลงกันก่อนเริ่มเขียนโค้ด

> เอกสารนี้คือ "จุดต่อ" ระหว่างงานของ 3 คน **ถ้าจะเปลี่ยนอะไรในนี้ต้องแจ้งอีก 2 คนก่อน**
> ตราบใดที่ทุกคนทำตามสัญญานี้ จะเขียนโค้ดแยกกันได้โดยไม่ต้องรอใคร และไม่ชนกันตอน merge

---

## 1. สัญญาข้อสำคัญที่สุด: หน้าตาของฟังก์ชันประมวลผล

ทุกฟังก์ชันใน `backend/processing/edge.py` และ `backend/processing/corner.py` **ต้อง** มีหน้าตาแบบนี้:

```python
def ชื่อฟังก์ชัน(img_bgr, พารามิเตอร์1=ค่าเริ่มต้น, พารามิเตอร์2=ค่าเริ่มต้น, ...):
    ...
    return numpy_array
```

| ข้อกำหนด | รายละเอียด |
|---|---|
| พารามิเตอร์ตัวแรก | ชื่อ `img_bgr` เสมอ — เป็น numpy array 3 มิติ `(สูง, กว้าง, 3)` เรียงสี **BGR** ไม่ใช่ RGB |
| พารามิเตอร์ที่เหลือ | ต้องมีค่า default ทุกตัว และต้องเป็น `int` หรือ `float` เท่านั้น (เพราะส่งมาทาง HTTP form) |
| ค่าที่คืน | numpy array — จะเป็น grayscale 2 มิติ `(สูง, กว้าง)` หรือ BGR 3 มิติก็ได้ `cv2.imencode` รับได้ทั้งคู่ |
| ห้าม | `import` อะไรจาก `app.py` (จะเป็น circular import), แก้ไฟล์ของคนอื่น, `print()` หรือ `cv2.imshow()` (server ไม่มีจอ) |

**ฟังก์ชันที่ยังไม่ได้เขียน** ให้ `raise NotImplementedError("...")` ไว้ — `app.py` ดักไว้แล้วและจะตอบ HTTP 501
พร้อมข้อความนั้นกลับไปให้หน้าเว็บ ทำให้แยกออกจาก bug จริง (500) ได้ **ห้ามลบ raise ทิ้งเฉยๆ โดยไม่เขียนโค้ดแทน**

---

## 2. การลงทะเบียน operation — `backend/processing/__init__.py`

ไฟล์นี้เป็นของ **เจตน์** แต่ Tshering กับบอสต้องมาแก้เมื่อเพิ่ม/แก้ operation ของตัวเอง
(เป็นไฟล์เดียวที่ทั้ง 3 คนแตะ — แก้คนละ block กัน conflict ง่าย)

```python
"canny": {
    "label": "Canny Edge Detection",       # ข้อความใน dropdown
    "owner": "Tshering",                    # ไว้ดูตอน debug ว่าต้องตามใคร
    "func": edge.canny,                     # ฟังก์ชันจริง (ไม่ต้องใส่วงเล็บ)
    "params": {
        "low": {"type": "int", "default": 50, "min": 0, "max": 255,
                "label": "Threshold ต่ำ (hysteresis)"},
    },
},
```

**ชื่อ key ใน `params` ต้องตรงกับชื่อพารามิเตอร์ของฟังก์ชันเป๊ะๆ** เพราะ `app.py` เรียกด้วย `func(img_bgr, **params)`
สะกดผิด 1 ตัว = `TypeError: unexpected keyword argument` ทันที

`type` รับแค่ `"int"` กับ `"float"` — `app.py` ใช้ค่านี้ตัดสินว่าจะแปลงค่าจาก form ด้วย `int()` หรือ `float()`
และ `min`/`max` ถูกบังคับใช้จริงฝั่ง server (เกินช่วง → HTTP 400) ไม่ได้เป็นแค่คำใบ้ให้หน้าเว็บ

---

## 3. REST API — Browser → Flask

### `GET /api/health`
เช็คว่า backend ยังมีชีวิตและ URL ที่กรอกถูกต้อง

```json
{ "status": "ok", "service": "Image Processing Backend" }
```

### `GET /api/operations`
frontend เรียกตอนกด "เชื่อมต่อ" เพื่อสร้าง dropdown + ช่องกรอกพารามิเตอร์เอง
**ห้าม hardcode รายชื่อ operation ลงใน JS** เด็ดขาด (จะกลายเป็นต้องแก้สองที่ทุกครั้ง)

```json
{
  "success": true,
  "operations": [
    { "key": "canny", "label": "Canny Edge Detection", "owner": "Tshering",
      "params": { "low": {"type":"int","default":50,"min":0,"max":255,"label":"..."} } }
  ]
}
```

### `POST /api/process`
**Request** — `multipart/form-data` (ไม่ใช่ JSON เพราะต้องแนบไฟล์)

| field | ชนิด | ตัวอย่าง | บังคับ |
|---|---|---|---|
| `image` | ไฟล์ | รูป .jpg/.png | ✅ |
| `operation` | ข้อความ | `canny` | ✅ |
| ชื่อพารามิเตอร์ | ข้อความ (ตัวเลข) | `low=60`, `k=0.04` | ไม่ (ไม่ส่ง = ใช้ default) |

**Response 200**
```json
{
  "success": true,
  "operation": "canny",
  "params": { "blur_ksize": 5, "low": 60, "high": 180 },
  "width": 1091, "height": 1280,
  "image": "data:image/png;base64,iVBORw0KGgo..."
}
```
`image` เอาไปใส่ `<img src="...">` ได้ตรงๆ และใช้เป็น `href` ของปุ่มดาวน์โหลดได้เลย
`params` คือค่าที่ server **ใช้จริง** (หลังเติม default แล้ว) — ไว้ยืนยันว่าค่าที่กรอกส่งถึงจริง

**Response ที่ไม่สำเร็จ** — รูปแบบเดียวกันหมด ต่างที่ status code

| code | ความหมาย | ตัวอย่าง |
|---|---|---|
| 400 | client ส่งมาผิด | ไม่แนบไฟล์ / operation ไม่รู้จัก / พารามิเตอร์เกินช่วง / ไฟล์ไม่ใช่รูป |
| 413 | ไฟล์เกิน 15 MB | `MAX_CONTENT_LENGTH` |
| 501 | ฟังก์ชันยังไม่ได้เขียน | `NotImplementedError` จาก stub |
| 500 | โค้ดที่เขียนแล้วพัง | ต้องไปดู log ฝั่ง server |

```json
{ "success": false, "error": "ข้อความอธิบายเป็นภาษาที่คนอ่านรู้เรื่อง" }
```

---

## 4. Element id ในหน้าเว็บ (frontend)

`app.js` ผูกกับ id พวกนี้ตรงๆ **ห้ามเปลี่ยนชื่อโดยไม่แจ้ง**

`#backend-url` `#connect-btn` `#operation` `#operation-owner` `#params`
`#file-input` `#process-btn` `#status` `#source-image` `#result-image` `#download-btn`

ช่องกรอกพารามิเตอร์ถูกสร้างด้วย JS ตอน runtime และผูกชื่อผ่าน `input.dataset.param` (attribute `data-param`)
ไม่ได้ใช้ id — ดังนั้นเพิ่มพารามิเตอร์ใหม่ฝั่ง Python ได้เลยโดยไม่ต้องแตะ HTML

---

## 5. เช็คลิสต์ก่อนบอกว่า "ฟีเจอร์ของฉันเสร็จแล้ว"

- [ ] เรียกผ่านหน้าเว็บได้จริง ไม่ใช่แค่รันฟังก์ชันใน Python ตรงๆ
- [ ] เปิด F12 → Console ไม่มี error สีแดง (ยกเว้นตอนตั้งใจทดสอบ error)
- [ ] ทดสอบกับภาพจริงอย่างน้อย 3 ภาพที่ต่างกัน (ภาพถ่าย / ภาพวาดเส้น / ภาพมี noise)
- [ ] ลองปรับพารามิเตอร์จนสุดทั้งสองด้าน (min และ max) แล้ว server ไม่ crash
- [ ] อัปเดตเอกสารนี้ถ้า contract เปลี่ยน (เพิ่ม param / เปลี่ยนชื่อฟังก์ชัน / เปลี่ยน element id)
