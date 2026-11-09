/* CHILDNET SafeSignal portal: concept prototype, synthetic data only. */
/* CHILDNET 360 — LOCAL & CLOUD API CONFIGURATION */

const API_BASE =
  ["localhost", "127.0.0.1"].includes(window.location.hostname)
  && window.location.port !== "8001"
    ? "http://127.0.0.1:8001"
    : window.location.origin;

const CONFIG = {
  API_URL: `${API_BASE}/api/help`,
  TIMEOUT_MS: 8000,
  QUEUE_KEY: "childnet_queue_v1",
  EXIT_URL: "https://www.google.com",
  LANG: "AR",
};

const HELP_TYPES = {1:"تهديد أو ابتزاز", 2:"تواصل غير مرغوب", 3:"تنمّر", 4:"احتيال", 5:"طلب غير لائق", 6:"بدي أحكي مع حدا"};
const AGE_BANDS  = {0:"تخطّي", 1:"أقل من 10", 2:"10 - 12", 3:"13 - 15", 4:"16 - 17"};
const state = { helpType: 6, age: 0 };

/* ---------- SafeSignal code (نفس صيغة notebook 02) ---------- */
const CRC_TABLE = (() => { const t = []; for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; } return t; })();
function crc32(str) { let c = 0xFFFFFFFF; for (const b of new TextEncoder().encode(str)) c = CRC_TABLE[(c ^ b) & 255] ^ (c >>> 8); return (c ^ 0xFFFFFFFF) >>> 0; }
const crc4 = s => (crc32(s) & 0xFFFF).toString(16).toUpperCase().padStart(4, "0");
const token = () => Array.from(crypto.getRandomValues(new Uint8Array(3)), b => b.toString(16).padStart(2, "0")).join("").toUpperCase();
function buildCode(tok) {
  const urgency = $("#urgent").checked ? 4 : 2;
  const core = `SS1|${state.helpType}|${urgency}|${CONFIG.LANG}|${state.age}|${tok}`;
  return { code: `${core}|${crc4(core)}`, urgency };
}

/* ---------- helpers ---------- */
const $ = s => document.querySelector(s);
const load = () => { try { return JSON.parse(localStorage.getItem(CONFIG.QUEUE_KEY)) || []; } catch { return []; } };
const save = q => { try { localStorage.setItem(CONFIG.QUEUE_KEY, JSON.stringify(q)); } catch {} };
let currentToken = token();

function toast(msg) {
  const t = $("#toast"); t.textContent = msg; t.hidden = false;
  clearTimeout(toast.id); toast.id = setTimeout(() => (t.hidden = true), 3500);
}

function chips(el, map, key, onPick) {
  el.replaceChildren();
  for (const [v, label] of Object.entries(map)) {
    const b = document.createElement("button");
    b.type = "button"; b.className = "chip"; b.textContent = label; b.setAttribute("role", "radio");
    b.setAttribute("aria-checked", String(Number(v) === state[key]));
    b.onclick = () => { state[key] = Number(v); chips(el, map, key, onPick); onPick(); };
    el.appendChild(b);
  }
}

function refreshCode() { $("#code").textContent = buildCode(currentToken).code; }

/* ---------- connection badge ---------- */
function updateNet() {
  const b = $("#net-badge"), slow = ["slow-2g", "2g"].includes(navigator.connection?.effectiveType);
  if (!navigator.onLine) { b.textContent = "● بدون إنترنت"; b.className = "badge off"; }
  else if (slow)        { b.textContent = "● اتصال ضعيف"; b.className = "badge slow"; }
  else                  { b.textContent = "● متصل";        b.className = "badge on"; }
}

/* ---------- queue ---------- */
function renderQueue() {
  const q = load(), pending = q.filter(x => x.status === "pending");
  $("#count").textContent = pending.length;
  $("#empty").hidden = q.length > 0;
  const ul = $("#queue"); ul.replaceChildren();
  for (const item of q.slice(-5).reverse()) {
    const li = document.createElement("li");
    const code = document.createElement("code"); code.textContent = item.code;
    const tag = document.createElement("span");
    tag.className = "tag " + item.status; tag.textContent = item.status === "sent" ? "تم الاستلام" : "بانتظار الإرسال";
    li.append(code, tag); ul.appendChild(li);
  }
}


async function post(item) {
  const ctl = new AbortController();
  const t = setTimeout(() => ctl.abort(), CONFIG.TIMEOUT_MS);

  try {
    const res = await fetch(CONFIG.API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      signal: ctl.signal,
      body: JSON.stringify({
        request_id: item.id,
        event_type: "help_request"
      })
    });

    if (!res.ok) {
      throw new Error("HTTP " + res.status);
    }

    const data = await res.json();

    if (!data.case_id) {
      throw new Error("Missing case_id");
    }

    return data;

  } finally {
    clearTimeout(t);
  }
}


