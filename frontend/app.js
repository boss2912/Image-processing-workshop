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

const backendUrlInput = document.getElementById("backend-url");
const connectBtn = document.getElementById("connect-btn");
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
const downloadBtn = document.getElementById("download-btn");

// เก็บ operation ที่ดึงมาจาก server ไว้ เพื่อไม่ต้องยิงซ้ำทุกครั้งที่เปลี่ยน dropdown
let operations = [];

function setStatus(message, kind = "") {
  statusEl.textContent = message;
  statusEl.className = "status" + (kind ? " " + kind : "");
}

/** ตัด / ท้าย URL ทิ้ง กัน http://x:5000/ + /api/health กลายเป็น // */
function backendUrl() {
  return backendUrlInput.value.trim().replace(/\/+$/, "");
}

/** ขั้นที่ 1 — เช็คว่า backend URL ที่กรอกใช้ได้จริง แล้วค่อยดึงรายชื่อ operation */
async function connect() {
  const base = backendUrl();
  if (!base) {
    setStatus("กรุณากรอก Backend URL ก่อน", "error");
    return;
  }

  setStatus("กำลังเชื่อมต่อ " + base + " ...");
  try {
    const health = await fetch(base + "/api/health").then((r) => r.json());
    if (health.status !== "ok") throw new Error("backend ตอบกลับผิดรูปแบบ");

    const data = await fetch(base + "/api/operations").then((r) => r.json());
    operations = data.operations || [];
    buildOperationSelect();

    operationCard.hidden = false;
    uploadCard.hidden = false;
    setStatus("เชื่อมต่อสำเร็จ: " + health.service + " (" + operations.length + " operations)", "ok");
  } catch (err) {
    // fetch จะ throw ตอนต่อไม่ติด / โดน CORS บล็อก / URL ผิด — แยกจากกันจากใน JS ไม่ได้
    setStatus(
      "เชื่อมต่อไม่ได้: " + err.message +
      " — เช็คว่า backend รันอยู่จริง, URL/พอร์ตถูก, และ CORS เปิดอยู่",
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
    downloadBtn.href = data.image;
    downloadBtn.download = data.operation + ".png";
    downloadBtn.hidden = false;

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

connectBtn.addEventListener("click", connect);
operationSelect.addEventListener("change", buildParamInputs);

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  processBtn.disabled = !file;
  if (!file) return;
  // แสดงภาพต้นฉบับจากไฟล์ในเครื่องเลย ไม่ต้องรอ server
  sourceImage.src = URL.createObjectURL(file);
  resultImage.removeAttribute("src");
  downloadBtn.hidden = true;
  setStatus("");
});

processBtn.addEventListener("click", process);

// ลองเชื่อมต่ออัตโนมัติตอนเปิดหน้าเว็บ ด้วยค่า default (127.0.0.1:5000)
// ถ้าไม่ติดก็แค่ขึ้น error ให้ผู้ใช้แก้ URL เอง
connect();
