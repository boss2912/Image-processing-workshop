/*
 * Image Processing Client — frontend
 * เจ้าของไฟล์: เจตน์
 *
 * หน้าที่ของไฟล์นี้: คุยกับ backend ผ่าน REST API 3 เส้น
 *   GET  /api/health      กดปุ่ม "เชื่อมต่อ" เพื่อเช็คว่า URL ถูกไหม
 *   GET  /api/operations  ดึงรายชื่อ operation มาสร้าง dropdown + ช่องกรอกพารามิเตอร์
 *   POST /api/process     ส่งไฟล์ภาพ + operation + พารามิเตอร์ ไปประมวลผลที่ server
 *
 * ไฟล์นี้ไม่ประมวลผลภาพเองเลยแม้แต่บรรทัดเดียว — การประมวลผลทั้งหมดอยู่ที่ฝั่ง server
 * ตามโจทย์ workshop ข้อ 2
 */

const operationCard = document.getElementById("operation-card");
const operationSelect = document.getElementById("operation");
const operationOwner = document.getElementById("operation-owner");
const paramsBox = document.getElementById("params");
const uploadCard = document.getElementById("upload-card");
const fileInput = document.getElementById("file-input");
const processBtn = document.getElementById("process-btn");
const statusEl = document.getElementById("status");
const sourceImage = document.getElementById("source-image");
const resultImage = document.getElementById("result-image");
const sourcePlaceholder = document.getElementById("source-placeholder");
const resultPlaceholder = document.getElementById("result-placeholder");
const downloadBtn = document.getElementById("download-btn");

// เก็บ operation ที่ดึงมาจาก server ไว้ เพื่อไม่ต้องยิงซ้ำทุกครั้งที่เปลี่ยน dropdown
let operations = [];

function setStatus(message, kind = "") {
  statusEl.textContent = message;
  statusEl.className = "status" + (kind ? " " + kind : "");
}

/** ดึง Backend URL อัตโนมัติ */
function backendUrl() {
  const host = window.location.hostname;
  if (!host || host === "localhost") {
    return "http://127.0.0.1:5000";
  }
  return `http://${host}:5000`;
}

/** ขั้นที่ 1 — เชื่อมต่อ Backend อัตโนมัติในเบื้องหลัง แล้วดึงรายชื่อ operation */
async function connect() {
  const base = backendUrl();
  setStatus("กำลังเชื่อมต่อ Backend (" + base + ") ...");
  try {
    let res = null;
    try {
      res = await fetch(base + "/api/health");
    } catch (e) {
      // Fallback ลอง 127.0.0.1 ถ้าต่อ localhost ไม่ติด
      if (base !== "http://127.0.0.1:5000") {
        res = await fetch("http://127.0.0.1:5000/api/health");
      } else {
        throw e;
      }
    }
    const health = await res.json();
    if (health.status !== "ok") throw new Error("Backend ตอบกลับผิดรูปแบบ");

    const data = await fetch(base + "/api/operations").then((r) => r.json());
    operations = data.operations || [];
    buildOperationSelect();

    setStatus("เชื่อมต่อ Backend สำเร็จ: " + health.service + " (" + operations.length + " operations)", "ok");
  } catch (err) {
    setStatus(
      "เชื่อมต่อ Backend ไม่สำเร็จ: " + err.message +
      " — กรุณาตรวจสอบว่า Terminal รัน 'python app.py' อยู่",
      "error"
    );
  }
}

/** สร้าง dropdown จากรายชื่อที่ server ส่งมา (ไม่ hardcode ไว้ใน JS) */
function buildOperationSelect() {
  operationSelect.innerHTML = "";
  operations.forEach((op) => {
    const option = document.createElement("option");
    option.value = op.key;
    option.textContent = op.label;
    operationSelect.appendChild(option);
  });
  buildParamInputs();
}

