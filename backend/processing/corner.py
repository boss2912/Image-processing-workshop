"""
Corner Detection + Region Labeling — เจ้าของไฟล์: พงศภัค เทียบพิมพ์
อ้างอิง: Lecture 9 หน้า 24-31 (Harris) และหน้า 37-43 (Region labeling / Bounding box)

กติกาของไฟล์นี้ (ตกลงกันไว้ใน docs/API_CONTRACT.md):
    ทุกฟังก์ชันต้องมีหน้าตา  def ชื่อ(img_bgr, **params) -> numpy.ndarray
    - img_bgr : ภาพต้นฉบับ 3 channel เรียงแบบ BGR (แบบที่ OpenCV อ่านมาให้)
    - คืนค่า  : numpy array จะเป็น grayscale (2 มิติ) หรือ BGR (3 มิติ) ก็ได้
    - ห้าม import อะไรจาก app.py (จะเป็น circular import)
    - ห้ามแก้ edge.py (ของ Tshering) ถ้าต้องการอะไรจากไฟล์นั้นให้บอกเจ้าของ
"""

import cv2
import numpy as np


def _to_odd(n):
    """ทำให้เป็นเลขคี่เสมอ เพราะ Sobel ที่อยู่ข้างใน cornerHarris บังคับ ksize เป็นเลขคี่"""
    n = int(n)
    return n if n % 2 == 1 else n + 1


def _scale_for(img):
    """
    หาขนาดที่เหมาะกับภาพนี้ สำหรับวาดวงกลม/ตัวอักษร

    ทำไมต้องมี: ภาพจากมือถือกว้าง 4000-5000 พิกเซล ถ้าวาดวงกลมรัศมี 4 พิกเซลตายตัว
    พอย่อภาพลงมาดูในหน้าเว็บจะมองไม่เห็นอะไรเลย จึงต้องปรับขนาดตามความกว้างของภาพ
    """
    return max(1.0, img.shape[1] / 1200.0)


def _draw_count(img, text):
    """
    เขียนตัวเลขสรุปมุมซ้ายบนของภาพ

    วาด 2 รอบซ้อนกัน: รอบแรกสีดำหนากว่าเป็นขอบ รอบสองสีเหลืองบางกว่าทับข้างใน
    เพื่อให้อ่านออกไม่ว่าพื้นหลังตรงนั้นจะสว่างหรือมืด (ถ้าวาดสีเดียวบนพื้นสีใกล้กันจะกลืนหายไป)
    """
    scale = _scale_for(img)
    thickness = max(1, int(scale * 2))
    origin = (int(10 * scale), int(40 * scale))
    cv2.putText(img, text, origin, cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), thickness * 3)
    cv2.putText(img, text, origin, cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 255, 255), thickness)


def _corner_response(img_bgr, block_size, ksize, k):
    """
    หา Corner Response Function (CRF) ตามสไลด์หน้า 26-28

    [1] หา gradient ของภาพ (Sobel ขนาด ksize)
    [2] สร้าง covariance matrix จาก gradient กำลังสอง (Ix^2, Iy^2, Ix*Iy)
    [3] เกลี่ยด้วย low-pass filter ในหน้าต่างขนาด block_size
    [4] หา eigenvalue λ1, λ2 ของ matrix นั้น
    [5] CRF  R = λ1*λ2 - k*(λ1+λ2)^2 = det(M) - k*trace(M)^2

    ทั้ง 5 ขั้นตอน cv2.cornerHarris() ทำให้ครบในคำสั่งเดียว

    ความหมายของค่า R:
        R มาก      -> เป็นมุม  (gradient แรงทั้งสองทิศพร้อมกัน)
        R ติดลบมาก -> เป็นขอบ  (gradient แรงทิศเดียว)
        R ใกล้ 0   -> พื้นเรียบ
    """
    gray = np.float32(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY))
    return cv2.cornerHarris(gray, int(block_size), _to_odd(ksize), float(k))


