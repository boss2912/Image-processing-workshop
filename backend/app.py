"""
Image Processing Backend — Flask REST API
วิชา 310-3311 Image Processing / Workshop ท้าย Lecture 9

เจ้าของไฟล์: เจตน์

ไฟล์นี้คือ "พนักงานรับของ" ของเครื่องเซิร์ฟเวอร์
มันไม่ได้ประมวลผลภาพเอง แต่เป็นคนรับภาพจากหน้าเว็บ ส่งต่อให้ฟังก์ชันใน processing/
แล้วเอาผลลัพธ์ส่งกลับไป

ไฟล์นี้มี 5 ฟังก์ชัน:
    parse_params()    แปลงค่าที่กรอกในหน้าเว็บ (เป็นข้อความ) ให้เป็นตัวเลข
    health_check()    ตอบว่า "ยังอยู่นะ"                     <- GET  /api/health
    list_operations() ส่งรายชื่อ operation ให้หน้าเว็บ        <- GET  /api/operations
    process()         รับภาพ -> ประมวลผล -> ส่งภาพกลับ      <- POST /api/process
    too_large()       ดักกรณีอัปโหลดไฟล์ใหญ่เกิน

รัน:
    python app.py
ค่าเริ่มต้นคือ 0.0.0.0:5000 — ผูกกับ 0.0.0.0 (ไม่ใช่ 127.0.0.1) เพราะตอนเดโมต้องให้
frontend ที่อยู่คนละเครื่องในวง LAN เรียกเข้ามาได้
"""

import base64
import os

import cv2
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS

from processing import OPERATIONS

app = Flask(__name__)

# CORS เปิดไว้เพราะ frontend รันคนละพอร์ต (8000) และตอนเดโมจริงรันคนละเครื่องด้วย
# เบราว์เซอร์จะบล็อก request ข้าม origin ถ้า server ไม่ส่ง header Access-Control-Allow-Origin กลับมา
# ถ้าเป็นงานจริงควรจำกัดเฉพาะ origin ที่เชื่อถือได้ ไม่ใช่เปิดหมดแบบนี้
CORS(app)

# กันไฟล์ใหญ่เกินจนกิน RAM ของ server (15 MB) — เกินกว่านี้ Flask จะโยน 413 ให้เอง
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024


# parse_params() : แปลงค่าที่กรอกในหน้าเว็บให้เป็นตัวเลขที่ฟังก์ชันประมวลผลใช้ได้
#   รับ  -> รายการพารามิเตอร์ที่ operation นั้นต้องการ + ค่าที่ส่งมาจากหน้าเว็บ
#   คืน  -> dict ของตัวเลขพร้อมใช้ เช่น {"low": 60, "high": 180}
#   ***  ถ้าค่าไม่ใช่ตัวเลข หรือเกินช่วง min/max จะโยน ValueError ออกมา  ***
def parse_params(spec, form):
    """
    แปลงค่าที่ส่งมาใน form (เป็น string เสมอ) ให้เป็น int/float ตามที่ operation ประกาศไว้

    spec คือ dict "params" ของ operation นั้นใน processing/__init__.py
    ตัวไหนที่ client ไม่ส่งมา ใช้ค่า default
    """
    params = {}
    for name, rule in spec.items():
        raw = form.get(name)
        if raw is None or raw == "":
            params[name] = rule["default"]
            continue
        try:
            value = int(raw) if rule["type"] == "int" else float(raw)
        except ValueError:
            raise ValueError(f"พารามิเตอร์ {name} ต้องเป็นตัวเลข (ได้มา: {raw!r})")
        if value < rule["min"] or value > rule["max"]:
            raise ValueError(
                f"พารามิเตอร์ {name} ต้องอยู่ระหว่าง {rule['min']} ถึง {rule['max']} (ได้มา: {value})"
            )
        params[name] = value
    return params


# health_check() : ตอบกลับว่า backend ยังทำงานอยู่
#   รับ  -> ไม่รับอะไร (แค่เปิด URL /api/health)
#   คืน  -> JSON {"status": "ok", "service": "Image Processing Backend"}
@app.route("/api/health", methods=["GET"])
def health_check():
    """ให้ frontend กดเช็คได้ว่ากรอก backend URL ถูกไหม ก่อนจะอัปโหลดภาพจริง"""
    return jsonify({
        "status": "ok",
        "service": "Image Processing Backend",
    })