function showReceipt(data, urgent) {

  $("#receipt-title").textContent =
    "تمت معالجة الإشارة التجريبية";

  $("#receipt-msg").textContent =
    `استجاب الخادم التجريبي للطلب.
    رقم الحالة: ${data.case_id}.
    لم يتم إرسال بلاغ حقيقي أو التواصل مع جهة حماية.`;

  $("#receipt").hidden = false;

  $("#receipt").scrollIntoView({
    behavior: "smooth",
    block: "center"
  });

}

async function sendItem(item) {
  try {
    const data = await post(item);
    const q = load(); const i = q.findIndex(x => x.id === item.id);
    if (i >= 0) { q[i].status = "sent"; save(q); }
    renderQueue(); return data;                      // التأكيد بعد رد الخادم فقط
  } catch { return null; }
}

async function onSOS() {
  const btn = $("#sos"); btn.disabled = true;
  const { code, urgency } = buildCode(currentToken);
  const item = { id: crypto.randomUUID?.() || String(Date.now()), code, urgency, createdAt: Date.now(), status: "pending" };
  const q = load(); q.push(item); save(q); renderQueue();    // احفظ محليًا أولًا
  const data = await sendItem(item);
  if (data) { showReceipt(data, urgency === 4); currentToken = token(); refreshCode(); }
  else toast("تعذّر الاتصال. حُفظ الطلب على هذا الجهاز، وتقدر تنسخ الرمز وترسله برسالة SMS.");
  btn.disabled = false;
}

async function retryAll() {
  const btn = $("#retry"), pending = load().filter(x => x.status === "pending");
  if (!pending.length) return toast("لا توجد طلبات معلّقة.");
  btn.disabled = true; let ok = 0;
  for (const it of pending) if (await sendItem(it)) ok++;
  btn.disabled = false;
  toast(ok ? `تم إرسال ${ok} من ${pending.length}` : "ما زال الاتصال متعذّرًا. جرّب لاحقًا.");
}

/* ---------- quick exit ---------- */
let lastEsc = 0;
const quickExit = () => location.replace(CONFIG.EXIT_URL);
document.addEventListener("keydown", e => {
  if (e.key !== "Escape") return;
  if (Date.now() - lastEsc < 600) quickExit();
  lastEsc = Date.now();
});

/* ---------- init ---------- */
chips($("#help-types"), HELP_TYPES, "helpType", refreshCode);
chips($("#age-bands"), AGE_BANDS, "age", refreshCode);
$("#urgent").addEventListener("change", refreshCode);
$("#sos").addEventListener("click", onSOS);
$("#retry").addEventListener("click", retryAll);
$("#quick-exit").addEventListener("click", quickExit);
$("#copy").addEventListener("click", async () => {
  try { await navigator.clipboard.writeText($("#code").textContent); toast("تم نسخ الرمز"); } catch { toast("تعذّر النسخ، حدّد الرمز يدويًا."); }
});
window.addEventListener("online", () => { updateNet(); retryAll(); });
window.addEventListener("offline", updateNet);
updateNet(); refreshCode(); renderQueue();

// ==================================
// CHILDNET 360 - AI AGENT CHAT
// ==================================

const agentForm = document.getElementById("agent-chat-form");
const agentQuestion = document.getElementById("agent-chat-question");
const agentStatus = document.getElementById("agent-chat-status");
const agentAnswer = document.getElementById("agent-chat-answer");
const agentSources = document.getElementById("agent-chat-sources");

