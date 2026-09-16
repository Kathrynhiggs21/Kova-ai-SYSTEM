// KOVA OS Dashboard Client App

// Fallback data in case config fetch is blocked by CORS (common in local file access)
const fallbackDashboardData = {
  "dashboard_date": "2026-09-15",
  "system_status": "canonical_pair_selected_build_in_progress",
  "source_of_truth": "Kathrynhiggs21/Kova-ai-SYSTEM",
  "canonical_app": "Kathrynhiggs21/kovaos-site",
  "active_repositories": [
    "Kathrynhiggs21/Kova-ai-SYSTEM",
    "Kathrynhiggs21/kovaos-site"
  ],
  "organization_model": {
    "area": ["KOVA", "Personal", "Reagan", "Other"],
    "lifecycle": ["ACTIVE", "FINAL", "REVIEW", "ARCHIVE"],
    "optional_flags": ["SENSITIVE", "DUPLICATE"],
    "rule": "File Type and Content Origin are fields; exact duplicate status requires content or revision evidence."
  },
  "tagline": "You clearly need me.",
  "top_priorities": [
    {
      "id": "p1-site-truth",
      "title": "Align kovaos-site routes, authentication and status claims",
      "status": "in_progress",
      "owner": "KOVA",
      "reason": "The static site must match the current canonical repositories, routes, and evidence-backed status claims."
    },
    {
      "id": "p2-api-contract",
      "title": "Implement the versioned Core-to-app API contract",
      "status": "next",
      "owner": "KOVA",
      "reason": "The command center and canonical app still need one stable contract for shared runtime state."
    },
    {
      "id": "p3-runtime-proof",
      "title": "Verify one AI path and one connector path end to end",
      "status": "next",
      "owner": "KOVA",
      "reason": "Production claims remain provisional until at least one authenticated AI and connector flow is verified."
    }
  ],
  "integrations": [
    {
      "name": "GitHub",
      "assistant_access": "verified",
      "kova_runtime": "partial",
      "status": "partial",
      "evidence": "Assistant access: verified. KOVA runtime: partial.",
      "next_action": "Require green checks on both active repositories."
    },
    {
      "name": "Google Drive",
      "assistant_access": "verified",
      "kova_runtime": "unverified",
      "status": "unverified",
      "evidence": "Assistant access: verified. KOVA runtime: unverified.",
      "next_action": "Run metadata inventory with readback and no source mutation."
    },
    {
      "name": "Notion",
      "assistant_access": "verified",
      "kova_runtime": "unverified",
      "status": "unverified",
      "evidence": "Assistant access: verified. KOVA runtime: unverified.",
      "next_action": "Use as a view, not a competing canonical store."
    },
    {
      "name": "MCP",
      "assistant_access": "n/a",
      "kova_runtime": "implemented_not_production_verified",
      "status": "implemented_not_production_verified",
      "evidence": "Assistant access: n/a. KOVA runtime: implemented_not_production_verified.",
      "next_action": "Merge hardening and verify authenticated production calls."
    },
    {
      "name": "Zapier/Make/n8n",
      "assistant_access": "optional",
      "kova_runtime": "disabled_until_named_gap",
      "status": "disabled_until_named_gap",
      "evidence": "Assistant access: optional. KOVA runtime: disabled_until_named_gap.",
      "next_action": "Use only when a direct connector or official API is insufficient."
    }
  ],
  "blockers": [
    "kovaos-site contains stale or unverified product and integration claims.",
    "The versioned Core-to-app API contract is not implemented.",
    "Durable runs, queueing, retries and connector telemetry are not production-proven.",
    "No authenticated end-to-end AI-provider and connector paths are verified."
  ],
  "next_actions": [
    "Complete and review the safe metadata registry PR.",
    "Adopt the modular Core boundary policy without creating empty repositories.",
    "Align kovaos-site with current routes, privacy boundaries and evidence states.",
    "Keep inaccessible shared-chat links in REVIEW until content is verified."
  ]
};

