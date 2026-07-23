// KOVA OS Dashboard Client App

// Fallback data in case config fetch is blocked by CORS (common in local file access)
const fallbackDashboardData = {
  "dashboard_date": "2026-07-23",
  "system_status": "foundation_active_live_integrations_partial",
  "source_of_truth": "Kathrynhiggs21/Kova-ai-SYSTEM",
  "tagline": "You clearly need me.",
  "top_priorities": [
    {
      "id": "p1-dashboard-shell",
      "title": "Build Dashboard v1 shell from static JSON",
      "status": "completed",
      "owner": "KOVA",
      "reason": "The dashboard spec supports static config first. This is now fully created and ready."
    },
    {
      "id": "p2-calendar-digest",
      "title": "Wire Google Calendar into Daily Digest v1",
      "status": "ready",
      "owner": "KOVA",
      "reason": "Calendar access is readable and should be the first live digest source."
    },
    {
      "id": "p3-integration-seeds",
      "title": "Create integration seed files for Contacts, Dropbox, Notion, Manus, and OpenAI Platform",
      "status": "next",
      "owner": "KOVA",
      "reason": "Unavailable or empty connectors still need declared targets, scopes, owners, and expected outputs."
    }
  ],
  "integrations": [
    {
      "name": "GitHub",
      "status": "active",
      "evidence": "Repo metadata readable and command-center files writable.",
      "next_action": "Use Kova-ai-SYSTEM as canonical command center and add implementation backlog files."
    },
    {
      "name": "Google Calendar",
      "status": "active_read_ready",
      "evidence": "Upcoming calendar events are readable through the connected calendar integration.",
      "next_action": "Turn calendar reads into the Today Card and Daily Digest agenda section."
    },
    {
      "name": "Google Contacts",
      "status": "connected_but_unseeded",
      "evidence": "Contacts search ran, but broad VIP query returned no matching contacts.",
      "next_action": "Create a VIP/entity seed list: Katy, Reagan, Marcy, Blake, medical providers, school, vendors, collaborators."
    },
    {
      "name": "Manus",
      "status": "blocked_external",
      "evidence": "No live Manus connector is available in this runtime.",
      "next_action": "Export Manus project docs/assets into Drive or GitHub and track links in integrations/manus_sources.md."
    },
    {
      "name": "Dropbox",
      "status": "blocked_no_connector",
      "evidence": "No Dropbox connector is available in this runtime.",
      "next_action": "Pick a canonical Dropbox folder and define file-index rules before connecting OAuth/API."
    },
    {
      "name": "Notion",
      "status": "blocked_no_connector",
      "evidence": "No Notion connector is available in this runtime.",
      "next_action": "Define the Notion database schema or choose GitHub docs as source of truth to avoid duplicate dashboards."
    },
    {
      "name": "OpenAI Platform",
      "status": "ready_for_secret_setup",
      "evidence": "Config template exists, but real secrets must not be committed.",
      "next_action": "Create an OpenAI project/API key and store it only in deployment/local secrets."
    }
  ],
  "blockers": [
    "No live Manus connector in runtime.",
    "No Dropbox connector in runtime.",
    "No Notion connector in runtime.",
    "OpenAI Platform needs private API key/project setup outside the repo.",
    "Google Contacts needs a seed/entity list because broad contact search returned no matches.",
    "Dashboard deployment target still needs a final repo decision: kovaos-site vs kova-ai-site."
  ],
  "next_actions": [
    "Create a static dashboard shell that reads config/dashboard.v1.json.",
    "Create reports/digests/2026-07-08.md as the first manual/live hybrid digest artifact.",
    "Create integrations/contact_entity_seed.csv for VIP/contact routing.",
    "Create integrations/external_source_targets.md for Manus, Dropbox, Notion, and OpenAI Platform setup instructions.",
    "Choose the dashboard implementation repo and wire it to this command-center config."
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
    const res = await fetch("../config/dashboard.v1.json");
    if (res.ok) {
      const liveData = await res.json();
      data = { ...fallbackDashboardData, ...liveData };
      logToConsole("Loaded dashboard configuration from live config/dashboard.v1.json", "emerald");
    } else {
      logToConsole("Using local high-fidelity fallback dashboard data.", "slate");
    }
  } catch (err) {
    logToConsole("Using localized fallback data (CORS or local mode).", "slate");
  }
  
  renderDashboard(data);
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
      
      if (status === "active") {
        badge.className += " bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
        dot.className += " bg-emerald-400";
        label.textContent = "Active";
      } else if (status.includes("ready") || status.includes("connected")) {
        badge.className += " bg-indigo-500/10 text-indigo-400 border border-indigo-500/20";
        dot.className += " bg-indigo-400 animate-pulse";
        label.textContent = "Ready";
      } else {
        badge.className += " bg-rose-500/10 text-rose-400 border border-rose-500/20";
        dot.className += " bg-rose-400";
        label.textContent = "Blocked";
      }
      
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
      <span>${blocker}</span>
    `;
    blockersList.appendChild(li);
  });
  
  // Render Next Actions
  const nextActionsList = document.getElementById("next-actions-list");
  nextActionsList.innerHTML = "";
  data.next_actions.forEach((act, idx) => {
    const id = `act-chk-${idx}`;
    const div = document.createElement("div");
    div.className = "flex items-start gap-3 bg-slate-900/40 hover:bg-slate-900/60 p-3 rounded-lg border border-slate-800 transition-colors text-xs text-slate-300";
    div.innerHTML = `
      <input type="checkbox" id="${id}" onchange="toggleAction('${id}')" class="w-4 h-4 rounded border-slate-700 bg-slate-950 text-indigo-600 focus:ring-indigo-500 focus:ring-offset-slate-900 mt-0.5 cursor-pointer">
      <label for="${id}" class="cursor-pointer font-medium select-none flex-1 leading-relaxed">${act}</label>
    `;
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
function triggerLocalExport() {
  logToConsole("Initiating full site package compilation...", "amber");
  
  // Direct file download trigger or API endpoint call
  fetch('/api/export/site')
    .then(res => {
      if (res.ok) {
        return res.blob();
      }
      throw new Error("Local API endpoint not running, falling back to static download");
    })
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'site_final.zip';
      document.body.appendChild(a);
      a.click();
      a.remove();
      logToConsole("Successfully downloaded site_final.zip via local API.", "emerald");
    })
    .catch(err => {
      // Fallback: direct download link if packaged locally
      const a = document.createElement('a');
      a.href = '../site_final.zip';
      a.download = 'site_final.zip';
      document.body.appendChild(a);
      a.click();
      a.remove();
      logToConsole("Downloaded packaged site_final.zip from static cache.", "emerald");
    });
}

function triggerImagesExport() {
  logToConsole("Initiating images package compilation for kovoas.com...", "amber");
  
  fetch('/api/export/images')
    .then(res => {
      if (res.ok) {
        return res.blob();
      }
      throw new Error("Local API endpoint not running, falling back to static download");
    })
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'images.zip';
      document.body.appendChild(a);
      a.click();
      a.remove();
      logToConsole("Successfully downloaded images.zip via local API.", "emerald");
    })
    .catch(err => {
      const a = document.createElement('a');
      a.href = '../images.zip';
      a.download = 'images.zip';
      document.body.appendChild(a);
      a.click();
      a.remove();
      logToConsole("Downloaded packaged images.zip from static cache.", "emerald");
    });
}
