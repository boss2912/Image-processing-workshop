"""
Edge Detection — เจ้าของไฟล์: Tshering Dorji
อ้างอิง: Lecture 9 - Edge and Corner Detection หน้า 6-22

กติกาของไฟล์นี้ (ตกลงกันไว้ใน docs/API_CONTRACT.md):
    ทุกฟังก์ชันต้องมีหน้าตา  def ชื่อ(img_bgr, **params) -> numpy.ndarray
    - img_bgr : ภาพต้นฉบับ 3 channel เรียงแบบ BGR (แบบที่ OpenCV อ่านมาให้)
    - คืนค่า  : numpy array จะเป็น grayscale (2 มิติ) หรือ BGR (3 มิติ) ก็ได้
                app.py เข้ารหัสเป็น PNG ได้ทั้งสองแบบ
    - ห้าม import อะไรจาก app.py (จะกลายเป็น circular import)
    - ห้ามแก้ corner.py (ของ Pongsapak) ถ้าต้องการอะไรจากไฟล์นั้นให้บอกเจ้าของ
"""

import cv2
import numpy as np


def _to_odd(n):
    """ทำให้เป็นเลขคี่เสมอ เพราะ GaussianBlur / Sobel บังคับ ksize เป็นเลขคี่"""
    n = int(n)
    return n if n % 2 == 1 else n + 1


def canny(img_bgr, blur_ksize=5, low=50, high=150):
    """
    Canny Edge Detector — 5 ขั้นตอนตามสไลด์หน้า 9

    1. Noise removal      : เบลอด้วย Gaussian filter ก่อน ไม่งั้น noise จะกลายเป็นขอบปลอม
    2. Find gradient      : หา gradient ด้วย Sobel
    3. Non-max suppression: เก็บเฉพาะจุดที่ gradient แรงสุดในทิศของ gradient (ทำให้เส้นบาง)
    4. Double threshold   : แบ่งเป็นขอบชัด / ขอบอ่อน / ไม่ใช่ขอบ
    5. Hysteresis         : ขอบอ่อนที่ต่อกับขอบชัดถึงจะถูกเก็บไว้

    ข้อ 2-5 cv2.Canny() ทำให้ครบในคำสั่งเดียว เราทำเองแค่ข้อ 1

    พารามิเตอร์:
        blur_ksize : ขนาด kernel ของ Gaussian ยิ่งใหญ่ยิ่งเบลอ เส้นขอบยิ่งเหลือน้อย (สไลด์หน้า 18-19)
        low, high  : threshold คู่ของ hysteresis (สไลด์หน้า 20-21)
                     high สูง -> เหลือแต่ขอบที่มั่นใจจริงๆ / low ต่ำ -> ได้เส้นต่อเนื่องขึ้นแต่มี noise มากขึ้น

    คืนค่า: ภาพขาวดำ (uint8) ขอบเป็นสีขาว 255 พื้นหลังดำ 0
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (_to_odd(blur_ksize), _to_odd(blur_ksize)), 0)
    return cv2.Canny(blurred, int(low), int(high))


def sobel(img_bgr, blur_ksize=5, ksize=3):
    """
    Sobel Gradient Magnitude — ขั้นตอนที่ 2 ของ Canny ที่ดึงออกมาดูเดี่ยวๆ (สไลด์หน้า 11-12)

    >>> งานของ Tshering — ยังไม่ได้เขียน <<<

    สิ่งที่ต้องทำ (ทำตามลำดับนี้ได้เลย):
        1. แปลงเป็น grayscale ด้วย cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        2. เบลอด้วย cv2.GaussianBlur เหมือนใน canny() ข้างบน (ใช้ _to_odd(blur_ksize))
        3. หา gradient แกน x : cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=_to_odd(ksize))
           หา gradient แกน y : cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=_to_odd(ksize))
           *** ต้องใช้ CV_64F ไม่ใช่ uint8 เพราะ gradient ติดลบได้ ถ้าใช้ uint8 ค่าลบจะโดนตัดทิ้งหมด
        4. หา magnitude : np.sqrt(gx**2 + gy**2)   หรือ cv2.magnitude(gx, gy)
        5. ปรับสเกลกลับมา 0-255 แล้วแปลงเป็น uint8 :
           cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        6. return ผลลัพธ์ (แล้วลบ raise NotImplementedError ทิ้ง)

    ทดสอบ: รัน backend แล้วเลือก "Sobel Gradient Magnitude" ในหน้าเว็บ
           ผลที่ควรได้คือภาพเทาๆ ที่ขอบสว่าง ไม่ใช่ภาพขาวดำเส้นบางแบบ Canny
    """
    raise NotImplementedError(
        "sobel() ยังไม่ได้เขียน — งานของ Tshering (ดูขั้นตอนใน docstring ของฟังก์ชันนี้)"
    )
