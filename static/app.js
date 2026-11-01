"use strict";

const byId = (id) => document.getElementById(id);
const svgNamespace = "http://www.w3.org/2000/svg";
const storageKey = "simple-rag-session-uploads";
let selectedFile = null;
let uploading = false;
let toastTimeout;
let documents = [];

// The API has no document-list route. Keep only this tab's upload receipts.
try {
  const stored = JSON.parse(sessionStorage.getItem(storageKey) || "[]");
  if (Array.isArray(stored)) {
    documents = stored.filter((item) => item && typeof item.source === "string"
      && Number.isFinite(item.pages_read) && Number.isFinite(item.chunks_stored));
  }
} catch { /* Uploads still work when browser storage is unavailable. */ }

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function icon(name) {
  const svg = document.createElementNS(svgNamespace, "svg");
  svg.classList.add("icon");
  svg.setAttribute("aria-hidden", "true");
  const use = document.createElementNS(svgNamespace, "use");
  use.setAttribute("href", `#icon-${name}`);
  svg.append(use);
  return svg;
}

function notify(message, isError = false) {
  clearTimeout(toastTimeout);
  const toast = byId("toast");
  toast.textContent = message;
  toast.className = `toast ${isError ? "error" : "success"}`;
  toast.hidden = false;
  toastTimeout = setTimeout(() => { toast.hidden = true; }, 3500);
}

function showError(id, message = "") {
  const target = byId(id);
  target.textContent = message;
  target.hidden = !message;
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(path, options);
  } catch {
    throw new Error("Cannot reach the app. Check your connection and try again.");
  }
  let data;
  try { data = await response.json(); } catch {
    throw new Error(response.ok
      ? "The app returned an unreadable response. Please try again."
      : `The request failed (${response.status}). Please try again.`);
  }
  if (!response.ok) {
    let detail = data.detail;
    if (Array.isArray(detail)) detail = detail.map((item) => item.msg).join(" ");
    throw new Error(typeof detail === "string" ? detail : `The request failed (${response.status}). Please try again.`);
  }
  return data;
}

async function checkHealth() {
  const button = byId("refresh-health");
  button.disabled = true;
  byId("health-status").className = "status-pill info";
  byId("health-label").textContent = "Connecting";
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000);
  try {
    const data = await request("/health", { signal: controller.signal });
    if (data.status !== "OK") throw new Error("Unavailable");
    byId("health-status").className = "status-pill success";
    byId("health-label").textContent = "API online";
  } catch {
    byId("health-status").className = "status-pill error";
    byId("health-label").textContent = "API offline";
  } finally {
    clearTimeout(timeout);
    button.disabled = false;
  }
}

function renderDocuments() {
  const list = byId("document-list");
  list.replaceChildren();
  byId("document-count").textContent = documents.length;
  byId("documents-empty").hidden = documents.length > 0;
  for (const doc of documents) {
    const row = element("div", "document-item");
    const fileIcon = element("span", "file-icon");
    fileIcon.append(icon("file"));
    const details = element("div", "file-details");
    details.append(element("strong", "", doc.source));
    details.append(element("span", "", `${doc.pages_read} ${doc.pages_read === 1 ? "page" : "pages"} · ${doc.chunks_stored} ${doc.chunks_stored === 1 ? "chunk" : "chunks"} indexed`));
    const ready = element("span", "ready-icon");
    ready.title = "Ready to search";
    ready.setAttribute("aria-label", "Ready to search");
    ready.append(icon("check"));
    row.append(fileIcon, details, ready);
    list.append(row);
  }
}

function selectFile(file) {
  if (uploading) return;
  showError("upload-error");
  if (file && !file.name.toLowerCase().endsWith(".pdf")) {
    showError("upload-error", "Choose a PDF file. Other file types are not supported.");
    return;
  }
  if (file && file.size === 0) {
    showError("upload-error", "This PDF is empty. Choose a file with readable text.");
    return;
  }
  selectedFile = file || null;
  byId("selected-file").hidden = !selectedFile;
  byId("upload-button").disabled = !selectedFile;
  if (selectedFile) {
    byId("selected-name").textContent = file.name;
    byId("selected-size").textContent = file.size < 1024 * 1024
      ? `${Math.max(1, Math.round(file.size / 1024))} KB`
      : `${(file.size / (1024 * 1024)).toFixed(1)} MB`;
  }
  // Allow choosing the same file again, including after a failed upload.
  byId("pdf-file").value = "";
}

