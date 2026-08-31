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
const sourcePlaceholder = document.getElementById("source-placeholder");
const resultPlaceholder = document.getElementById("result-placeholder");
const downloadBtn = document.getElementById("download-btn");

// เก็บ operation ที่ดึงมาจาก server ไว้ เพื่อไม่ต้องยิงซ้ำทุกครั้งที่เปลี่ยน dropdown
let operations = [];

function setStatus(message, kind = "") {
  statusEl.textContent = message;
  statusEl.className = "status" + (kind ? " " + kind : "");
}

/**
 * เดา Backend URL จากที่อยู่ของหน้าเว็บเอง — ใช้เป็น "ค่าตั้งต้น" ที่เติมให้ในช่องกรอก
 *
 * เปิดหน้าเว็บด้วย localhost      -> เดาว่า backend อยู่เครื่องเดียวกัน (127.0.0.1)
 * เปิดหน้าเว็บด้วย 172.20.56.133 -> เดาว่า backend อยู่เครื่องเดียวกับที่เสิร์ฟหน้าเว็บ
 *
 * การเดาแบบนี้ใช้ไม่ได้ตอนเดโม 2 เครื่องแบบที่โจทย์ต้องการ
 * เพราะเครื่องผู้ใช้เสิร์ฟหน้าเว็บเอง (localhost:8000) แต่ backend อยู่อีกเครื่อง
 * จึงต้องมีช่องให้กรอกเองทับค่าที่เดาได้เสมอ (สไลด์หน้า 89)
 */
function detectBackendUrl() {
  const host = window.location.hostname;
  if (!host || host === "localhost") {
    return "http://127.0.0.1:5000";
  }
  return `http://${host}:5000`;
}

/** Backend URL ที่จะใช้จริง — เอาจากช่องกรอกก่อน ถ้าว่างค่อยใช้ค่าที่เดาได้ */
function backendUrl() {
  const typed = backendUrlInput.value.trim().replace(/\/+$/, "");
  return typed || detectBackendUrl();
}

/** ขั้นที่ 1 — เชื่อมต่อ Backend อัตโนมัติในเบื้องหลัง แล้วดึงรายชื่อ operation */
async function connect() {
  const base = backendUrl();
  setStatus("กำลังเชื่อมต่อ Backend (" + base + ") ...");
  try {
    // ยิงไปที่ URL ที่ผู้ใช้ระบุเท่านั้น ไม่มี fallback เงียบๆ ไปที่ 127.0.0.1
    // เพราะตอนเดโม 2 เครื่อง ถ้าแอบ fallback จะขึ้นว่าสำเร็จทั้งที่ต่อผิดเครื่อง หาสาเหตุไม่เจอ
    //
    // ตัดรอที่ 5 วินาที: ถ้าพิมพ์ IP ผิด Windows จะรอ TCP timeout เป็นนาที
    // ผู้ใช้จะนึกว่าเว็บค้าง แทนที่จะรู้ว่ากรอก IP ผิด
    const res = await fetch(base + "/api/health", { signal: AbortSignal.timeout(5000) });
    const health = await res.json();
    if (health.status !== "ok") throw new Error("Backend ตอบกลับผิดรูปแบบ");

    const data = await fetch(base + "/api/operations").then((r) => r.json());
    operations = data.operations || [];
    buildOperationSelect();

    setStatus("เชื่อมต่อ Backend สำเร็จ: " + health.service + " (" + operations.length + " operations)", "ok");
  } catch (err) {
    // TimeoutError = ยิงไปแล้วเงียบจนครบ 5 วินาที มักแปลว่า IP ผิด หรือ firewall บล็อก
    const reason = err.name === "TimeoutError"
      ? "ไม่มีการตอบกลับภายใน 5 วินาที (IP อาจผิด หรือ firewall บล็อกพอร์ต 5000)"
      : err.message;
    setStatus(
      "เชื่อมต่อ Backend ไม่สำเร็จ: " + reason +
      " — เช็คว่าเครื่องเซิร์ฟเวอร์รัน app.py อยู่จริง, Backend URL ในช่องด้านบนถูกต้อง, และ firewall เปิดพอร์ต 5000 แล้ว",
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

// กดปุ่ม "เชื่อมต่อ" หรือกด Enter ในช่อง URL แล้วลองต่อใหม่ได้ทันที
// (จำเป็นตอนเดโม 2 เครื่อง เพราะต้องแก้ IP แล้วต่อใหม่โดยไม่ต้อง refresh หน้า)
connectBtn.addEventListener("click", connect);
backendUrlInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") connect();
});

// เติมค่าที่เดาได้ให้ในช่องกรอกก่อน แล้วลองเชื่อมต่ออัตโนมัติตอนเปิดหน้าเว็บ
// ถ้าไม่ติดก็แค่ขึ้น error สีแดง ผู้ใช้แก้ URL ในช่องแล้วกดเชื่อมต่อใหม่ได้เลย
backendUrlInput.value = detectBackendUrl();
connect();
