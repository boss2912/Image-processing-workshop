"""
ทะเบียนรวม operation ทั้งหมดของ backend

ทำไมต้องมีไฟล์นี้:
    app.py จะ "ไม่" import edge.py / corner.py ตรงๆ แต่มาอ่านจาก OPERATIONS ในไฟล์นี้แทน
    แปลว่าเวลาใครเพิ่ม operation ใหม่ ไม่ต้องไปแก้ app.py เลย แก้แค่ไฟล์นี้ไฟล์เดียว
    (ลดโอกาส merge conflict ระหว่าง 3 คน — app.py เป็นของเจตน์คนเดียว)

โครงสร้างของแต่ละ operation:
    "ชื่อ_key": {
        "label":  ข้อความที่โชว์ใน dropdown ฝั่ง frontend
        "owner":  ชื่อคนที่รับผิดชอบ (ไว้ดูตอน debug ว่าต้องไปตามใคร)
        "func":   ฟังก์ชันจริง รับ (img_bgr, **params) คืน numpy array
        "params": พารามิเตอร์ที่ปรับได้ ฝั่ง frontend จะเอาไปสร้างช่องกรอกให้อัตโนมัติ
    }

รูปแบบของ params แต่ละตัว:
    {"type": "int" หรือ "float", "default": ค่าเริ่มต้น, "min": ต่ำสุด, "max": สูงสุด, "label": คำอธิบาย}
"""

from . import corner, edge

OPERATIONS = {
    # ---------- Edge : Tshering Dorji (edge.py) ----------
    "canny": {
        "label": "Canny Edge Detection",
        "owner": "Tshering",
        "func": edge.canny,
        "params": {
            "blur_ksize": {"type": "int", "default": 5, "min": 1, "max": 31,
                           "label": "ขนาด Gaussian kernel (เลขคี่)"},
            "low": {"type": "int", "default": 50, "min": 0, "max": 255,
                    "label": "Threshold ต่ำ (hysteresis)"},
            "high": {"type": "int", "default": 150, "min": 0, "max": 255,
                     "label": "Threshold สูง (hysteresis)"},
        },
    },
    "sobel": {
        "label": "Sobel Gradient Magnitude",
        "owner": "Tshering",
        "func": edge.sobel,
        "params": {
            "blur_ksize": {"type": "int", "default": 5, "min": 1, "max": 31,
                           "label": "ขนาด Gaussian kernel (เลขคี่)"},
            "ksize": {"type": "int", "default": 3, "min": 1, "max": 7,
                      "label": "ขนาด Sobel kernel (1,3,5,7)"},
        },
    },

    # ---------- Corner & Region : พงศภัค เทียบพิมพ์ (corner.py) ----------
    "harris": {
        "label": "Harris Corner Detection",
        "owner": "Pongsapak",
        "func": corner.harris,
        "params": {
            "block_size": {"type": "int", "default": 2, "min": 1, "max": 10,
                           "label": "ขนาดหน้าต่างหา covariance matrix"},
            "ksize": {"type": "int", "default": 3, "min": 1, "max": 7,
                      "label": "ขนาด Sobel kernel (1,3,5,7)"},
            "k": {"type": "float", "default": 0.04, "min": 0.01, "max": 0.20,
                  "label": "ค่าคงที่ k ในสูตร CRF"},
            "threshold": {"type": "float", "default": 0.01, "min": 0.0001, "max": 1.0,
                          "label": "สัดส่วนของ R สูงสุดที่ถือว่าเป็นมุม"},
        },
    },
    "harris_nms": {
        "label": "Harris + Non-maximum Suppression",
        "owner": "Pongsapak",
        "func": corner.harris_nms,
        "params": {
            "block_size": {"type": "int", "default": 2, "min": 1, "max": 10,
                           "label": "ขนาดหน้าต่างหา covariance matrix"},
            "ksize": {"type": "int", "default": 3, "min": 1, "max": 7,
                      "label": "ขนาด Sobel kernel (1,3,5,7)"},
            "k": {"type": "float", "default": 0.04, "min": 0.01, "max": 0.20,
                  "label": "ค่าคงที่ k ในสูตร CRF"},
            "threshold": {"type": "float", "default": 0.01, "min": 0.0001, "max": 1.0,
                          "label": "สัดส่วนของ R สูงสุดที่ถือว่าเป็นมุม"},
            "radius": {"type": "int", "default": 10, "min": 1, "max": 50,
                       "label": "รัศมี (พิกเซล) ที่เลือกมุมแรงสุดแค่จุดเดียว"},
        },
    },
    "contour_boxes": {
        "label": "Region Labeling + Bounding Box",
        "owner": "Pongsapak",
        "func": corner.contour_boxes,
        "params": {
            "threshold": {"type": "int", "default": 127, "min": 0, "max": 255,
                          "label": "ค่า threshold แปลงเป็นภาพขาวดำ"},
            "min_area": {"type": "int", "default": 100, "min": 0, "max": 100000,
                         "label": "พื้นที่ต่ำสุดที่ยอมนับเป็นวัตถุ (พิกเซล)"},
        },
    },
}
