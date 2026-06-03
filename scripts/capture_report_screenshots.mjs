import fs from "node:fs/promises";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const outputDir = path.join(root, "report_screenshots");
const baseUrl = "http://localhost:8000/?report-capture=20260603";
const debugBase = "http://127.0.0.1:9222";

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
    const result = new Promise((resolve, reject) => {
      pending.set(id, { resolve, reject });
    });
    socket.send(JSON.stringify({ id, method, params }));
    return result;
  }

  return { socket, send };
}

async function wait(ms) {
  await new Promise((resolve) => setTimeout(resolve, ms));
}

async function evaluate(send, expression) {
  const result = await send("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });
  return result.result?.value;
}

async function capture(send, filename) {
  const metrics = await send("Page.getLayoutMetrics");
  const size = metrics.cssContentSize || metrics.contentSize;
  const screenshot = await send("Page.captureScreenshot", {
    format: "png",
    fromSurface: true,
    captureBeyondViewport: true,
    clip: {
      x: 0,
      y: 0,
      width: Math.ceil(size.width),
      height: Math.ceil(size.height),
      scale: 1,
    },
  });
  await fs.writeFile(path.join(outputDir, filename), Buffer.from(screenshot.data, "base64"));
}

const page = await createPage(baseUrl);
const { socket, send } = connect(page.webSocketDebuggerUrl);

await send("Page.enable");
await send("Runtime.enable");
await send("Emulation.setDeviceMetricsOverride", {
  width: 1600,
  height: 1000,
  deviceScaleFactor: 1,
  mobile: false,
});
await wait(1200);

const captureStep = async (step, filename) => {
  await evaluate(
    send,
    `document.querySelector('button[data-step="${step}"]').click(); true;`,
  );
  await wait(700);
  await capture(send, filename);
};

await captureStep(1, "fig1_overall_interface.png");
await captureStep(1, "fig2_long_term_context.png");
await captureStep(2, "fig3_seasonal_rhythm.png");
await captureStep(3, "fig4_sunshine_driver.png");
await captureStep(4, "fig5_extreme_days.png");
await captureStep(5, "fig6_planning_takeaway.png");
const step5CardCount = await evaluate(
  send,
  `document.querySelectorAll('.takeaway-card').length`,
);

await evaluate(send, `document.querySelector('button[data-step="4"]').click(); true;`);
await wait(700);
await evaluate(send, `document.querySelector('.date-link').click(); true;`);
await wait(700);
await capture(send, "fig7_linked_extreme_day.png");

const summary = await evaluate(
  send,
  `({
    title: document.title,
    activeStep: document.querySelector('.story-steps button.is-active')?.textContent.trim(),
    insight: document.querySelector('#insight-panel p')?.textContent.trim(),
    chartOverflow: getComputedStyle(document.querySelector('.chart-area')).overflow,
    step5CardCount: ${step5CardCount}
  })`,
);
console.log(JSON.stringify(summary, null, 2));

socket.close();
