const $ = (id) => document.getElementById(id);

const els = {
  dot: $("dot"),
  statusText: $("statusText"),
  apiBase: $("apiBase"),

  file: $("file"),
  uploadBtn: $("uploadBtn"),
  clearBtn: $("clearBtn"),

  uploadErr: $("uploadErr"),
  docIdView: $("docIdView"),
  fileView: $("fileView"),
  chunksView: $("chunksView"),

  // tabs
  tabs: [...document.querySelectorAll(".tab")],
  panels: {
    t1: $("panel-t1"),
    t2: $("panel-t2"),
    t3: $("panel-t3"),
    t4: $("panel-t4"),
  },

  // outputs
  summaryBtn: $("summaryBtn"),
  summaryErr: $("summaryErr"),
  summaryOut: $("summaryOut"),
  summaryCits: $("summaryCits"),

  planBtn: $("planBtn"),
  planErr: $("planErr"),
  planOut: $("planOut"),
  planCits: $("planCits"),

  genPracticeBtn: $("genPracticeBtn"),
  nQ: $("nQ"),
  pracErr: $("pracErr"),
  practiceList: $("practiceList"),

  // chat
  msgs: $("msgs"),
  question: $("question"),
  askBtn: $("askBtn"),
  resetChatBtn: $("resetChatBtn"),
  chatErr: $("chatErr"),
};

let state = {
  doc_id: localStorage.getItem("doc_id") || "",
  filename: localStorage.getItem("filename") || "",
  chunks: localStorage.getItem("chunks") || "",
};

function api() {
  return (els.apiBase.value || "http://127.0.0.1:8000").trim().replace(/\/+$/, "");
}

function setStatus(ok, text) {
  els.dot.className = "dot " + (ok ? "ok" : "bad");
  els.statusText.textContent = text;
}

function showErr(el, msg) {
  el.style.display = msg ? "block" : "none";
  el.textContent = msg || "";
}

function setDocInfo({ doc_id, filename, chunks }) {
  state.doc_id = doc_id || "";
  state.filename = filename || "";
  state.chunks = (chunks ?? "").toString();

  localStorage.setItem("doc_id", state.doc_id);
  localStorage.setItem("filename", state.filename);
  localStorage.setItem("chunks", state.chunks);

  els.docIdView.textContent = state.doc_id || "—";
  els.fileView.textContent = state.filename || "—";
  els.chunksView.textContent = state.chunks || "—";
}

