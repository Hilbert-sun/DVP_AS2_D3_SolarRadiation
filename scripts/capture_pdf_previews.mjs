import fs from "node:fs/promises";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const outputDir = path.join(root, "report_preview_pages");
const pdfUrl = "http://localhost:8000/SUNZHEN_36446874_Report.pdf";
const debugBase = `http://127.0.0.1:${process.env.CDP_PORT || "9222"}`;
const pages = [2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15];

await fs.mkdir(outputDir, { recursive: true });

async function createPage(url) {
  const response = await fetch(`${debugBase}/json/new?${encodeURIComponent(url)}`, {
    method: "PUT",
  });
  if (!response.ok) {
    throw new Error(`Unable to create Chrome page: ${response.status}`);
  }
  return response.json();
}

function connect(wsUrl) {
  const socket = new WebSocket(wsUrl);
  let nextId = 1;
  const pending = new Map();
  const ready = new Promise((resolve, reject) => {
    socket.addEventListener("open", resolve, { once: true });
    socket.addEventListener("error", reject, { once: true });
  });
  socket.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    if (!message.id || !pending.has(message.id)) {
      return;
    }
    const { resolve, reject } = pending.get(message.id);
    pending.delete(message.id);
    if (message.error) {
      reject(new Error(message.error.message));
    } else {
      resolve(message.result);
    }
  });
  async function send(method, params = {}) {
    await ready;
    const id = nextId++;
    const result = new Promise((resolve, reject) => pending.set(id, { resolve, reject }));
    socket.send(JSON.stringify({ id, method, params }));
    return result;
  }
  return { socket, send };
}

async function wait(ms) {
  await new Promise((resolve) => setTimeout(resolve, ms));
}

for (const pageNumber of pages) {
  const page = await createPage(`${pdfUrl}#page=${pageNumber}&zoom=page-width`);
  const { socket, send } = connect(page.webSocketDebuggerUrl);
  await send("Page.enable");
  await send("Emulation.setDeviceMetricsOverride", {
    width: 1250,
    height: 1050,
    deviceScaleFactor: 1,
    mobile: false,
  });
  await wait(1400);
  const screenshot = await send("Page.captureScreenshot", {
    format: "png",
    fromSurface: true,
    captureBeyondViewport: false,
  });
  await fs.writeFile(
    path.join(outputDir, `page_${String(pageNumber).padStart(2, "0")}.png`),
    Buffer.from(screenshot.data, "base64"),
  );
  socket.close();
}

console.log(`Captured ${pages.length} report preview pages.`);
