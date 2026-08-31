"""
Corner Detection + Region Labeling — เจ้าของไฟล์: พงศภัค เทียบพิมพ์
อ้างอิง: Lecture 9 หน้า 24-31 (Harris) และหน้า 37-43 (Region labeling / Bounding box)

กติกาของไฟล์นี้ (ตกลงกันไว้ใน docs/API_CONTRACT.md):
    ทุกฟังก์ชันต้องมีหน้าตา  def ชื่อ(img_bgr, **params) -> numpy.ndarray
    - img_bgr : ภาพต้นฉบับ 3 channel เรียงแบบ BGR (แบบที่ OpenCV อ่านมาให้)
    - คืนค่า  : numpy array จะเป็น grayscale (2 มิติ) หรือ BGR (3 มิติ) ก็ได้
    - ห้าม import อะไรจาก app.py (จะกลายเป็น circular import)
    - ห้ามแก้ edge.py (ของ Tshering) ถ้าต้องการอะไรจากไฟล์นั้นให้บอกเจ้าของ
"""

import cv2
import numpy as np


def _to_odd(n):
    """ทำให้เป็นเลขคี่เสมอ เพราะ Sobel ที่อยู่ข้างใน cornerHarris บังคับ ksize เป็นเลขคี่"""
    n = int(n)
    return n if n % 2 == 1 else n + 1


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
    Harris Corner Detection แบบพื้นฐาน — วาดจุดสีแดงทับทุกพิกเซลที่ R สูงพอ

    พารามิเตอร์:
        threshold : สัดส่วนเทียบกับ R สูงสุดในภาพ เช่น 0.01 = เอาเฉพาะจุดที่ R > 1% ของ R สูงสุด
                    ลอง 0.001 กับ 0.1 เทียบกันดู จะเห็นจำนวนจุดต่างกันมาก

    ข้อสังเกตที่จะเจอ (และเป็นที่มาของ harris_nms ข้างล่าง):
        มุมหนึ่งมุมจะได้จุดแดงเป็นกระจุกหลายสิบพิกเซล ไม่ใช่จุดเดียว
        เพราะพิกเซลรอบๆ มุมก็มี R สูงตามไปด้วย

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

    >>> งานของบอส — ยังไม่ได้เขียน <<<

    ปัญหาที่ต้องแก้: harris() ข้างบนให้จุดแดงเป็นกระจุกต่อ 1 มุม
    เป้าหมาย: ในรัศมี radius พิกเซล ให้เหลือจุดที่ R แรงที่สุดแค่จุดเดียว

    วิธีที่ง่ายที่สุด (dilate trick) — ทำตามนี้ได้เลย:
        1. response = _corner_response(img_bgr, block_size, ksize, k)
        2. สร้าง kernel วงกลมรัศมี radius:
           size = 2 * int(radius) + 1
           kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
        3. local_max = cv2.dilate(response, kernel)
           *** dilate = แทนค่าทุกพิกเซลด้วย "ค่าสูงสุดในละแวก" ดังนั้นพิกเซลไหนที่
               response == local_max ก็แปลว่าพิกเซลนั้นคือตัวที่แรงที่สุดในละแวกของมันเอง
        4. mask = (response == local_max) & (response > threshold * response.max())
        5. หาพิกัดของจุดที่เหลือ: ys, xs = np.nonzero(mask)
        6. วาดวงกลมทีละจุดบนสำเนาภาพ:
           output = img_bgr.copy()
           for x, y in zip(xs, ys):
               cv2.circle(output, (int(x), int(y)), 4, (0, 0, 255), 2)
           *** ระวังลำดับ: numpy เป็น (แถว, คอลัมน์) = (y, x) แต่ cv2.circle รับ (x, y) สลับกัน
        7. return output (แล้วลบ raise NotImplementedError ทิ้ง)

    ทดสอบ: ใช้ภาพเดิมเทียบกับ harris() ธรรมดา จำนวนจุดต้องลดลงชัดเจน
           แล้วลองปรับ radius 3 -> 10 -> 30 ดูว่าจุดหายไปเรื่อยๆ ตามที่คาดไหม
    """
    raise NotImplementedError(
        "harris_nms() ยังไม่ได้เขียน — งานของบอส (ดูขั้นตอนใน docstring ของฟังก์ชันนี้)"
    )


def contour_boxes(img_bgr, threshold=127, min_area=100):
    """
    Region Labeling + Bounding Box — สไลด์หน้า 37-43
    "How to tell a computer that this image have nine object?"

    >>> งานของบอส — ยังไม่ได้เขียน <<<

    สไลด์สอน flood fill + scanline เอง แต่ OpenCV มี findContours ให้ใช้แล้ว
    ให้ใช้ findContours ก่อนเพื่อให้ demo ทำงานได้ (ถ้ามีเวลาค่อยเขียน flood fill เองเพิ่ม)

    ขั้นตอน:
        1. gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        2. แปลงเป็นภาพ binary (0 กับ 255) ตามนิยาม foreground/background ในสไลด์หน้า 38:
           _, binary = cv2.threshold(gray, int(threshold), 255, cv2.THRESH_BINARY)
           *** ถ้าวัตถุในภาพเป็นสีเข้มบนพื้นสว่าง ให้ใช้ cv2.THRESH_BINARY_INV แทน
               ไม่งั้นมันจะไปนับพื้นหลังเป็นวัตถุ — ลองทั้งสองแบบแล้วดูผล
        3. contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
           RETR_EXTERNAL = เอาเฉพาะ external contour ตามสไลด์หน้า 46 (ไม่เอารูข้างใน)
        4. output = img_bgr.copy()  แล้ววนทีละ contour:
           for c in contours:
               if cv2.contourArea(c) < min_area:   # กรองจุด noise เล็กๆ ทิ้ง
                   continue
               x, y, w, h = cv2.boundingRect(c)
               cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
        5. นับจำนวนวัตถุที่ผ่านเกณฑ์ แล้วเขียนลงบนภาพด้วย cv2.putText
           (จะได้ตอบคำถามในสไลด์ได้ว่า "ภาพนี้มีกี่วัตถุ")
        6. return output (แล้วลบ raise NotImplementedError ทิ้ง)

    ทดสอบ: หาภาพที่มีวัตถุแยกกันชัดๆ หลายชิ้น นับจำนวนกล่องที่ได้เทียบกับที่ตาเห็น
           ถ้าไม่ตรง ให้ไปปรับ threshold ก่อน แล้วค่อยปรับ min_area
    """
    raise NotImplementedError(
        "contour_boxes() ยังไม่ได้เขียน — งานของบอส (ดูขั้นตอนใน docstring ของฟังก์ชันนี้)"
    )
