const dashboardSections = {
  overview: {
    title: "Overview",
    subtitle: "Unified command-center summary themed for KOVA OS and ready for desktop/mobile.",
    cards: [
      { title: "System Status", body: "API: healthy · Metrics: online · Routing: /dashboard enabled" },
      { title: "Manus Import Status", body: "External Manus links referenced. Direct ingestion depends on exported zip/source files available in this repo." },
      { title: "Domain Target", body: "kovaos.com and www.kovaos.com route to the API gateway, with dashboard pages at /dashboard/*." },
      { title: "Current Focus", body: "Consolidate duplicated dashboard concepts into one KOVA OS command-center experience." },
      { title: "Live Connections", body: "GitHub, Calendar, and API exports represented in the integration map for follow-up wiring." },
      { title: "Next Step", body: "Map each external source zip to explicit widgets once source files are committed to repository storage." }
    ]
  },
  integrations: {
    title: "Integrations",
    subtitle: "Detailed connectors and readiness for KOVA ecosystem services.",
    cards: [
      { title: "GitHub", body: "Connected; primary source-of-truth for code, issues, and automation metadata." },
      { title: "Google Drive", body: "Pending direct ingest from drive exports; use repo-checked assets to avoid broken dependencies." },
      { title: "Manus Dashboards", body: "Configured as external references for lovadash, kovacontrol, kova, and kovaos sources." },
      { title: "Calendar & Digest", body: "Ready to attach scheduling intelligence to dashboard cards and digest generation." },
      { title: "OpenAI/Anthropic", body: "Back-end keys managed through .env; no secrets exposed in UI." },
      { title: "Monitoring", body: "Prometheus metrics endpoint available at /metrics for observability panels." }
    ]
  },
  devices: {
    title: "Smart Devices",
    subtitle: "Placeholder pages for Sexton and other smart-device control integrations.",
    cards: [
      { title: "Sexton Hub", body: "Device bridge slot prepared for telemetry, states, and scene controls." },
      { title: "Lighting", body: "Room groups and schedules can be mapped once device API endpoints are added." },
      { title: "Security", body: "Camera and sensor status panel reserved for future authenticated feeds." },
      { title: "Climate", body: "HVAC controls and comfort automations planned for shared command workflows." },
      { title: "Media", body: "Playback targets and routines can be orchestrated through automation scenes." },
      { title: "Health of Devices", body: "Online/offline status and battery telemetry card structure is in place." }
    ]
  },
  automation: {
    title: "Automation",
    subtitle: "Operational jobs, digest generation, and orchestration actions.",
    cards: [
      { title: "Daily Digest Job", body: "Dashboard supports digest visibility and rerun hooks for scheduled summaries." },
      { title: "Backup Exports", body: "Use /api/export/site and /api/export/images to produce deployable packages." },
      { title: "Webhook Routing", body: "GitHub webhook endpoint ready for workflow-based triggers." },
      { title: "Task Queue", body: "Reserved panel for long-running integrations and job retries." },
      { title: "Alerts", body: "Dedicated cards can surface blockers and missing credential warnings." },
      { title: "Future ERP Layer", body: "This section is prepared for deeper operational modules under kovaos.com/dashboard." }
    ]
  }
};

function getRouteKey() {
  const parts = window.location.pathname.replace(/\/+$/, "").split("/");
  const key = parts[2] || "overview";
  return dashboardSections[key] ? key : "overview";
}

function render() {
  const route = getRouteKey();
  const section = dashboardSections[route];

  document.getElementById("page-title").textContent = section.title;
  document.getElementById("page-subtitle").textContent = section.subtitle;

  document.querySelectorAll(".dash-link").forEach((el) => {
    const active = el.dataset.route === route;
    el.classList.toggle("bg-indigo-600", active);
    el.classList.toggle("border-indigo-400", active);
    el.classList.toggle("text-white", active);
  });

  const cards = document.getElementById("cards");
  cards.innerHTML = "";
  section.cards.forEach((card) => {
    const article = document.createElement("article");
    article.className = "border border-slate-800 rounded-xl bg-slate-900/50 p-4 sm:p-5";
    article.innerHTML = `<h3 class=\"font-bold text-indigo-300\">${card.title}</h3><p class=\"text-sm text-slate-400 mt-2\">${card.body}</p>`;
    cards.appendChild(article);
  });
}

function wireClientRouting() {
  document.querySelectorAll(".dash-link").forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      window.history.pushState({}, "", link.getAttribute("href"));
      render();
      document.getElementById("mobile-nav").classList.add("hidden");
    });
  });

  window.addEventListener("popstate", render);
}

document.getElementById("nav-toggle").addEventListener("click", () => {
  document.getElementById("mobile-nav").classList.toggle("hidden");
});

wireClientRouting();
render();