byId("pdf-file").addEventListener("change", (event) => selectFile(event.target.files[0]));
byId("remove-file").addEventListener("click", () => selectFile(null));

const dropZone = byId("drop-zone");
let dragDepth = 0;
dropZone.addEventListener("dragenter", (event) => {
  event.preventDefault();
  dragDepth += 1;
  if (!uploading) dropZone.classList.add("dragging");
});
dropZone.addEventListener("dragover", (event) => event.preventDefault());
dropZone.addEventListener("dragleave", (event) => {
  event.preventDefault();
  dragDepth -= 1;
  if (dragDepth <= 0) dropZone.classList.remove("dragging");
});
dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  dragDepth = 0;
  dropZone.classList.remove("dragging");
  if (uploading) return;
  if (event.dataTransfer.files.length !== 1) {
    showError("upload-error", "Choose one PDF at a time.");
    return;
  }
  selectFile(event.dataTransfer.files[0]);
});
// Stop a dropped file outside the upload area from replacing the page.
window.addEventListener("dragover", (event) => event.preventDefault());
window.addEventListener("drop", (event) => event.preventDefault());

byId("upload-button").addEventListener("click", async () => {
  if (!selectedFile || uploading) return;
  uploading = true;
  byId("upload-button").disabled = true;
  byId("remove-file").disabled = true;
  byId("pdf-file").disabled = true;
  byId("upload-button-label").textContent = "Preparing document…";
  byId("upload-progress").hidden = false;
  dropZone.classList.add("uploading");
  showError("upload-error");
  try {
    const body = new FormData();
    body.append("file", selectedFile);
    const data = await request("/ingest", { method: "POST", body });
    documents.unshift(data);
    renderDocuments();
    try { sessionStorage.setItem(storageKey, JSON.stringify(documents)); } catch { /* Optional browser session receipt. */ }
    selectedFile = null;
    byId("selected-file").hidden = true;
    notify("Document uploaded and ready to search.");
  } catch (error) {
    showError("upload-error", error.message);
  } finally {
    uploading = false;
    byId("upload-button").disabled = !selectedFile;
    byId("remove-file").disabled = false;
    byId("pdf-file").disabled = false;
    byId("upload-button-label").textContent = "Upload document";
    byId("upload-progress").hidden = true;
    dropZone.classList.remove("uploading");
  }
});

function activateTab(mode, focus = false) {
  for (const name of ["ask", "brief"]) {
    const active = name === mode;
    const tab = byId(`${name}-tab`);
    tab.classList.toggle("active", active);
    tab.setAttribute("aria-selected", String(active));
    tab.tabIndex = active ? 0 : -1;
    byId(`${name}-panel`).hidden = !active;
  }
  if (focus) byId(`${mode}-tab`).focus();
}