# list_operations() : ส่งรายชื่อวิธีประมวลผลทั้งหมดให้หน้าเว็บ
#   รับ  -> ไม่รับอะไร
#   คืน  -> JSON รายชื่อ operation พร้อมพารามิเตอร์ของแต่ละตัว
@app.route("/api/operations", methods=["GET"])
def list_operations():
    """
    ส่งรายชื่อ operation ให้ frontend เอาไปสร้าง dropdown + ช่องกรอกพารามิเตอร์เอง

    ทำแบบนี้เพื่อไม่ให้ต้องเขียนรายชื่อ operation ซ้ำสองที่ (ทั้งใน Python และใน JS)
    เวลา Tshering หรือบอสเพิ่ม operation ใหม่ หน้าเว็บจะขึ้นให้เองโดยไม่ต้องแก้ JS
    """
    items = [
        {
            "key": key,
            "label": op["label"],
            "owner": op["owner"],
            "params": op["params"],
        }
        for key, op in OPERATIONS.items()
    ]
    return jsonify({"success": True, "operations": items})


# process() : ฟังก์ชันหลักของทั้งโปรเจกต์ — รับภาพจาก client แล้วส่งภาพที่ประมวลผลแล้วกลับไป
#   รับ  -> ไฟล์ภาพ + ชื่อ operation + ค่าพารามิเตอร์ (ส่งมาแบบ multipart/form-data)
#   คืน  -> JSON ที่มีภาพผลลัพธ์ฝังอยู่เป็นข้อความ base64 + ขนาดภาพ + ค่าที่ใช้จริง
#   ***  ถ้ามีอะไรผิด จะคืน JSON {"success": false, "error": "..."} พร้อมรหัส 400/413/501/500  ***
@app.route("/api/process", methods=["POST"])
def process():
    # ใช้ POST เพราะ client ส่งไฟล์ + พารามิเตอร์มาใน request body ซึ่งเป็นรูปแบบมาตรฐานของการอัปโหลด
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image uploaded"}), 400

    operation = request.form.get("operation", "")
    if operation not in OPERATIONS:
        return jsonify({
            "success": False,
            "error": f"Unknown operation: {operation!r} (ดูรายชื่อที่ใช้ได้จาก GET /api/operations)",
        }), 400
    op = OPERATIONS[operation]

    raw = request.files["image"].read()
    if not raw:
        return jsonify({"success": False, "error": "Empty image file"}), 400

    # แปลง bytes ที่อัปโหลดมาให้เป็น numpy array แบบ BGR
    # frombuffer = มอง bytes เป็น array ของ uint8 / imdecode = ถอดรหัส JPEG/PNG ให้เป็นภาพจริง
    img_bgr = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    if img_bgr is None:
        return jsonify({
            "success": False,
            "error": "Cannot decode image — ไฟล์ที่ส่งมาอาจไม่ใช่รูปภาพ หรือเป็นฟอร์แมตที่ OpenCV ไม่รองรับ",
        }), 400

    try:
        params = parse_params(op["params"], request.form)
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400

    try:
        result = op["func"](img_bgr, **params)
    except NotImplementedError as exc:
        # ฟังก์ชันที่ยังเป็น TODO รอเจ้าของเขียน — ตอบ 501 Not Implemented
        # เพื่อให้แยกออกจาก 500 ที่แปลว่า "โค้ดที่เขียนแล้วมีบั๊ก"
        return jsonify({"success": False, "error": str(exc)}), 501
    except cv2.error as exc:
        return jsonify({"success": False, "error": f"OpenCV error: {exc}"}), 400

    ok, buffer = cv2.imencode(".png", result)
    if not ok:
        return jsonify({"success": False, "error": "Cannot encode result image"}), 500

    # ส่งภาพกลับเป็น data URL ฝัง base64 เพื่อให้ frontend เอาไปใส่ <img src="..."> ได้ตรงๆ
    # และยังคงรูปแบบ response เป็น JSON เหมือนกันทั้งกรณีสำเร็จและกรณี error
    return jsonify({
        "success": True,
        "operation": operation,
        "params": params,
        "width": int(result.shape[1]),
        "height": int(result.shape[0]),
        "image": "data:image/png;base64," + base64.b64encode(buffer).decode("ascii"),
    })


# too_large() : ดักกรณีผู้ใช้อัปโหลดไฟล์ใหญ่เกิน 15 MB
#   รับ  -> Flask เรียกให้เองอัตโนมัติ ไม่ต้องเรียกเอง
#   คืน  -> JSON {"success": false, "error": "ไฟล์ใหญ่เกิน 15 MB"} พร้อมรหัส 413
@app.errorhandler(413)
def too_large(_error):
    """Flask โยน 413 เองเมื่อไฟล์เกิน MAX_CONTENT_LENGTH — ดักไว้เพื่อตอบเป็น JSON ให้เหมือน error อื่น"""
    return jsonify({"success": False, "error": "ไฟล์ใหญ่เกิน 15 MB"}), 413


if __name__ == "__main__":
    # อ่านจาก environment variable ไม่ hardcode
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host=host, port=port, debug=debug)
