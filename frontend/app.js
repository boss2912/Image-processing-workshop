/*
 * Image Processing Client — เครื่องผู้ใช้
 * วิชา 310-3311 Image Processing / Workshop ท้าย Lecture 9
 *
 * ไฟล์นี้ไม่ประมวลผลภาพเองแม้แต่บรรทัดเดียว การประมวลผลเกิดที่เครื่องเซิร์ฟเวอร์ทั้งหมด
 *
 * เรียงตามลำดับที่ใช้งานจริง
 *   1. ดึงของในหน้าเว็บมาเก็บไว้ในตัวแปร
 *   2. ปุ่ม "เช็คการเชื่อมต่อ"  ยิง GET  /api/health
 *   3. เลือกไฟล์             แสดงภาพต้นฉบับ ยังไม่ส่งไปไหน
 *   4. ปุ่ม "ประมวลผล"       ยิง POST /api/process
 */


// ====================================================================
//  1. ดึงของในหน้าเว็บมาเก็บไว้ในตัวแปร
// ====================================================================
// ชื่อ id ในวงเล็บ ต้องตรงกับที่เขียนไว้ใน index.html เป๊ะๆ ถ้าพิมพ์ผิดจะได้ค่า null

const backendUrlInput = document.getElementById("backend-url-input");
const checkConnectionButton = document.getElementById("check-connection-button");
const imageFileInput = document.getElementById("image-file-input");
const processButton = document.getElementById("process-button");
const originalImage = document.getElementById("original-image");
const resultImage = document.getElementById("result-image");
const statusText = document.getElementById("status-text");


// ====================================================================
//  2. ปุ่ม "เช็คการเชื่อมต่อ"  ->  GET /api/health
// ====================================================================
// คำว่า async หน้า function แปลว่าข้างในมีการรอ (await) ตรงนี้คือรอ server ตอบกลับ
// ระหว่างที่รอ หน้าเว็บจะไม่ค้าง

checkConnectionButton.addEventListener("click", async function () {
  const serverUrl = backendUrlInput.value;

  statusText.textContent = "กำลังเช็ค " + serverUrl + " ...";

  // try / catch ดักกรณีต่อไม่ติดเลย เช่นพิมพ์ IP ผิด หรือยังไม่ได้เปิด app.py
  // ถ้าไม่ดักไว้ หน้าเว็บจะเงียบไปเฉยๆ ผู้ใช้ไม่รู้ว่าเกิดอะไรขึ้น
  try {
    // fetch ถ้าไม่บอกว่าใช้วิธีไหน มันจะใช้ GET ให้เอง
    const response = await fetch(serverUrl + "/api/health");
    const responseData = await response.json();

    // status กับ service คือ 2 ค่าที่ health_check() ใน app.py ส่งมา
    statusText.textContent = "ต่อได้: " + responseData.service + " — status " + responseData.status;
  } catch (error) {
    statusText.textContent =
      "ต่อไม่ได้: " + error.message + " — เช็คว่า Backend URL ถูกและเครื่องเซิร์ฟเวอร์รัน app.py อยู่";
  }
});


// ====================================================================
//  3. เลือกไฟล์  ->  แสดงภาพต้นฉบับทันที (ยังไม่ยุ่งกับ server)
// ====================================================================

imageFileInput.addEventListener("change", function () {
  // .files คือรายการไฟล์ที่เลือก เอาตัวแรกคือ [0] เพราะให้เลือกได้ทีละไฟล์
  const selectedFile = imageFileInput.files[0];

  // เปิดหน้าต่างเลือกไฟล์แล้วกดยกเลิก จะไม่มีไฟล์ ให้จบตรงนี้
  if (!selectedFile) {
    return;
  }

  // createObjectURL สร้างที่อยู่ชั่วคราวของไฟล์ในเครื่อง ให้ <img> เอาไปแสดงได้
  originalImage.src = URL.createObjectURL(selectedFile);

  // ล้างผลลัพธ์เก่าทิ้ง จะได้ไม่สับสนว่าเป็นผลของรูปเก่าหรือรูปใหม่
  resultImage.removeAttribute("src");
  statusText.textContent = "";
});


// ====================================================================
//  4. ปุ่ม "ประมวลผล"  ->  POST /api/process พร้อมไฟล์ภาพ
// ====================================================================

processButton.addEventListener("click", async function () {
  const selectedFile = imageFileInput.files[0];

  if (!selectedFile) {
    statusText.textContent = "ยังไม่ได้เลือกรูป";
    return;
  }

  // FormData คือรูปแบบมาตรฐานของการแนบไฟล์ไปกับ request
  // ชื่อ "image" ต้องตรงกับฝั่ง server ที่เขียนว่า request.files["image"]
  // ถ้าตั้งชื่อไม่ตรงกัน server จะตอบว่า No image uploaded
  const formData = new FormData();
  formData.append("image", selectedFile);

  const serverUrl = backendUrlInput.value;

  statusText.textContent = "กำลังส่งไปประมวลผลที่ server ...";

  try {
    // รอบนี้ต้องบอกว่าใช้ POST เพราะค่าเริ่มต้นของ fetch คือ GET
    // body คือของที่แนบไปด้วย ในที่นี้คือไฟล์ภาพที่อยู่ใน formData
    const response = await fetch(serverUrl + "/api/process", {
      method: "POST",
      body: formData,
    });

    const responseData = await response.json();

    // server ตอบ success เป็น false แปลว่ามีอะไรผิด เช่นส่งไฟล์ที่ไม่ใช่รูปไป
    if (responseData.success === false) {
      statusText.textContent = "Server ตอบกลับว่า: " + responseData.error;
      return;
    }

    // responseData.image คือข้อความ base64 ที่ app.py ส่งมา
    // เอาไปใส่ src ของ <img> ได้ตรงๆ เบราว์เซอร์แปลงกลับเป็นรูปให้เอง
    resultImage.src = responseData.image;
    statusText.textContent = "สำเร็จ";
  } catch (error) {
    statusText.textContent =
      "ส่งไม่สำเร็จ: " + error.message + " — เช็คว่า Backend URL ถูกและเครื่องเซิร์ฟเวอร์รัน app.py อยู่";
  }
});