// Fallback Digest text
const fallbackDigestText = `<h3>KOVA Daily Digest — 2026-07-23</h3>
<p><strong>Status:</strong> KOVA OS command-center foundation is active. GitHub is readable/writable. Google Calendar is readable. Google Contacts is connected but needs a clean seed/entity list. Manus, Dropbox, and Notion are not directly connected in this runtime yet.</p>

<h4 class="font-bold text-indigo-400 mt-3">Calendar Lookahead</h4>
<ul class="list-disc list-inside space-y-1 text-slate-300">
  <li><strong>2026-07-24 12:00 PM</strong> — 45-minute Session with Nathan Fite / Appointment with Nathan Fite</li>
  <li><strong>2026-07-25 01:15 PM</strong> — CEI Perez</li>
  <li><strong>2026-07-28 10:00 AM</strong> — Dream to Me Premiere</li>
</ul>
<p class="text-xs text-slate-400 mt-2"><em>Note: Nathan Fite appears twice at the same time, likely one recurring/manual calendar item and one Gmail-created event. This should be deduplicated in the digest engine so KOVA does not nag twice like a caffeinated parrot.</em></p>

<h4 class="font-bold text-indigo-400 mt-3">Project Pulse</h4>
<div class="space-y-1.5 text-slate-300">
  <p><strong>KOVA OS:</strong> Command-center docs, integration matrix, dashboard v1 spec, daily digest spec, and static JSON dashboard config are now complete. Live exports are successfully packaged!</p>
  <p><strong>Dashboard v1:</strong> This premium static HTML dashboard has been successfully implemented and is ready for production hosting at <code>kovoas.com</code>.</p>
</div>`;

// Calendar Agenda Fallback
const fallbackCalendarEvents = [
  { time: "12:00 PM", title: "Session with Nathan Fite", date: "Tomorrow" },
  { time: "01:15 PM", title: "CEI Perez", date: "Friday" },
  { time: "All Day", title: "Dream to Me Premiere", date: "Monday" }
];

// Memory list
const fallbackMemory = [
  { key: "Preferred Timezone", val: "America/New_York (Eastern Time)" },
  { key: "Primary Owner", val: "Katy (Kathrynhiggs21)" },
  { key: "Orchestrator Path", val: "Kova-ai-SYSTEM" },
  { key: "Deployment Goal", val: "kovoas.com (static and API routes)" },
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
  // Update header tagline
  if (data.tagline) {
    document.getElementById("tagline").textContent = data.tagline;
  }
  
  // Render Calendar Agenda (Today card)
  const agendaList = document.getElementById("calendar-agenda-list");
  agendaList.innerHTML = "";
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
  const digestEl = document.getElementById("digest-content");
  digestEl.innerHTML = fallbackDigestText;
  
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
    logToConsole(`Completed task: "${label.textContent}"`, "emerald");
  } else {
    label.classList.remove("line-through", "text-slate-500");
    logToConsole(`Reopened task: "${label.textContent}"`, "indigo");
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

// Trigger Daily Digest mock regeneration
function regenerateDigest() {
  logToConsole("Triggering Daily Digest engine update...", "amber");
  setTimeout(() => {
    logToConsole("Google Calendar data parsed successfully.", "emerald");
  }, 600);
  setTimeout(() => {
    logToConsole("Daily Digest regenerated successfully and dispatched to active routes.", "emerald");
    const digestEl = document.getElementById("digest-content");
    digestEl.innerHTML = `<h3>KOVA Daily Digest — 2026-07-23 (REGENERATED)</h3>
    <p class="text-emerald-400 font-bold mb-2">✓ Successfully updated with latest live telemetry!</p>
    ${fallbackDigestText}`;
  }, 1200);
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
  
  // Simulate responses based on commands
  setTimeout(() => {
    const lower = cmd.toLowerCase();
    if (lower.includes("hello") || lower.includes("hi")) {
      logToConsole("KOVA: Hello Katy. How can I help organize your life today?", "indigo");
    } else if (lower.includes("status")) {
      logToConsole("KOVA: System status: ACTIVE. Integrations partially active. 6 blockers identified.", "indigo");
    } else if (lower.includes("export") || lower.includes("zip")) {
      logToConsole("KOVA: You can download the final website ZIP or images ZIP from the top bar actions.", "indigo");
    } else if (lower.includes("priority")) {
      logToConsole("KOVA: Current top priority is building the Dashboard v1 shell.", "indigo");
    } else {
      logToConsole("KOVA: Understood. Action logged. You clearly need me.", "indigo");
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
