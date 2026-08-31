"""
Image Processing Backend — เครื่องเซิร์ฟเวอร์
วิชา 310-3311 Image Processing / Workshop ท้าย Lecture 9

โจทย์ที่ไฟล์นี้ตอบ
    ข้อ 1  เป็น Backend 1 เครื่อง
    ข้อ 2  รับไฟล์ภาพจาก Client แล้วประมวลผลที่ฝั่ง Server
    ข้อ 3  ส่งภาพผลลัพธ์กลับไปให้ Client
    ข้อ 4  ทำงานด้วย REST API (Flask)

รัน:  python app.py     (ผูกกับ 0.0.0.0:5000 เพื่อให้เครื่องอื่นในวง LAN เรียกได้)
"""

import base64

import cv2
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

# frontend อยู่คนละพอร์ตและคนละเครื่อง เบราว์เซอร์จะบล็อกถ้า server ไม่ส่ง header อนุญาตกลับไป
CORS(app)


@app.route("/api/process", methods=["POST"])
def process():
    """รับภาพ -> ประมวลผล -> ส่งภาพผลลัพธ์กลับ"""

    # 1. เอาไฟล์ออกจาก request (ชื่อ "image" ต้องตรงกับที่ frontend ส่งมา)
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image uploaded"}), 400

    raw = request.files["image"].read()

    # 2. แปลงไบต์ของไฟล์ JPEG/PNG ให้เป็นตารางพิกเซล BGR
    #    imdecode ดูลายเซ็นที่ต้นไฟล์เอง ไม่ได้ดูนามสกุล ถ้าไม่ใช่รูปจะคืน None (ไม่ใช่ error)
    img_bgr = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    if img_bgr is None:
        return jsonify({"success": False, "error": "ไฟล์ที่ส่งมาไม่ใช่รูปภาพ"}), 400

    # 3. ประมวลผลที่ฝั่ง server — Canny Edge Detection (สไลด์หน้า 9)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    result = cv2.Canny(blurred, 50, 150)

    # 4. บีบกลับเป็นไฟล์ PNG แล้วแปลงเป็นข้อความ base64 เพื่อใส่ใน JSON
    ok, buffer = cv2.imencode(".png", result)
    if not ok:
        return jsonify({"success": False, "error": "เข้ารหัสภาพผลลัพธ์ไม่สำเร็จ"}), 500

    return jsonify({
        "success": True,
        "image": "data:image/png;base64," + base64.b64encode(buffer).decode("ascii"),
    })


if __name__ == "__main__":
    # 0.0.0.0 = รับจากทุกเครื่องในวง LAN ถ้าใช้ 127.0.0.1 เครื่องอื่นจะต่อไม่ได้
    app.run(host="0.0.0.0", port=5000)
