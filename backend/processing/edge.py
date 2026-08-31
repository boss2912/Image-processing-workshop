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

    ขั้นตอน:
        1. แปลงภาพเป็น grayscale และลด noise ด้วย Gaussian blur
        2. คำนวณ gradient แกน x และ y ด้วย CV_64F เพื่อรักษาค่าติดลบ
        3. รวม gradient ทั้งสองแกนเป็น magnitude
        4. normalize เป็นช่วง 0-255 และคืนค่าเป็น uint8

    ทดสอบ: รัน backend แล้วเลือก "Sobel Gradient Magnitude" ในหน้าเว็บ
           ผลที่ควรได้คือภาพเทาๆ ที่ขอบสว่าง ไม่ใช่ภาพขาวดำเส้นบางแบบ Canny
    """
    # Sobel works on image intensity, so convert the BGR input to grayscale first.
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # Gaussian smoothing reduces noise that could otherwise appear as false edges.
    # OpenCV requires both Gaussian and Sobel kernel sizes to be odd numbers.
    blur_size = _to_odd(blur_ksize)
    sobel_size = _to_odd(ksize)
    blurred = cv2.GaussianBlur(gray, (blur_size, blur_size), 0)

    # Calculate horizontal and vertical intensity gradients separately
    # CV_64F preserves negative gradients instead of clipping them to zero.
    gradient_x = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=sobel_size)
    gradient_y = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=sobel_size)

    # Combine both directions to obtain the overall edge strength per pixel.
    magnitude = cv2.magnitude(gradient_x, gradient_y)

    # Scale the magnitude into a displayable 8-bit grayscale image (0-255).
    return cv2.normalize(
        magnitude, None, 0, 255, cv2.NORM_MINMAX
    ).astype(np.uint8)
