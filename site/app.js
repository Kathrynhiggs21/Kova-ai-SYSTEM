// KOVA OS Dashboard Client App

// Fallback data in case config fetch is blocked by CORS (common in local file access)
const fallbackDashboardData = {
  "dashboard_date": "2026-09-15",
  "system_status": "architecture_aligned_runtime_integrations_unverified",
  "source_of_truth": "Kathrynhiggs21/Kova-ai-SYSTEM",
  "canonical_application": "Kathrynhiggs21/kovaos-site",
  "tagline": "You clearly need me.",
  "top_priorities": [
    {
      "id": "p1-api-contract",
      "title": "Define the versioned Core-to-site API",
      "status": "next",
      "owner": "KOVA",
      "reason": "The canonical repositories are settled; their authenticated runtime contract still needs implementation and proof."
    },
    {
      "id": "p2-connector-proof",
      "title": "Verify one connector end to end",
      "status": "blocked",
      "owner": "KOVA",
      "reason": "Configured or documented integrations must not appear live until authentication, health, and last-success evidence exist."
    },
    {
      "id": "p3-donor-migration",
      "title": "Audit dashboard donor features",
      "status": "review",
      "owner": "KOVA",
      "reason": "Move only unique, verified features from kova-ai-dash into kovaos-site before archiving the donor."
    }
  ],
  "integrations": [
    {
      "name": "GitHub",
      "status": "active",
      "evidence": "Canonical repositories and reviewed change workflow are available.",
      "next_action": "Keep Core and site changes behind exact-head CI and review gates."
    },
    {
      "name": "KOVA Core API",
      "status": "implemented_unverified_in_production",
      "evidence": "FastAPI, health, MCP, repository status, and export routes exist in Core.",
      "next_action": "Verify the protected production health and authenticated API boundary."
    },
    {
      "name": "KOVA Web Application",
      "status": "canonical",
      "evidence": "kovaos-site is the sole canonical authenticated application repository.",
      "next_action": "Connect it to a versioned Core API and verify private deployment behavior."
    },
    {
      "name": "External Connectors",
      "status": "disabled_or_unverified",
      "evidence": "No repository evidence currently proves production health for optional providers.",
      "next_action": "Enable one least-privilege connector only after authentication, health, audit, and revocation tests pass."
    }
  ],
  "blockers": [
    "No verified production Core-to-site API contract.",
    "No proof-backed end-to-end connector path.",
    "Durable run history, queueing, retries, and connector telemetry remain incomplete.",
    "The duplicate legacy Core Vercel project still creates configuration-drift risk."
  ],
  "next_actions": [
    "Merge architecture changes only after exact-head CI and review pass.",
    "Implement and test the versioned Core-to-site API.",
    "Verify one authenticated connector path with audit evidence.",
    "Migrate unique donor features before archiving any repository."
  ],
  "organization_model": {
    "area": [
      "KOVA",
      "Personal",
      "Reagan",
      "Other"
    ],
    "lifecycle": [
      "ACTIVE",
      "FINAL",
      "REVIEW",
      "ARCHIVE"
    ],
    "optional_flags": [
      "SENSITIVE",
      "DUPLICATE"
    ],
    "rule": "File type and content origin are metadata fields. Exact duplicates require content or revision evidence; source files are never moved or copied."
  }
};

// The reference dashboard holds configuration, not verified live provider data.
let currentDashboardData = fallbackDashboardData;
const fallbackCalendarEvents = [];

function describeSystemStatus(status) {
  const value = String(status || "unknown");
  return {
    label: value === "blocked" ? "Blocked" : "Needs verification",
    detail: `Configuration status: ${value.replaceAll("_", " ")}. Production routes and provider connections still need verification.`
  };
}

function renderSystemStatus(data) {
  const status = describeSystemStatus(data.system_status);
  document.getElementById("badge-status").textContent = status.label;
  document.getElementById("system-status-detail").textContent = status.detail;
}