def harris(img_bgr, block_size=2, ksize=3, k=0.04, threshold=0.01):
    """
    Harris Corner Detection แบบพื้นฐาน — ระบายสีแดงทับทุกพิกเซลที่ R สูงพอ

    พารามิเตอร์:
        threshold : สัดส่วนเทียบกับ R สูงสุดในภาพ เช่น 0.01 = เอาเฉพาะจุดที่ R > 1% ของ R สูงสุด
                    ลอง 0.001 กับ 0.1 เทียบกันดู จะเห็นจำนวนจุดต่างกันมาก

    ข้อสังเกตที่จะเจอ (และเป็นที่มาของ harris_nms ข้างล่าง):
        มุมหนึ่งมุมจะได้จุดแดงเป็นกระจุกหลายสิบพิกเซล ไม่ใช่จุดเดียว
        เพราะพิกเซลรอบๆ มุมก็มี R สูงตามไปด้วย
        ฟังก์ชันนี้จึงไม่เขียนจำนวน "มุม" ลงบนภาพ เพราะสิ่งที่นับได้คือจำนวน "พิกเซล" ไม่ใช่จำนวนมุม

    คืนค่า: ภาพ BGR (สำเนาของต้นฉบับ) ที่มีจุดมุมเป็นสีแดง
    """
    response = _corner_response(img_bgr, block_size, ksize, k)
    output = img_bgr.copy()
    # response > threshold * response.max() ได้ผลเป็น mask แบบ True/False ขนาดเท่าภาพ
    # เอา mask ไปใช้เป็น index ของ numpy เพื่อระบายสีแดง (BGR = 0,0,255) เฉพาะจุดที่ True
    output[response > float(threshold) * response.max()] = (0, 0, 255)
    return output


def harris_nms(img_bgr, block_size=2, ksize=3, k=0.04, threshold=0.01, radius=10):
    """
    Harris + Non-maximum Suppression — สไลด์หน้า 30
    "selecting the strongest corner points within a 10-pixel radius"

    ปัญหาที่แก้: harris() ข้างบนให้จุดแดงเป็นกระจุกต่อ 1 มุม
    ผลลัพธ์ที่ต้องการ: ในรัศมี radius พิกเซล เหลือจุดที่ R แรงที่สุดแค่จุดเดียว

    วิธีที่ใช้คือ dilate trick:
        cv2.dilate แทนค่าทุกพิกเซลด้วย "ค่าสูงสุดในละแวก" ที่ kernel ครอบถึง
        ดังนั้นพิกเซลไหนที่ response เท่ากับ local_max ก็แปลว่าพิกเซลนั้นเป็นตัวที่แรงที่สุด
        ในละแวกของตัวเองอยู่แล้ว ไม่ต้องวนลูปเทียบทีละคู่ให้ช้า

    พารามิเตอร์:
        radius : รัศมีเป็นพิกเซล ยิ่งใหญ่ยิ่งเหลือจุดน้อย (สไลด์ใช้ 10)

    คืนค่า: ภาพ BGR ที่มีวงกลมสีแดงรอบมุมที่ตรวจพบ + จำนวนมุมมุมซ้ายบน
    """
    response = _corner_response(img_bgr, block_size, ksize, k)

    # kernel วงกลมรัศมี radius -> ขนาดจริงคือเส้นผ่านศูนย์กลาง 2*radius+1 (ต้องเป็นเลขคี่เพื่อให้มีจุดกลาง)
    size = 2 * int(radius) + 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
    local_max = cv2.dilate(response, kernel)

    # เงื่อนไข 2 ข้อพร้อมกัน:
    #   response == local_max              -> เป็นตัวแรงที่สุดในละแวกของตัวเอง (non-maximum suppression)
    #   response > threshold * max         -> และแรงพอที่จะเรียกว่ามุมจริงๆ ไม่ใช่ noise
    # ใช้ & ไม่ใช่ and เพราะเป็นการเทียบทั้ง array ทีเดียว ไม่ใช่เทียบค่าเดียว
    mask = (response == local_max) & (response > float(threshold) * response.max())

    # np.nonzero คืนพิกัดของตำแหน่งที่เป็น True โดยเรียงเป็น (แถว, คอลัมน์) = (y, x)
    ys, xs = np.nonzero(mask)

    output = img_bgr.copy()
    scale = _scale_for(output)
    circle_radius = max(3, int(4 * scale))
    circle_thickness = max(1, int(2 * scale))
    for x, y in zip(xs, ys):
        # cv2.circle รับพิกัดเป็น (x, y) ซึ่งสลับกับที่ numpy คืนมา ถ้าใส่ผิดลำดับ
        # จุดจะไปโผล่ตำแหน่งที่พลิกตามแนวทแยงของภาพ
        cv2.circle(output, (int(x), int(y)), circle_radius, (0, 0, 255), circle_thickness)

    _draw_count(output, "corners: %d" % len(xs))
    return output