function escapeHtml(s) {
  return (s || "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  }[c]));
}

function citationsHtml(citations) {
  if (!Array.isArray(citations) || citations.length === 0) return "";
  const items = citations.map((c, i) => {
    const src = escapeHtml(c.source || `Fuente ${i + 1}`);
    const chunk = escapeHtml(c.chunk_id || "");
    const snip = escapeHtml(c.snippet || "");
    return `
      <div>
        <div class="pill">${src} · ${chunk}</div>
        <div style="margin-top:6px;font-size:12px;color:rgba(255,255,255,.65);white-space:pre-wrap">${snip}</div>
      </div>
    `;
  }).join("");
  return `
    <details>
      <summary>Ver fuentes usadas</summary>
      <div class="cit">${items}</div>
    </details>
  `;
}

function appendMsg(who, text, extraHtml = "") {
  const wrap = document.createElement("div");
  wrap.className = "msg " + (who === "me" ? "me" : "bot");

  const meta = document.createElement("div");
  meta.className = "meta";
  meta.textContent = who === "me" ? "Tú" : "Asistente";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text || "";

  wrap.appendChild(meta);
  wrap.appendChild(bubble);

  if (extraHtml) {
    const extra = document.createElement("div");
    extra.innerHTML = extraHtml;
    wrap.appendChild(extra);
  }

  els.msgs.appendChild(wrap);
  els.msgs.scrollTop = els.msgs.scrollHeight;
}

async function safeJson(res) {
  const text = await res.text();
  try { return { json: JSON.parse(text), text }; }
  catch { return { json: null, text }; }
}

async function healthCheck() {
  try {
    const res = await fetch(`${api()}/health`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    setStatus(data?.status === "ok", data?.status === "ok" ? "Backend conectado" : "Backend respondió raro");
  } catch (e) {
    setStatus(false, `Backend no disponible (${e.message})`);
  }
}

async function uploadFile(file) {
  showErr(els.uploadErr, "");
  if (!file) return showErr(els.uploadErr, "Selecciona un archivo.");

  els.uploadBtn.disabled = true;
  els.uploadBtn.textContent = "Subiendo...";

  try {
    const fd = new FormData();
    fd.append("file", file);

    const res = await fetch(`${api()}/documents/upload`, { method: "POST", body: fd });
    const { json, text } = await safeJson(res);

    if (!res.ok) throw new Error(json?.detail || text || `HTTP ${res.status}`);

    setDocInfo({ doc_id: json.doc_id, filename: json.filename, chunks: json.chunks });
    appendMsg("bot", `Documento indexado.\ndoc_id: ${json.doc_id}\nchunks: ${json.chunks}`);
  } catch (e) {
    showErr(els.uploadErr, `Error en upload:\n${e.message}`);
  } finally {
    els.uploadBtn.disabled = false;
    els.uploadBtn.textContent = "Subir";
  }
}

async function doSummary() {
  showErr(els.summaryErr, "");
  els.summaryOut.textContent = "";
  els.summaryCits.innerHTML = "";
  if (!state.doc_id) return showErr(els.summaryErr, "Primero sube un documento.");

  els.summaryBtn.disabled = true;
  els.summaryBtn.textContent = "Generando...";

  try {
    const res = await fetch(`${api()}/documents/${state.doc_id}/summary`, { method: "POST" });
    const { json, text } = await safeJson(res);
    if (!res.ok) throw new Error(json?.detail || text || `HTTP ${res.status}`);

    els.summaryOut.textContent = json.summary || "";
    els.summaryCits.innerHTML = citationsHtml(json.citations);
  } catch (e) {
    showErr(els.summaryErr, `Error:\n${e.message}`);
  } finally {
    els.summaryBtn.disabled = false;
    els.summaryBtn.textContent = "Generar resumen";
  }
}

async function doPlan() {
  showErr(els.planErr, "");
  els.planOut.textContent = "";
  els.planCits.innerHTML = "";
  if (!state.doc_id) return showErr(els.planErr, "Primero sube un documento.");

  els.planBtn.disabled = true;
  els.planBtn.textContent = "Generando...";

  try {
    const res = await fetch(`${api()}/documents/${state.doc_id}/study-plan`, { method: "POST" });
    const { json, text } = await safeJson(res);
    if (!res.ok) throw new Error(json?.detail || text || `HTTP ${res.status}`);

    els.planOut.textContent = json.study_plan || "";
    els.planCits.innerHTML = citationsHtml(json.citations);
  } catch (e) {
    showErr(els.planErr, `Error:\n${e.message}`);
  } finally {
    els.planBtn.disabled = false;
    els.planBtn.textContent = "Generar plan";
  }
}

function renderPractice(questions) {
  els.practiceList.innerHTML = "";
  (questions || []).forEach((q) => {
    const box = document.createElement("div");
    box.className = "bubble";
    box.style.maxWidth = "100%";

    const qText = q.question || "";
    const qId = q.id || "q";

    box.innerHTML = `
      <div style="font-size:13px;color:rgba(255,255,255,.65)">Pregunta ${escapeHtml(qId)}</div>
      <div style="margin-top:6px">${escapeHtml(qText)}</div>
      <div style="margin-top:10px">
        <textarea class="textarea" rows="3" placeholder="Tu respuesta..." id="ans-${escapeHtml(qId)}"></textarea>
      </div>
      <div class="row" style="margin-top:10px">
        <button class="btn primary" data-grade="${escapeHtml(qId)}">Corregir</button>
      </div>
      <div class="err" id="err-${escapeHtml(qId)}"></div>
      <div id="out-${escapeHtml(qId)}" style="margin-top:10px"></div>
    `;
    els.practiceList.appendChild(box);
  });

  els.practiceList.querySelectorAll("button[data-grade]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const qid = btn.getAttribute("data-grade");
      const qObj = (questions || []).find(x => (x.id || "") === qid);
      const ansEl = document.getElementById(`ans-${qid}`);
      const outEl = document.getElementById(`out-${qid}`);
      const errEl = document.getElementById(`err-${qid}`);

      errEl.style.display = "none";
      outEl.innerHTML = "";

      const user_answer = (ansEl?.value || "").trim();
      if (!user_answer) {
        errEl.style.display = "block";
        errEl.textContent = "Escribe una respuesta primero.";
        return;
      }

      btn.disabled = true;
      btn.textContent = "Corrigiendo...";

      try {
        const url = `${api()}/documents/${state.doc_id}/practice/grade?question_id=${encodeURIComponent(qid)}&question=${encodeURIComponent(qObj.question)}&user_answer=${encodeURIComponent(user_answer)}`;
        const res = await fetch(url, { method: "POST" });
        const { json, text } = await safeJson(res);
        if (!res.ok) throw new Error(json?.detail || text || `HTTP ${res.status}`);

        const ok = json.is_correct ? "Correcto" : "Incorrecto";
        outEl.innerHTML = `
          <div class="pill">${ok} · score ${(json.score ?? 0).toFixed(2)}</div>
          <div style="margin-top:8px;white-space:pre-wrap">${escapeHtml(json.feedback || "")}</div>
          <div style="margin-top:8px;color:rgba(255,255,255,.75)"><b>Respuesta esperada:</b> ${escapeHtml(json.expected_answer || "")}</div>
          ${citationsHtml(json.citations)}
        `;
      } catch (e) {
        errEl.style.display = "block";
        errEl.textContent = `Error:\n${e.message}`;
      } finally {
        btn.disabled = false;
        btn.textContent = "Corregir";
      }
    });
  });
}