function renderDigest(data) {
  const target = document.getElementById("digest-content");
  target.innerHTML = "";
  const heading = document.createElement("h3");
  heading.textContent = `KOVA configuration snapshot — ${data.dashboard_date || "date unknown"}`;
  const detail = document.createElement("p");
  detail.textContent = "A live digest and current calendar reads have not been verified. Check the canonical web application for authenticated work.";
  target.appendChild(heading);
  target.appendChild(detail);
  const blockers = document.createElement("ul");
  (data.blockers || []).forEach(blocker => {
    const row = document.createElement("li");
    row.textContent = blocker;
    blockers.appendChild(row);
  });
  target.appendChild(blockers);
}

// Memory list
const fallbackMemory = [
  { key: "Preferred Timezone", val: "America/New_York (Eastern Time)" },
  { key: "Primary Owner", val: "Katy (Kathrynhiggs21)" },
  { key: "Orchestrator Path", val: "Kova-ai-SYSTEM" },
  { key: "Deployment Goal", val: "kovaos.com via the canonical kovaos-site application" },
  { key: "Tone and Voice", val: "Slightly playful, helpful, says 'You clearly need me.'" }
];

// Initialize application
document.addEventListener("DOMContentLoaded", () => {
  startClock();
  loadDashboardData();
});