/** สร้างช่องกรอกพารามิเตอร์ตาม operation ที่เลือกอยู่ */
function buildParamInputs() {
  const op = operations.find((o) => o.key === operationSelect.value);
  paramsBox.innerHTML = "";
  if (!op) return;

  operationOwner.textContent = "รับผิดชอบโดย: " + op.owner;

  Object.entries(op.params).forEach(([name, rule]) => {
    const row = document.createElement("div");
    row.className = "row";

    const label = document.createElement("label");
    label.textContent = name;
    label.setAttribute("for", "param-" + name);

    const input = document.createElement("input");
    input.type = "number";
    input.id = "param-" + name;
    input.dataset.param = name;
    input.value = rule.default;
    input.min = rule.min;
    input.max = rule.max;
    // ค่าแบบ float ต้องให้กรอกทศนิยมได้ ไม่งั้น browser จะไม่ยอมรับ 0.04
    input.step = rule.type === "float" ? "0.001" : "1";

    const hint = document.createElement("span");
    hint.className = "param-hint";
    hint.textContent = rule.label + " (ช่วง " + rule.min + " ถึง " + rule.max + ")";

    row.appendChild(label);
    row.appendChild(input);
    row.appendChild(hint);
    paramsBox.appendChild(row);
  });
}

/** ขั้นที่ 3 — ส่งภาพไปประมวลผลที่ server */
async function process() {
  const file = fileInput.files[0];
  if (!file) {
    setStatus("ยังไม่ได้เลือกไฟล์ภาพ", "error");
    return;
  }

  // FormData = รูปแบบ multipart/form-data ซึ่งเป็นวิธีมาตรฐานของการอัปโหลดไฟล์ผ่าน HTTP
  // ชื่อ field "image" ต้องตรงกับที่ backend อ่าน (request.files["image"])
  const form = new FormData();
  form.append("image", file);
  form.append("operation", operationSelect.value);
  paramsBox.querySelectorAll("input[data-param]").forEach((input) => {
    form.append(input.dataset.param, input.value);
  });

  processBtn.disabled = true;
  setStatus("กำลังส่งไปประมวลผลที่ server ...");
  const startedAt = performance.now();

  try {
    const response = await fetch(backendUrl() + "/api/process", { method: "POST", body: form });
    const data = await response.json();

    if (!data.success) {
      // backend ตอบ JSON รูปแบบเดียวกันทุก error อยู่แล้ว เอา error มาโชว์ตรงๆ ได้เลย
      setStatus("Server ตอบกลับว่า: " + data.error, "error");
      return;
    }

    resultImage.src = data.image;
    resultImage.style.display = "block";
    resultPlaceholder.style.display = "none";
    downloadBtn.href = data.image;
    downloadBtn.download = data.operation + ".png";
    downloadBtn.style.display = "inline-block";

    const elapsed = Math.round(performance.now() - startedAt);
    setStatus(
      "สำเร็จ: " + data.operation + " " + data.width + "x" + data.height +
      " px (ไป-กลับ " + elapsed + " ms)",
      "ok"
    );
  } catch (err) {
    setStatus("ส่งไม่สำเร็จ: " + err.message, "error");
  } finally {
    processBtn.disabled = false;
  }
}

operationSelect.addEventListener("change", buildParamInputs);

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  processBtn.disabled = !file;
  if (!file) {
    sourceImage.style.display = "none";
    sourcePlaceholder.style.display = "block";
    return;
  }
  // แสดงภาพต้นฉบับจากไฟล์ในเครื่องเลย ไม่ต้องรอ server
  sourceImage.src = URL.createObjectURL(file);
  sourceImage.style.display = "block";
  sourcePlaceholder.style.display = "none";
  resultImage.removeAttribute("src");
  resultImage.style.display = "none";
  resultPlaceholder.style.display = "block";
  downloadBtn.style.display = "none";
  setStatus("");
});

processBtn.addEventListener("click", process);

// ลองเชื่อมต่ออัตโนมัติตอนเปิดหน้าเว็บ ด้วยค่า default (127.0.0.1:5000)
// ถ้าไม่ติดก็แค่ขึ้น error ให้ผู้ใช้แก้ URL เอง
connect();