if (agentForm) {
  agentForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const question = agentQuestion.value.trim();

    if (!question) return;

    agentStatus.textContent = "⏳ جاري تحليل السؤال...";
    agentAnswer.textContent = "";
    agentSources.replaceChildren();

    try {
      const response = await fetch(
        `${API_BASE}/agent-chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            message: question,
            top_k: 3
          })
        }
      );

      if (!response.ok) {
        throw new Error("HTTP " + response.status);
      }

      const result = await response.json();

      agentAnswer.textContent =
        result.answer || "لم تتوفر إجابة.";

      agentStatus.textContent =
        result.mode === "EVIDENCE_ONLY"
          ? "📚 تم استرجاع الأدلة من قاعدة المعرفة."
          : "✅ اكتمل تحليل السؤال.";

      const sources = Array.isArray(result.sources)
        ? result.sources
        : [];

      sources.forEach(function (source, index) {

        const card = document.createElement("div");
        card.className = "policy-source";

        const title = document.createElement("strong");
        title.textContent =
          `${index + 1}. ${source.document || "مصدر قانوني"}`;

        const excerpt = document.createElement("p");
        excerpt.textContent = source.text || "";

        card.append(title, excerpt);
        agentSources.appendChild(card);

      });

    } catch (error) {

  console.error("CHILDNET AI CHAT ERROR:", error);

  agentStatus.textContent =
    "❌ تعذّر الاتصال بالمساعد: " + error.message;

}

  });
}

/* ==========================================
   CHILDNET 360 — PLATFORM INTEGRATION
   Policy Intelligence + Progressive Scenario
========================================== */

const PLATFORM_API = API_BASE;


/* ---------- SAFE RESULT RENDERER ---------- */

/* ==========================================
   CHILDNET 360 — INTELLIGENCE DASHBOARD
========================================== */

function showPlatformResult(elementId, data) {

  const container = document.getElementById(elementId);

  if (!container) return;

  container.replaceChildren();

  const dashboard = document.createElement("div");

  dashboard.className = "intelligence-dashboard";

  function createField(label, value) {

    const field = document.createElement("div");

    field.className = "intelligence-field";

    const title = document.createElement("strong");

    title.textContent = label
      .replaceAll("_", " ")
      .replace(/([a-z])([A-Z])/g, "$1 $2");

    const content = document.createElement("div");

    content.className = "intelligence-value";

    if (value === null || value === undefined) {

      content.textContent = "Not available";

    } else if (Array.isArray(value)) {

      if (value.length === 0) {

        content.textContent = "No records available";

      } else {

        value.forEach((item, index) => {

          const subCard = document.createElement("div");

          subCard.className = "intelligence-subcard";

          if (typeof item === "object" && item !== null) {

            subCard.appendChild(
              createObject(item, `Record ${index + 1}`)
            );

          } else {

            subCard.textContent = String(item);

          }

          content.appendChild(subCard);

        });

      }

    } else if (typeof value === "object") {

      content.appendChild(
        createObject(value)
      );

    } else {

      content.textContent = String(value);

    }

    field.append(title, content);

    return field;
  }

  function createObject(obj, heading = "") {

    const card = document.createElement("div");

    card.className = "intelligence-card";

    if (heading) {

      const h = document.createElement("h3");

      h.textContent = heading;

      card.appendChild(h);

    }

    for (const [key, value] of Object.entries(obj)) {

      card.appendChild(
        createField(key, value)
      );

    }

    return card;
  }

  if (Array.isArray(data)) {

    data.forEach((item, index) => {

      if (typeof item === "object" && item !== null) {

        dashboard.appendChild(
          createObject(item, `Result ${index + 1}`)
        );

      } else {

        dashboard.appendChild(
          createField(`Result ${index + 1}`, item)
        );

      }

    });

  } else if (typeof data === "object" && data !== null) {

    dashboard.appendChild(
      createObject(data)
    );

  } else {

    dashboard.appendChild(
      createField("Result", data)
    );

  }

  container.appendChild(dashboard);

}


/* ---------- API REQUEST ---------- */

async function platformGet(endpoint) {

  const response = await fetch(
    PLATFORM_API + endpoint,
    {
      method: "GET",
      headers: {
        "Accept": "application/json"
      }
    }
  );

  if (!response.ok) {
    throw new Error("HTTP " + response.status);
  }

  return await response.json();
}


/* ---------- POLICY INTELLIGENCE ---------- */

const policyButton =
  document.getElementById("run-policy-analysis");

if (policyButton) {

  policyButton.addEventListener("click", async () => {

    policyButton.disabled = true;

    const resultBox =
      document.getElementById("policy-results");

    resultBox.textContent =
      "⏳ جاري استرجاع تحليل السياسات...";

    try {

      const data = await platformGet(
        "/policy-intelligence"
      );

      showPlatformResult("policy-results", data);

    } catch (error) {

      resultBox.textContent =
        "تعذر تحميل تحليل السياسات: " +
        error.message;

    } finally {

      policyButton.disabled = false;

    }

  });

}


/* ---------- PROGRESSIVE SCENARIO ---------- */

const scenarioButton =
  document.getElementById("run-progressive-scenario");

if (scenarioButton) {

  scenarioButton.addEventListener("click", async () => {

    scenarioButton.disabled = true;

    const resultBox =
      document.getElementById("scenario-results");

    resultBox.textContent =
      "⏳ جاري تحميل السيناريو...";

    try {

      const data = await platformGet(
        "/progressive-scenario"
      );

      showPlatformResult("scenario-results", data);

    } catch (error) {

      resultBox.textContent =
        "تعذر تشغيل السيناريو: " +
        error.message;

    } finally {

      scenarioButton.disabled = false;

    }

  });

}