// Start live clock matching Eastern Time
function startClock() {
  const timeEl = document.getElementById("live-time");
  const dateEl = document.getElementById("live-date");
  
  setInterval(() => {
    const now = new Date();
    // Force America/New_York Timezone for clock display
    const nyTimeStr = now.toLocaleTimeString("en-US", { timeZone: "America/New_York", hour12: true, hour: '2-digit', minute: '2-digit', second: '2-digit', timeZoneName: 'short' });
    const nyDateStr = now.toLocaleDateString("en-US", { timeZone: "America/New_York", weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    
    timeEl.textContent = nyTimeStr;
    dateEl.textContent = nyDateStr;
  }, 1000);
}

// Fetch dashboard config or fallback
async function loadDashboardData() {
  let data = fallbackDashboardData;
  
  try {
    for (const configPath of ["./config/dashboard.v1.json", "../config/dashboard.v1.json"]) {
      const res = await fetch(configPath);
      if (res.ok) {
        const liveData = await res.json();
        data = { ...fallbackDashboardData, ...liveData };
        logToConsole(`Loaded dashboard configuration from ${configPath}`, "emerald");
        break;
      }
    }
  } catch (err) {
    logToConsole("Using localized fallback data (CORS or local mode).", "slate");
  }
  
  renderDashboard(data);
}

function describeIntegrationStatus(status) {
  const normalized = String(status || "").toLowerCase();
  if (normalized === "active") {
    return {
      label: "Active",
      badgeClass: "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20",
      dotClass: "bg-emerald-400"
    };
  }
  if (normalized.includes("partial")) {
    return {
      label: "Partial",
      badgeClass: "bg-amber-500/10 text-amber-400 border border-amber-500/20",
      dotClass: "bg-amber-400"
    };
  }
  if (normalized.includes("implemented")) {
    return {
      label: "Implemented",
      badgeClass: "bg-sky-500/10 text-sky-400 border border-sky-500/20",
      dotClass: "bg-sky-400"
    };
  }
  if (normalized.includes("ready") || normalized.includes("connected")) {
    return {
      label: "Ready",
      badgeClass: "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20",
      dotClass: "bg-indigo-400 animate-pulse"
    };
  }
  if (normalized.includes("unverified")) {
    return {
      label: "Unverified",
      badgeClass: "bg-slate-500/10 text-slate-300 border border-slate-500/20",
      dotClass: "bg-slate-300"
    };
  }
  if (normalized.includes("disabled") || normalized.includes("optional")) {
    return {
      label: "Optional",
      badgeClass: "bg-violet-500/10 text-violet-400 border border-violet-500/20",
      dotClass: "bg-violet-400"
    };
  }
  return {
    label: "Blocked",
    badgeClass: "bg-rose-500/10 text-rose-400 border border-rose-500/20",
    dotClass: "bg-rose-400"
  };
}

// Render dynamic elements to DOM
function renderDashboard(data) {
  currentDashboardData = data;
  renderSystemStatus(data);
  // Update header tagline
  if (data.tagline) {
    document.getElementById("tagline").textContent = data.tagline;
  }
  
  // Render Calendar Agenda (Today card)
  const agendaList = document.getElementById("calendar-agenda-list");
  agendaList.innerHTML = "";
  if (fallbackCalendarEvents.length === 0) {
    agendaList.textContent = "No verified calendar feed is connected to this reference dashboard.";
  }
  fallbackCalendarEvents.forEach(evt => {
    const item = document.createElement("div");
    item.className = "flex justify-between items-center bg-slate-900/60 p-3 rounded-lg border border-slate-800 text-xs";
    item.innerHTML = `
      <div>
        <p class="font-bold text-slate-200">${evt.title}</p>
        <p class="text-[10px] text-slate-400 mt-0.5">${evt.date}</p>
      </div>
      <span class="px-2 py-0.5 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded font-mono text-[10px]">${evt.time}</span>
    `;
    agendaList.appendChild(item);
  });
  
  // Render Top Priorities (Today card)
  const prioritiesList = document.getElementById("top-priorities-list");
  prioritiesList.innerHTML = "";
  data.top_priorities.forEach((p, idx) => {
    const item = document.createElement("div");
    item.className = "bg-slate-900/60 p-3 rounded-lg border border-slate-800 text-xs flex gap-2.5 items-start";
    
    let badgeColor = "bg-indigo-500/10 text-indigo-400 border-indigo-500/20";
    if (p.status === "completed") badgeColor = "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
    else if (p.status === "ready") badgeColor = "bg-amber-500/10 text-amber-400 border-amber-500/20";
    
    item.innerHTML = `
      <span class="font-bold text-indigo-400">#${idx + 1}</span>
      <div class="flex-1">
        <div class="flex justify-between items-center">
          <p class="font-bold text-slate-200" data-kova-field="title"></p>
          <span class="px-1.5 py-0.5 rounded font-mono text-[9px] uppercase border ${badgeColor}" data-kova-field="status"></span>
        </div>
        <p class="text-[10px] text-slate-400 mt-1" data-kova-field="reason"></p>
      </div>
    `;
    item.querySelector('[data-kova-field="title"]').textContent = p.title || "";
    item.querySelector('[data-kova-field="status"]').textContent = p.status || "";
    item.querySelector('[data-kova-field="reason"]').textContent = p.reason || "";
    prioritiesList.appendChild(item);
  });
  
  // Render Daily Digest Content
  renderDigest(data);
  
  // Render Integrations Grid
  const integrationsGrid = document.getElementById("integrations-grid");
  integrationsGrid.innerHTML = "";
  data.integrations.forEach(integration => {
    const card = document.createElement("div");
    card.className = "p-4 bg-slate-900/40 rounded-xl border border-slate-800 flex items-start gap-3.5 transition-all duration-200 hover:bg-slate-900/60";
    
    let svgIcon = "";
    
    // Icon mapping with validation
    const iconName = integration.name
      .toLowerCase()
      .replaceAll(" ", "_")
      .replace(/_platform$/, "")
      .replace(/[^a-z0-9_-]/g, ""); // Remove any non-safe characters
    svgIcon = `images/${iconName}.svg`;
    
    // Build DOM safely without innerHTML injection for user data
    const img = document.createElement("img");
    img.src = svgIcon;
    img.alt = "";
    img.className = "w-8 h-8 p-1.5 bg-slate-800 rounded-lg text-slate-300";
    
    const contentDiv = document.createElement("div");
    contentDiv.className = "flex-1 min-w-0";
    
    const headerDiv = document.createElement("div");
    headerDiv.className = "flex justify-between items-center gap-2 mb-1";
    
    const nameP = document.createElement("p");
    nameP.className = "font-bold text-slate-200 text-sm truncate";
    nameP.textContent = integration.name;
    
    // Build status badge safely with DOM methods
    const createStatusBadge = (status) => {
      const badge = document.createElement("span");
      badge.className = "px-1.5 py-0.5 text-[9px] font-bold rounded-full flex items-center gap-1";
      
      const dot = document.createElement("span");
      dot.className = "w-1 h-1 rounded-full";
      
      const label = document.createElement("span");
      const statusView = describeIntegrationStatus(status);
      badge.className += ` ${statusView.badgeClass}`;
      dot.className += ` ${statusView.dotClass}`;
      label.textContent = statusView.label;
      
      badge.appendChild(dot);
      badge.appendChild(label);
      return badge;
    };
    
    const statusBadge = createStatusBadge(integration.status);
    
    headerDiv.appendChild(nameP);
    headerDiv.appendChild(statusBadge);
    
    const evidenceP = document.createElement("p");
    evidenceP.className = "text-[10px] text-slate-400 line-clamp-2";
    evidenceP.textContent = integration.evidence;
    evidenceP.setAttribute("title", integration.evidence);
    
    const actionP = document.createElement("p");
    actionP.className = "text-[10px] text-indigo-300 mt-1.5 font-semibold truncate";
    const nextLabel = document.createElement("span");
    nextLabel.className = "text-slate-500 font-normal";
    nextLabel.textContent = "Next:";
    actionP.appendChild(nextLabel);
    actionP.appendChild(document.createTextNode(" " + integration.next_action));
    
    contentDiv.appendChild(headerDiv);
    contentDiv.appendChild(evidenceP);
    contentDiv.appendChild(actionP);
    
    card.appendChild(img);
    card.appendChild(contentDiv);
    integrationsGrid.appendChild(card);
  });
  
  // Render Blockers List
  const blockersList = document.getElementById("blockers-list");
  blockersList.innerHTML = "";
  data.blockers.forEach(blocker => {
    const li = document.createElement("li");
    li.className = "flex gap-2 bg-rose-950/20 border border-rose-500/10 p-2.5 rounded-lg text-rose-300";
    li.innerHTML = `
      <svg class="w-4 h-4 text-rose-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
      <span data-kova-field="blocker"></span>
    `;
    li.querySelector('[data-kova-field="blocker"]').textContent = blocker || "";
    blockersList.appendChild(li);
  });
  
  // Render Next Actions
  const nextActionsList = document.getElementById("next-actions-list");
  nextActionsList.innerHTML = "";
  data.next_actions.forEach((act, idx) => {
    const id = `act-chk-${idx}`;
    const div = document.createElement("div");
    div.className = "flex items-start gap-3 bg-slate-900/40 hover:bg-slate-900/60 p-3 rounded-lg border border-slate-800 transition-colors text-xs text-slate-300";
    
    const input = document.createElement("input");
    input.type = "checkbox";
    input.id = id;
    input.className = "w-4 h-4 rounded border-slate-700 bg-slate-950 text-indigo-600 focus:ring-indigo-500 focus:ring-offset-slate-900 mt-0.5 cursor-pointer";
    input.addEventListener("change", () => toggleAction(id));
    
    const label = document.createElement("label");
    label.setAttribute("for", id);
    label.className = "cursor-pointer font-medium select-none flex-1 leading-relaxed";
    label.textContent = act || "";
    
    div.appendChild(input);
    div.appendChild(label);
    nextActionsList.appendChild(div);
  });
  
  // Render Memory / Preferences List
  const memoryList = document.getElementById("memory-list");
  memoryList.innerHTML = "";
  fallbackMemory.forEach(mem => {
    const div = document.createElement("div");
    div.className = "flex justify-between items-start bg-slate-900/20 border border-slate-800 p-2.5 rounded-lg";
    div.innerHTML = `
      <span class="font-semibold text-indigo-400">${mem.key}:</span>
      <span class="text-right text-slate-300 max-w-[65%]">${mem.val}</span>
    `;
    memoryList.appendChild(div);
  });
}

// Handle local actions checklist toggle
function toggleAction(id) {
  const checkbox = document.getElementById(id);
  const label = checkbox.nextElementSibling;
  if (checkbox.checked) {
    label.classList.add("line-through", "text-slate-500");
    logToConsole(`Marked locally: "${label.textContent}". This checklist is not saved to the task service.`, "emerald");
  } else {
    label.classList.remove("line-through", "text-slate-500");
    logToConsole(`Unmarked locally: "${label.textContent}". This checklist is not saved to the task service.`, "indigo");
  }
}

// Console helper
function logToConsole(msg, color = "slate") {
  const logsEl = document.getElementById("console-logs");
  const time = new Date().toLocaleTimeString("en-US", { hour12: false });
  const colorMap = {
    emerald: "text-emerald-400",
    indigo: "text-indigo-400",
    slate: "text-slate-400",
    rose: "text-rose-400",
    amber: "text-amber-400"
  };
  
  const p = document.createElement("p");
  p.className = colorMap[color] || "text-slate-300";
  
  const span = document.createElement("span");
  span.className = "text-slate-500";
  span.textContent = `[${time}] `;
  
  p.appendChild(span);
  p.appendChild(document.createTextNode(msg));
  logsEl.appendChild(p);
  logsEl.scrollTop = logsEl.scrollHeight;
}

// Refresh configuration without claiming a provider read or dispatch.
async function regenerateDigest() {
  await loadDashboardData();
  logToConsole("Configuration snapshot refreshed. Live digest generation is not connected.", "amber");
}

// Console Command submission
function handleConsoleSubmit(event) {
  if (event.key === "Enter") {
    submitConsoleCommand();
  }
}

function submitConsoleCommand() {
  const inputEl = document.getElementById("console-input");
  const cmd = inputEl.value.trim();
  if (!cmd) return;
  
  logToConsole(`User: ${cmd}`, "slate");
  inputEl.value = "";
  
  // Show local configuration guidance; this does not execute commands.
  setTimeout(() => {
    const lower = cmd.toLowerCase();
    if (lower.includes("hello") || lower.includes("hi")) {
      logToConsole("KOVA: Hello Katy. How can I help organize your life today?", "indigo");
    } else if (lower.includes("status")) {
      logToConsole(`KOVA: ${describeSystemStatus(currentDashboardData.system_status).detail}`, "indigo");
    } else if (lower.includes("export") || lower.includes("zip")) {
      logToConsole("KOVA: You can download the final website ZIP or images ZIP from the top bar actions.", "indigo");
    } else if (lower.includes("priority")) {
      logToConsole(`KOVA: ${currentDashboardData.top_priorities?.[0]?.title || "No priority has been configured."}`, "indigo");
    } else {
      logToConsole("KOVA: Command execution is not connected on this reference dashboard.", "indigo");
    }
  }, 650);
}

// Download/Export triggers (direct or API integrations)
async function fetchArchive(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Archive request failed with HTTP ${response.status}`);
  }

  const blob = await response.blob();
  const signature = new Uint8Array(await blob.slice(0, 4).arrayBuffer());
  const isZip =
    signature.length === 4 &&
    signature[0] === 0x50 &&
    signature[1] === 0x4b &&
    ((signature[2] === 0x03 && signature[3] === 0x04) ||
      (signature[2] === 0x05 && signature[3] === 0x06) ||
      (signature[2] === 0x07 && signature[3] === 0x08));
  if (!isZip) {
    throw new Error("Archive response is not a ZIP file");
  }
  return blob;
}

function downloadArchive(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => window.URL.revokeObjectURL(url), 0);
}

function requestLocalArchive(path, filename) {
  const link = document.createElement("a");
  link.href = path;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
}

async function downloadExport(apiPath, fallbackPath, filename) {
  if (window.location.protocol === "file:") {
    requestLocalArchive(fallbackPath, filename);
    logToConsole(
      `Opened the checked-in ${filename} download request; completion cannot be verified in local file mode.`,
      "amber"
    );
    return true;
  }

  try {
    const blob = await fetchArchive(apiPath);
    downloadArchive(blob, filename);
    logToConsole(`Successfully downloaded ${filename} via local API.`, "emerald");
    return true;
  } catch (apiError) {
    try {
      const blob = await fetchArchive(fallbackPath);
      downloadArchive(blob, filename);
      logToConsole(
        `Downloaded the checked-in ${filename} archive; it may be older than the current source.`,
        "amber"
      );
      return true;
    } catch (fallbackError) {
      logToConsole(
        `Unable to download ${filename}: neither the published API nor the checked-in archive is available.`,
        "rose"
      );
      return false;
    }
  }
}

function triggerLocalExport() {
  logToConsole("Preparing the latest available site package download...", "amber");
  return downloadExport("/api/export/site", "../site_final.zip", "site_final.zip");
}

function triggerImagesExport() {
  logToConsole("Preparing the latest available images package download...", "amber");
  return downloadExport("/api/export/images", "../images.zip", "images.zip");
}