for (const mode of ["ask", "brief"]) {
  byId(`${mode}-tab`).addEventListener("click", () => activateTab(mode));
  byId(`${mode}-tab`).addEventListener("keydown", (event) => {
    if (["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) {
      event.preventDefault();
      const next = event.key === "Home" ? "ask" : event.key === "End" ? "brief" : mode === "ask" ? "brief" : "ask";
      activateTab(next, true);
    }
  });
}

document.querySelectorAll(".suggestion").forEach((button) => {
  button.addEventListener("click", () => {
    const field = byId(button.dataset.mode === "ask" ? "question" : "topic");
    field.value = button.dataset.prompt;
    field.focus();
  });
});

function renderMarkdown(text) {
  const response = element("div", "response-text markdown-body");
  // Fail safely to readable text if a local Markdown dependency cannot load.
  if (!window.marked || !window.DOMPurify) {
    response.classList.add("markdown-fallback");
    response.textContent = text;
    return response;
  }
  const html = window.marked.parse(text, { gfm: true, breaks: true, async: false });
  const fragment = window.DOMPurify.sanitize(html, {
    RETURN_DOM_FRAGMENT: true,
    ALLOWED_TAGS: [
      "p", "br", "hr", "h1", "h2", "h3", "h4", "h5", "h6",
      "strong", "b", "em", "i", "del", "s", "u", "mark", "small",
      "sub", "sup", "blockquote", "ul", "ol", "li", "input",
      "pre", "code", "kbd", "samp", "a", "img", "figure", "figcaption",
      "table", "thead", "tbody", "tfoot", "tr", "th", "td", "caption",
      "details", "summary", "div", "span", "dl", "dt", "dd", "abbr",
    ],
    ALLOWED_ATTR: [
      "href", "title", "src", "alt", "width", "height", "align",
      "start", "reversed", "type", "checked", "disabled", "colspan", "rowspan", "scope",
    ],
    ALLOW_DATA_ATTR: false,
    ALLOW_ARIA_ATTR: false,
  });
  // Task-list checkboxes are display-only; discard other form controls.
  fragment.querySelectorAll("input").forEach((input) => {
    if (input.type !== "checkbox") input.remove();
    else input.disabled = true;
  });
  fragment.querySelectorAll("a[href]").forEach((link) => {
    link.target = "_blank";
    link.rel = "noopener noreferrer";
  });
  fragment.querySelectorAll("img").forEach((image) => {
    image.loading = "lazy";
    image.referrerPolicy = "no-referrer";
  });
  fragment.querySelectorAll("table").forEach((table, index) => {
    const wrapper = element("div", "markdown-table-scroll");
    wrapper.tabIndex = 0;
    wrapper.setAttribute("role", "region");
    wrapper.setAttribute("aria-label", `Response table ${index + 1}; scroll horizontally to see all columns`);
    table.replaceWith(wrapper);
    wrapper.append(table);
  });
  response.append(fragment);
  return response;
}

function renderResult(mode, query, data) {
  const text = mode === "ask" ? data.answer : data.brief;
  if (typeof text !== "string") throw new Error("The app returned an incomplete response. Please try again.");
  const content = element("div", "result-content");
  const heading = element("div", "result-heading");
  const title = element("h2");
  title.append(icon(mode === "ask" ? "chat" : "spark"), document.createTextNode(mode === "ask" ? "Your answer" : "Your brief"));
  const copy = element("button", "copy-button");
  copy.type = "button";
  copy.append(icon("copy"), document.createTextNode("Copy"));
  copy.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(text);
      notify("Response copied.");
    } catch {
      notify("Could not copy. Select the response text to copy it manually.", true);
    }
  });
  heading.append(title, copy);
  content.append(heading, element("p", "result-query", query), renderMarkdown(text || "No response was generated. Try a more specific question or topic."));
  const sources = element("section", "sources");
  const sourcesTitle = element("h3");
  sourcesTitle.append(icon("link"), document.createTextNode("Source references"));
  sources.append(sourcesTitle);
  if (Array.isArray(data.sources) && data.sources.length) {
    const list = element("div", "source-list");
    for (const source of data.sources) {
      const reference = element("div", "source-reference");
      reference.append(icon("file"), element("span", "source-name", source.source || "Document"));
      if (source.page !== undefined && source.page !== null) {
        reference.append(element("span", "source-page", `p. ${source.page}`));
      }
      list.append(reference);
    }
    sources.append(list);
  } else {
    sources.append(element("p", "no-sources", "No source references were returned. Upload a relevant PDF or try another question or topic."));
  }
  content.append(sources);
  byId(`${mode}-result`).replaceChildren(content);
}

for (const mode of ["ask", "brief"]) {
  const form = byId(`${mode}-form`);
  const input = byId(mode === "ask" ? "question" : "topic");
  let pending = false;
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (pending) return;
    const query = input.value.trim();
    if (!query) {
      showError(`${mode}-error`, mode === "ask" ? "Enter a question to get started." : "Enter a topic for your brief.");
      input.focus();
      return;
    }
    pending = true;
    const button = byId(`${mode}-button`);
    const result = byId(`${mode}-result`);
    // Retain the last successful result if a subsequent request fails.
    const previous = Array.from(result.childNodes);
    const loading = element("div", "result-loading");
    loading.append(element("span", "spinner"), document.createTextNode(mode === "ask" ? "Finding an answer in your documents…" : "Putting your brief together…"));
    result.replaceChildren(loading);
    result.setAttribute("aria-busy", "true");
    button.disabled = true;
    input.readOnly = true;
    button.querySelector("span").textContent = mode === "ask" ? "Finding answer…" : "Creating brief…";
    showError(`${mode}-error`);
    try {
      const payload = mode === "ask" ? { question: query } : { topic: query };
      const data = await request(`/${mode}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      renderResult(mode, query, data);
    } catch (error) {
      result.replaceChildren(...previous);
      showError(`${mode}-error`, error.message);
    } finally {
      pending = false;
      result.setAttribute("aria-busy", "false");
      button.disabled = false;
      input.readOnly = false;
      button.querySelector("span").textContent = mode === "ask" ? "Ask question" : "Create brief";
    }
  });
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      form.requestSubmit();
    }
  });
}

byId("refresh-health").addEventListener("click", checkHealth);
renderDocuments();
checkHealth();