def contour_boxes(img_bgr, threshold=127, min_area=100, invert=0):
    """
    Region Labeling + Bounding Box — สไลด์หน้า 37-43
    ตอบคำถามในสไลด์ที่ว่า "How to tell a computer that this image have nine object?"

    สไลด์สอนวิธี flood fill + scanline ให้เห็นหลักการ (หน้า 40-42) แต่ OpenCV มี findContours
    ที่ทำงานเดียวกันให้แล้ว จึงใช้ตัวนั้นเพื่อให้ demo ทำงานได้จริงในเวลาที่มี

    ขั้นตอน:
        1. แปลงเป็น grayscale
        2. แปลงเป็นภาพ binary ตามนิยาม foreground/background ในสไลด์หน้า 38
           (0 = background, 255 = foreground)
        3. findContours หาเส้นขอบของแต่ละ region -> 1 contour = 1 วัตถุ
        4. กรอง contour ที่เล็กกว่า min_area ทิ้ง (พวก noise จุดเล็กๆ)
        5. ตีกรอบสี่เหลี่ยมด้วย boundingRect (สไลด์หน้า 43)
        6. เขียนจำนวนวัตถุที่นับได้ลงบนภาพ

    พารามิเตอร์:
        threshold : ค่าตัดระหว่าง background กับ foreground (0-255)
        min_area  : พื้นที่ต่ำสุดที่ยอมนับเป็นวัตถุ ใช้กรอง noise
        invert    : 0 = วัตถุสว่างกว่าพื้นหลัง (THRESH_BINARY)
                    1 = วัตถุเข้มกว่าพื้นหลัง  (THRESH_BINARY_INV)
                    ถ้าเลือกผิดด้าน โปรแกรมจะไปนับ "พื้นหลัง" เป็นวัตถุ 1 ชิ้นใหญ่แทน
                    ให้ลองทั้งสองค่าแล้วดูว่าอันไหนได้จำนวนตรงกับที่ตาเห็น

    คืนค่า: ภาพ BGR ที่มีกรอบสีเขียวรอบวัตถุ + จำนวนวัตถุมุมซ้ายบน
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    mode = cv2.THRESH_BINARY_INV if int(invert) else cv2.THRESH_BINARY
    _, binary = cv2.threshold(gray, int(threshold), 255, mode)

    # RETR_EXTERNAL = เอาเฉพาะ external contour ตามสไลด์หน้า 46 (ไม่เอารูที่อยู่ข้างในวัตถุ)
    # CHAIN_APPROX_SIMPLE = เก็บเฉพาะจุดหักมุมของเส้นขอบ ไม่เก็บทุกพิกเซล (ประหยัดหน่วยความจำ)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    output = img_bgr.copy()
    scale = _scale_for(output)
    box_thickness = max(1, int(2 * scale))

    count = 0
    for c in contours:
        if cv2.contourArea(c) < int(min_area):
            continue
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), box_thickness)
        count += 1

    _draw_count(output, "objects: %d" % count)
    return output