async function genPractice() {
  showErr(els.pracErr, "");
  els.practiceList.innerHTML = "";
  if (!state.doc_id) return showErr(els.pracErr, "Primero sube un documento.");

  const n = parseInt(els.nQ.value || "8", 10) || 8;

  els.genPracticeBtn.disabled = true;
  els.genPracticeBtn.textContent = "Generando...";

  try {
    const res = await fetch(`${api()}/documents/${state.doc_id}/practice/generate?n=${encodeURIComponent(n)}`, { method: "POST" });
    const { json, text } = await safeJson(res);
    if (!res.ok) throw new Error(json?.detail || text || `HTTP ${res.status}`);

    renderPractice(json.questions || []);
  } catch (e) {
    showErr(els.pracErr, `Error:\n${e.message}`);
  } finally {
    els.genPracticeBtn.disabled = false;
    els.genPracticeBtn.textContent = "Generar preguntas";
  }
}

async function askChat(question) {
  showErr(els.chatErr, "");
  if (!state.doc_id) return showErr(els.chatErr, "Primero sube un documento.");
  if (!question.trim()) return;

  appendMsg("me", question);
  els.askBtn.disabled = true;
  els.askBtn.textContent = "Enviando...";

  try {
    const res = await fetch(`${api()}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ doc_id: state.doc_id, question }),
    });

    const { json, text } = await safeJson(res);
    if (!res.ok) throw new Error(json?.detail || text || `HTTP ${res.status}`);

    appendMsg("bot", json.answer || "(sin respuesta)", citationsHtml(json.citations));
  } catch (e) {
    showErr(els.chatErr, `Error:\n${e.message}`);
  } finally {
    els.askBtn.disabled = false;
    els.askBtn.textContent = "Enviar";
    els.question.value = "";
    els.question.focus();
  }
}

/* Tabs */
els.tabs.forEach((t) => {
  t.addEventListener("click", () => {
    els.tabs.forEach(x => x.classList.remove("active"));
    t.classList.add("active");
    const id = t.getAttribute("data-tab");
    Object.values(els.panels).forEach(p => p.classList.remove("active"));
    els.panels[id].classList.add("active");
  });
});

/* Eventos */
els.uploadBtn.addEventListener("click", () => uploadFile(els.file.files[0]));
els.clearBtn.addEventListener("click", () => {
  localStorage.clear();
  setDocInfo({ doc_id: "", filename: "", chunks: "" });
  els.msgs.innerHTML = "";
  els.summaryOut.textContent = "";
  els.planOut.textContent = "";
  els.practiceList.innerHTML = "";
  showErr(els.uploadErr, ""); showErr(els.chatErr, "");
  showErr(els.summaryErr, ""); showErr(els.planErr, ""); showErr(els.pracErr, "");
  appendMsg("bot", "Listo. Sube un documento para comenzar.");
});

els.summaryBtn.addEventListener("click", doSummary);
els.planBtn.addEventListener("click", doPlan);
els.genPracticeBtn.addEventListener("click", genPractice);

els.askBtn.addEventListener("click", () => askChat(els.question.value));
els.resetChatBtn.addEventListener("click", () => {
  els.msgs.innerHTML = "";
  showErr(els.chatErr, "");
  appendMsg("bot", "Chat reiniciado.");
});

els.question.addEventListener("keydown", (e) => {
  if (e.ctrlKey && e.key === "Enter") askChat(els.question.value);
});

/* Init */
setDocInfo(state);
appendMsg("bot", "Bienvenido. Sube un documento para comenzar.");
healthCheck();
setInterval(healthCheck, 5000);
