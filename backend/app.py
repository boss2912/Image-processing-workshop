"""
Image Processing Backend — เครื่องเซิร์ฟเวอร์
วิชา 310-3311 Image Processing / Workshop ท้าย Lecture 9

โจทย์ (สไลด์หน้า 90)
    1. Backend 1 เครื่อง Frontend 1 เครื่อง
    2. รับไฟล์ภาพจาก Client มาประมวลผลที่ Server
    3. ส่งภาพผลลัพธ์กลับไปให้ Client
    4. ใช้ REST API

ไฟล์นี้มี 3 def เรียงตามลำดับที่ใช้งานจริง
    1. health_check()            ปุ่ม "เช็คการเชื่อมต่อ" เรียก   GET  /api/health
    2. process()                 ปุ่ม "ประมวลผล" เรียก           POST /api/process
    3. find_edges_with_canny()   process() เรียกต่ออีกที          ไม่ใช่ endpoint

รัน:  python app.py
"""

import base64

import cv2
from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)

# หน้าเว็บเปิดจาก localhost:8000 แต่ยิง request มาที่ port 5000 เบราว์เซอร์ถือว่าคนละที่
# ปกติจะบล็อกทิ้ง CORS(app) สั่งให้ server ใส่ header อนุญาตกลับไปด้วย (สไลด์หน้า 86)
# ถ้าลบบรรทัดนี้ หน้าเว็บจะ error ทั้งที่ server ทำงานปกติ
CORS(app)


# ====================================================================
#  1. GET /api/health — ปุ่ม "เช็คการเชื่อมต่อ" (สไลด์หน้า 87)
# ====================================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    """
    บอก client ว่าเครื่องนี้เปิดอยู่และพร้อมทำงาน

    ไม่รับอะไรเข้ามา ส่งกลับเป็น JSON สั้นๆ
    มีไว้ให้กดเช็คก่อนได้ว่าต่อถึงกันไหม จะได้ไม่ต้องส่งรูปก้อนใหญ่ไปแล้วค่อยรู้ว่าต่อไม่ติด
    """
    return jsonify({
        "status": "ok",
        "service": "Image Processing Backend",
    })


# ====================================================================
#  2. POST /api/process — ปุ่ม "ประมวลผล" (สไลด์หน้า 88)
# ====================================================================

@app.route("/api/process", methods=["POST"])
def process():
    """
    รับภาพจาก client -> ประมวลผลที่เครื่องนี้ -> ส่งภาพผลลัพธ์กลับไป
    ตรงกับโจทย์ข้อ 2 และข้อ 3

    ใช้ POST เพราะต้องแนบไฟล์มาใน body ของ request ซึ่ง GET ทำไม่ได้
    """

    # ขั้นที่ 1 — เช็คว่า client แนบไฟล์มาจริงไหม
    # คำว่า "image" คือชื่อช่องที่ตกลงกับ frontend ไว้ ถ้าตั้งชื่อไม่ตรงกันจะหาไม่เจอ
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image uploaded"}), 400

    # ขั้นที่ 2 — เซฟไฟล์ที่ client ส่งมา แล้วอ่านกลับด้วย cv2.imread
    uploaded_file = request.files["image"]
    uploaded_file.save("uploaded.png")
    original_image = cv2.imread("uploaded.png")

    # ถ้าส่งไฟล์ที่ไม่ใช่รูปมา เช่นไฟล์ .txt  imread จะไม่ error แต่คืน None ออกมา
    if original_image is None:
        return jsonify({"success": False, "error": "ไฟล์ที่ส่งมาไม่ใช่รูปภาพ"}), 400

    # ขั้นที่ 3 — ประมวลผลที่ฝั่ง server (โจทย์ข้อ 2)
    edge_image = find_edges_with_canny(original_image)

    # ขั้นที่ 4 — เซฟภาพผลลัพธ์เป็นไฟล์ แล้วอ่านกลับมาเป็นข้อมูลดิบ
    cv2.imwrite("result.png", edge_image)
    result_file = open("result.png", "rb")
    result_bytes = result_file.read()
    result_file.close()

    # ขั้นที่ 5 — JSON ส่งได้แต่ตัวหนังสือ ส่งข้อมูลดิบของรูปไปตรงๆ ไม่ได้
    # base64 คือวิธีเขียนข้อมูลดิบให้กลายเป็นตัวหนังสือ
    image_as_text = base64.b64encode(result_bytes).decode()

    # ขั้นที่ 6 — ส่งกลับไปให้ client (โจทย์ข้อ 3)
    # ส่วนหน้า "data:image/png;base64," บอกเบราว์เซอร์ว่าข้อความข้างหลังคือไฟล์ PNG
    # ใส่ไว้แบบนี้ frontend เอาไปแปะใส่ <img src="..."> ได้เลย
    return jsonify({
        "success": True,
        "image": "data:image/png;base64," + image_as_text,
    })


# ====================================================================
#  3. find_edges_with_canny() — ตัวประมวลผลภาพ ที่ process() เรียกใช้
# ====================================================================

def find_edges_with_canny(original_image):
    """
    หาเส้นขอบของวัตถุในภาพ ด้วยวิธี Canny Edge Detection (สไลด์หน้า 9)

    รับ     : ภาพสีที่อ่านมาจาก cv2.imread
    ส่งกลับ : ภาพขาวดำ เส้นขอบเป็นสีขาว พื้นหลังเป็นสีดำ
    """

    # หาเส้นขอบดูแค่ความสว่างที่เปลี่ยนไป ไม่ต้องใช้สี จึงแปลงเป็นขาวดำก่อน
    gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

    # ถ้าไม่เบลอก่อน noise เม็ดเล็กๆ จะถูกนับเป็นเส้นขอบไปด้วย ผลลัพธ์จะรก
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # 50 กับ 150 คือ threshold ค่าต่ำกับค่าสูง
    # จุดที่แรงกว่า 150 นับเป็นขอบแน่นอน
    # จุดที่อยู่ระหว่าง 50 ถึง 150 นับเป็นขอบก็ต่อเมื่อต่อกับขอบที่แน่นอนอยู่แล้ว
    edge_image = cv2.Canny(blurred_image, 50, 150)

    return edge_image


if __name__ == "__main__":
    # 0.0.0.0 = รับ request จากทุกเครื่องในวง LAN
    # ถ้าใส่ 127.0.0.1 จะรับเฉพาะในเครื่องตัวเอง เครื่องอื่นต่อไม่ได้
    app.run(host="0.0.0.0", port=5000)
