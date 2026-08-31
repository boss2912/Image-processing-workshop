/*
 * Image Processing Client — เครื่องผู้ใช้
 *
 * ไฟล์นี้ไม่ประมวลผลภาพเองเลย มีหน้าที่แค่
 *   1. ให้ผู้ใช้เลือกรูป
 *   2. ส่งรูปไปที่เครื่องเซิร์ฟเวอร์
 *   3. เอาภาพผลลัพธ์ที่ส่งกลับมาแสดง
 */

// ===================================================================
//  แก้บรรทัดนี้บรรทัดเดียว ให้เป็น IP ของเครื่องเซิร์ฟเวอร์
//  หา IP ด้วยการรัน  ipconfig  บนเครื่องเซิร์ฟเวอร์ แล้วดูบรรทัด IPv4 Address
//  ถ้ารันเครื่องเดียวกับ backend ใช้ http://127.0.0.1:5000 ได้เลย
// ===================================================================
const BACKEND_URL = "http://172.20.56.133:5000";

const fileInput = document.getElementById("file-input");
const processBtn = document.getElementById("process-btn");
const sourceImage = document.getElementById("source-image");
const resultImage = document.getElementById("result-image");
const statusEl = document.getElementById("status");

// เลือกไฟล์แล้วแสดงภาพต้นฉบับทันที (ยังไม่ส่งไปไหน)
fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (!file) return;
  sourceImage.src = URL.createObjectURL(file);
  resultImage.removeAttribute("src");
  statusEl.textContent = "";
});

// กดประมวลผล = ส่งไฟล์ไปที่เครื่องเซิร์ฟเวอร์
processBtn.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) {
    statusEl.textContent = "ยังไม่ได้เลือกรูป";
    return;
  }

  // FormData = รูปแบบ multipart/form-data ซึ่งเป็นวิธีมาตรฐานของการอัปโหลดไฟล์
  // ชื่อ "image" ต้องตรงกับที่ backend อ่าน (request.files["image"])
  const form = new FormData();
  form.append("image", file);

  statusEl.textContent = "กำลังส่งไปประมวลผลที่ server ...";
  try {
    const response = await fetch(BACKEND_URL + "/api/process", {
      method: "POST",
      body: form,
    });
    const data = await response.json();

    if (!data.success) {
      statusEl.textContent = "Server ตอบกลับว่า: " + data.error;
      return;
    }

    resultImage.src = data.image;
    statusEl.textContent = "สำเร็จ";
  } catch (err) {
    statusEl.textContent =
      "ส่งไม่สำเร็จ: " + err.message + " — เช็คว่า BACKEND_URL ถูกต้องและเครื่องเซิร์ฟเวอร์รัน app.py อยู่";
  }
});
