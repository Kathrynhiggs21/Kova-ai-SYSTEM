// ─── Real KOVA OS data from workbook (July 4 2026) ────────────────────────────

const KOVA_CONNECTIONS = [
  { name: "Google Drive",      category: "Google",         status: "connected",      tools: "Full",    notes: "All 15 worlds structured. 70+ subfolders. Docs uploaded." },
  { name: "Gmail",             category: "Google",         status: "connected",      tools: "4",       notes: "Full email search, read, send, label management." },
  { name: "Google Calendar",   category: "Google",         status: "connected",      tools: "5",       notes: "Full calendar search, create, update, delete." },
  { name: "Notion",            category: "Productivity",   status: "connected",      tools: "12",      notes: "Master Dashboard + 15 world pages + skills registry live." },
  { name: "Slack",             category: "Productivity",   status: "connected",      tools: "12",      notes: "Real-time messaging, channel search, canvas creation." },
  { name: "Wix",               category: "Web",            status: "connected",      tools: "15",      notes: "11 sites managed: Scribbles, Hope4Anxiety, Fite Club, etc." },
  { name: "Outlook Mail",      category: "Microsoft",      status: "connected",      tools: "Full",    notes: "Search, read, send messages." },
  { name: "Outlook Calendar",  category: "Microsoft",      status: "connected",      tools: "Full",    notes: "Search, create, update, delete events." },
  { name: "HubSpot",           category: "CRM",            status: "connected",      tools: "Full",    notes: "Contacts, companies, deals, associations." },
  { name: "Supabase",          category: "Database",       status: "connected",      tools: "Full",    notes: "Database project management, SQL execution." },
  { name: "GitHub",            category: "Dev",            status: "connected-read", tools: "Full read", notes: "30 repos accessible. Write blocked — needs token upgrade." },
  { name: "Asana",             category: "Productivity",   status: "needs-reauth",   tools: "0",       notes: "OAuth timeout. Go to Manus Settings → Integrations → Reconnect." },
  { name: "tl;dv",             category: "Meetings",       status: "needs-reauth",   tools: "0",       notes: "OAuth timeout. Go to Manus Settings → Integrations → Reconnect." },
  { name: "Zapier",            category: "Automation",     status: "needs-config",   tools: "1",       notes: "Connected but needs actions at mcp.zapier.com/mcp/servers/..." },
  { name: "Make",              category: "Automation",     status: "needs-reauth",   tools: "0",       notes: "OAuth 404. Go to Manus Settings → Integrations → Reconnect." },
  { name: "Canva",             category: "Design",         status: "needs-reauth",   tools: "0",       notes: "Connection timeout. Go to Manus Settings → Integrations → Reconnect." },
  { name: "Neon",              category: "Database",       status: "needs-reauth",   tools: "0",       notes: "Connection timeout. Go to Manus Settings → Integrations → Reconnect." },
  { name: "Android S24 Ultra", category: "Device",         status: "skill-installed",tools: "N/A",     notes: "Install Automate app, create webhook flow, provide URL to Manus." },
  { name: "Dropbox",           category: "Storage",        status: "needs-new-key",  tools: "N/A",     notes: "API key invalid. Get new key from dropbox.com/developers." },
  { name: "Perplexity (Sonar)","category": "AI",           status: "api-key-set",    tools: "Full",    notes: "SONAR_API_KEY env var set. Use for real-time web research." },
  { name: "Google Gemini",     category: "AI",             status: "api-key-set",    tools: "Full",    notes: "GEMINI_API_KEY env var set. Gemini 2.5 Flash available." },
  { name: "Anthropic Claude",  category: "AI",             status: "api-key-set",    tools: "Full",    notes: "ANTHROPIC_API_KEY env var set. Claude 3.5 Sonnet available." },
  { name: "Cloudflare",        category: "Infrastructure", status: "api-token-set",  tools: "Full",    notes: "CLOUDFLARE_API_TOKEN env var set. Workers, DNS, R2 available." },
];

const KOVA_SKILLS = [
  { name: "katy-ai-assistant",          cat: "Kova Core",      trigger: "Any personal task",           cap: "Main Kova persona, profile, context" },
  { name: "kova-os-drive-organizer",    cat: "Kova Core",      trigger: "Organize my Drive",           cap: "Structures 15 worlds in Google Drive" },
  { name: "kova-web-capture",           cat: "Kova Core",      trigger: "Capture [URL] to [world]",    cap: "Saves web content to Drive world folder" },
  { name: "kova-android-connect",       cat: "Kova Core",      trigger: "Connect my phone",            cap: "Android SMS, contacts, files via Automate" },
  { name: "kova-skill-builder",         cat: "Kova Core",      trigger: "Create a skill",              cap: "Build new Kova OS skills" },
  { name: "kova-system-audit",          cat: "Kova Core",      trigger: "Audit Kova OS",               cap: "Full system health check and status report" },
  { name: "kova-voice-assistant-builder", cat: "Kova Core",    trigger: "Build voice assistant",       cap: "Full-stack AI voice assistant PWA with orb UI" },
  { name: "skill-creator",              cat: "Meta",           trigger: "Create/update a skill",       cap: "Builds new skills with SKILL.md structure" },
  { name: "manus-config",               cat: "Meta",           trigger: "Configure Manus",             cap: "Manage connectors, schedules, project files" },
  { name: "manus-api",                  cat: "Meta",           trigger: "Manus API task",              cap: "Create tasks, manage projects via Manus API" },
  { name: "scribbles-by-marcy-wix",     cat: "Scribbles",      trigger: "Update Scribbles site",       cap: "Manage Scribbles by Marcy Wix website" },
  { name: "scribbles-ai-content-gen",   cat: "Scribbles",      trigger: "Generate Scribbles content",  cap: "AI blog posts and social media for Scribbles" },
  { name: "scribbles-financial-scanner",cat: "Scribbles",      trigger: "Scan receipt/invoice",        cap: "Extract financial data from images/PDFs" },
  { name: "scribbles-marketing-mats",   cat: "Scribbles",      trigger: "Create marketing materials",  cap: "Design PDFs, business cards, printables" },
  { name: "scribbles-printables-gen",   cat: "Scribbles",      trigger: "Generate printables",         cap: "Coloring pages, activity sheets, bookmarks" },
  { name: "scribbles-drive-sync",       cat: "Scribbles",      trigger: "Sync Scribbles files",        cap: "Auto-sync files to Scribbles Google Drive" },
  { name: "scribbles-domain-email",     cat: "Scribbles",      trigger: "Setup domain/email",          cap: "Domain transfer, DNS, Google Workspace email" },
  { name: "scribbles-email-automations",cat: "Scribbles",      trigger: "Setup email automations",     cap: "Order confirmations, welcome sequences on Wix" },
  { name: "scribbles-financials",       cat: "Scribbles",      trigger: "Setup payments",              cap: "Wix Payments, Avalara tax, shipping setup" },
  { name: "scribbles-frontend-design",  cat: "Scribbles",      trigger: "Update site design",          cap: "CSS updates, Wix API integration patterns" },
  { name: "scribbles-social-media",     cat: "Scribbles",      trigger: "Post social media",           cap: "Facebook, Instagram, Google Business setup" },
  { name: "scribbles-wix-dashboard",    cat: "Scribbles",      trigger: "Manage Wix backend",          cap: "Wix admin, apps, subscriptions, MCP auth" },
  { name: "backlink-analysis",          cat: "SEO/Research",   trigger: "Audit backlinks for [domain]",cap: "Backlink profile audit with risk scoring" },
  { name: "comparison-article-writer",  cat: "Content",        trigger: "Write comparison article",    cap: "X vs Y blog articles with research" },
  { name: "content-gap-analysis",       cat: "SEO/Research",   trigger: "Content gap analysis",        cap: "Find missing topics vs competitors" },
  { name: "keyword-research",           cat: "SEO/Research",   trigger: "Research keyword for [topic]",cap: "3-tab Excel workbook with 300 keywords" },
  { name: "seo-audit",                  cat: "SEO/Research",   trigger: "SEO audit for [domain]",      cap: "Plain-language SEO audit report" },
  { name: "seo-competitor-analysis",    cat: "SEO/Research",   trigger: "Competitor analysis",         cap: "Organic competitor visibility report" },
  { name: "similarweb-analytics",       cat: "Analytics",      trigger: "Analyze traffic for [domain]",cap: "Traffic metrics, sources, rankings" },
  { name: "website-traffic-checker",    cat: "Analytics",      trigger: "Check traffic for [domain]",  cap: "Comprehensive traffic analysis" },
  { name: "stock-analysis",             cat: "Finance",        trigger: "Analyze stock [ticker]",      cap: "Stock profiles, charts, SEC filings" },
  { name: "imagegen",                   cat: "Creative",       trigger: "Generate/edit image",         cap: "Visual routing and AI image generation" },
  { name: "video-generator",            cat: "Creative",       trigger: "Create video",                cap: "AI video production workflow" },
  { name: "html-video-production",      cat: "Creative",       trigger: "Build HTML video",            cap: "Scene-based HTML videos rendered to MP4" },
  { name: "manim-animator",             cat: "Creative",       trigger: "Create math animation",       cap: "Manim engine for math/algorithm animations" },
  { name: "music-prompter",             cat: "Creative",       trigger: "Generate music",              cap: "Music prompt crafting for AI generation" },
  { name: "tts-prompter",               cat: "Creative",       trigger: "Generate speech",             cap: "Text-to-speech prompt crafting" },
  { name: "excel-generator",            cat: "Data",           trigger: "Create spreadsheet",          cap: "Professional Excel with aesthetics" },
  { name: "automation-and-scheduling",  cat: "Dev",            trigger: "Automate [task]",             cap: "Recurring execution, background jobs" },
  { name: "persistent-computing",       cat: "Dev",            trigger: "Deploy persistent service",   cap: "Docker, VMs, background processes" },
  { name: "github-gem-seeker",          cat: "Dev",            trigger: "Find GitHub solution for [problem]", cap: "Search GitHub for battle-tested solutions" },
  { name: "api-explorer-and-brief",     cat: "Dev",            trigger: "Explore [API]",               cap: "Research APIs, build demos, write briefs" },
  { name: "builtin-llm-models",         cat: "Dev",            trigger: "Use LLM in code",             cap: "Reference for built-in LLM catalog" },
  { name: "gws-best-practices",         cat: "Dev",            trigger: "Use gws CLI",                 cap: "Best practices for Google Workspace CLI" },
  { name: "billing-dispute-case-builder",cat: "Legal/Finance", trigger: "Build dispute case",          cap: "Professional billing dispute case files" },
  { name: "budgie-mutation-identifier", cat: "Personal",       trigger: "Identify budgie mutation",    cap: "Identifies budgerigar color mutations from image" },
  { name: "merch-product-pipeline",     cat: "Business",       trigger: "Research merch product",      cap: "End-to-end merchandise product development" },
  { name: "canva-mcp",                  cat: "Design",         trigger: "Create Canva design",         cap: "Canva MCP integration guide" },
  { name: "internet-skill-finder",      cat: "Meta",           trigger: "Find skill for [task]",       cap: "Search GitHub for agent skills" },
  { name: "reagan-bird-behavior",       cat: "Personal",       trigger: "Update Reagan's bird behavior",cap: "Reagan's bird companion behaviors" },
  { name: "persistent-computing",       cat: "Dev",            trigger: "Deploy always-on service",    cap: "Persistent VM and Docker deployments" },
];

// Status badge helper
function statusBadge(status) {
  const map = {
    "connected":       { label: "Connected",       cls: "bg-emerald-950/60 text-emerald-400 border-emerald-800/40" },
    "connected-read":  { label: "Connected (read)", cls: "bg-sky-950/60 text-sky-400 border-sky-800/40" },
    "needs-reauth":    { label: "Needs Re-Auth",    cls: "bg-amber-950/60 text-amber-400 border-amber-800/40" },
    "needs-config":    { label: "Needs Config",     cls: "bg-orange-950/60 text-orange-400 border-orange-800/40" },
    "needs-new-key":   { label: "Needs New Key",    cls: "bg-rose-950/60 text-rose-400 border-rose-800/40" },
    "skill-installed": { label: "Skill Installed",  cls: "bg-violet-950/60 text-violet-400 border-violet-800/40" },
    "api-key-set":     { label: "API Key Set",      cls: "bg-sky-950/60 text-sky-300 border-sky-800/40" },
    "api-token-set":   { label: "API Token Set",    cls: "bg-indigo-950/60 text-indigo-300 border-indigo-800/40" },
  };
  const s = map[status] || { label: status, cls: "bg-slate-800 text-slate-400 border-slate-700" };
  return `<span class="inline-block text-xs font-semibold px-2 py-0.5 rounded-full border ${s.cls}">${s.label}</span>`;
}

// Category colour dot
function catDot(cat) {
  const colours = {
    "Google": "#34d399", "Productivity": "#818cf8", "Microsoft": "#60a5fa",
    "Web": "#f472b6", "CRM": "#fb923c", "Database": "#a78bfa",
    "Dev": "#38bdf8", "Meetings": "#facc15", "Automation": "#f97316",
    "Design": "#e879f9", "Storage": "#94a3b8", "AI": "#c084fc",
    "Infrastructure": "#64748b", "Device": "#22c55e",
    "Kova Core": "#c084fc", "Meta": "#818cf8", "Scribbles": "#f472b6",
    "SEO/Research": "#38bdf8", "Content": "#34d399", "Analytics": "#60a5fa",
    "Finance": "#facc15", "Creative": "#e879f9", "Data": "#fb923c",
    "Legal/Finance": "#f97316", "Personal": "#a78bfa", "Business": "#f472b6",
    "default": "#64748b",
  };
  const c = colours[cat] || colours.default;
  return `<span class="inline-block w-2 h-2 rounded-full mr-1.5 flex-shrink-0" style="background:${c}"></span>`;
}

// ─── Dashboard sections ───────────────────────────────────────────────────────
const dashboardSections = {
  overview: {
    title: "Overview",
    subtitle: "KOVA OS command center — Katy Higgs · Cincinnati, OH",
    renderCustom(container) {
      const connected = KOVA_CONNECTIONS.filter(s => s.status === "connected" || s.status === "connected-read" || s.status === "api-key-set" || s.status === "api-token-set").length;
      const needsAttn = KOVA_CONNECTIONS.filter(s => ["needs-reauth","needs-config","needs-new-key"].includes(s.status)).length;
      const stats = [
        { label: "Connected Services", value: `${connected} / ${KOVA_CONNECTIONS.length}`, color: "text-emerald-400" },
        { label: "Needs Attention",    value: needsAttn, color: "text-amber-400" },
        { label: "Installed Skills",   value: KOVA_SKILLS.length, color: "text-violet-400" },
        { label: "Kova Worlds",        value: "15", color: "text-sky-400" },
        { label: "GitHub Repos",       value: "30", color: "text-indigo-300" },
        { label: "Wix Sites",          value: "11", color: "text-pink-400" },
        { label: "Active Projects",    value: "8",  color: "text-orange-400" },
        { label: "Automations Ready",  value: "12", color: "text-teal-400" },
      ];
      container.className = "grid grid-cols-2 sm:grid-cols-4 gap-4";
      stats.forEach(s => {
        const el = document.createElement("div");
        el.className = "rounded-2xl p-4 text-center" + " border border-white/5" + " bg-black/30 backdrop-blur";
        el.innerHTML = `<div class="text-2xl font-black ${s.color}">${s.value}</div><div class="text-xs text-slate-500 mt-1 uppercase tracking-wider">${s.label}</div>`;
        container.appendChild(el);
      });

      // Quick links
      const links = document.createElement("div");
      links.className = "col-span-full mt-4 rounded-2xl border border-white/5 bg-black/30 p-5";
      links.innerHTML = `
        <p class="text-xs uppercase tracking-[0.2em] text-violet-400 mb-4">Quick Links</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-sm">
          <a href="https://www.notion.so" target="_blank" class="flex items-center gap-2 text-sky-400 hover:text-sky-300 transition-colors">⚡ Notion Master Dashboard</a>
          <a href="https://github.com/Kathrynhiggs21" target="_blank" class="flex items-center gap-2 text-sky-400 hover:text-sky-300 transition-colors">💻 GitHub Profile</a>
          <a href="/dashboard/integrations" class="flex items-center gap-2 text-sky-400 hover:text-sky-300 transition-colors">🔗 All Integrations</a>
          <a href="/skills" class="flex items-center gap-2 text-sky-400 hover:text-sky-300 transition-colors">🧰 Skills Registry (${KOVA_SKILLS.length})</a>
          <a href="/ask" class="flex items-center gap-2 text-sky-400 hover:text-sky-300 transition-colors">🎤 Ask KOVA</a>
          <a href="/brain" class="flex items-center gap-2 text-sky-400 hover:text-sky-300 transition-colors">🧠 My Brain</a>
        </div>`;
      container.appendChild(links);
    }
  },

  integrations: {
    title: "Integrations",
    subtitle: "All 23 KOVA OS connected services — status as of July 4 2026",
    renderCustom(container) {
      container.className = "w-full";
      // Group attention-needed first
      const sorted = [...KOVA_CONNECTIONS].sort((a,b) => {
        const order = { "needs-reauth":0,"needs-config":1,"needs-new-key":2,"skill-installed":3,"connected-read":4,"api-key-set":5,"api-token-set":6,"connected":7 };
        return (order[a.status]??9) - (order[b.status]??9);
      });

      const wrapper = document.createElement("div");
      wrapper.className = "rounded-2xl border border-white/5 bg-black/30 overflow-hidden";
      wrapper.innerHTML = `
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-white/5 text-xs uppercase tracking-wider text-slate-500">
                <th class="text-left px-4 py-3">Service</th>
                <th class="text-left px-4 py-3">Category</th>
                <th class="text-left px-4 py-3">Status</th>
                <th class="text-left px-4 py-3">Tools</th>
                <th class="text-left px-4 py-3 hidden lg:table-cell">Notes / Action</th>
              </tr>
            </thead>
            <tbody id="conn-tbody">
            </tbody>
          </table>
        </div>`;
      container.appendChild(wrapper);

      const tbody = wrapper.querySelector("#conn-tbody");
      sorted.forEach(s => {
        const tr = document.createElement("tr");
        tr.className = "border-b border-white/5 hover:bg-white/[0.03] transition-colors";
        tr.innerHTML = `
          <td class="px-4 py-3 font-medium text-slate-200 whitespace-nowrap">${s.name}</td>
          <td class="px-4 py-3 whitespace-nowrap"><span class="flex items-center text-slate-400">${catDot(s.category)}${s.category}</span></td>
          <td class="px-4 py-3 whitespace-nowrap">${statusBadge(s.status)}</td>
          <td class="px-4 py-3 text-slate-400 whitespace-nowrap">${s.tools}</td>
          <td class="px-4 py-3 text-slate-500 text-xs hidden lg:table-cell max-w-xs">${s.notes}</td>`;
        tbody.appendChild(tr);
      });

      // Summary bar
      const connected = KOVA_CONNECTIONS.filter(s => ["connected","connected-read","api-key-set","api-token-set","skill-installed"].includes(s.status)).length;
      const attn = KOVA_CONNECTIONS.filter(s => ["needs-reauth","needs-config","needs-new-key"].includes(s.status)).length;
      const summary = document.createElement("div");
      summary.className = "mt-4 flex flex-wrap gap-4 text-sm text-slate-400";
      summary.innerHTML = `<span class="text-emerald-400 font-semibold">${connected} operational</span> · <span class="text-amber-400 font-semibold">${attn} need attention</span> · <span>${KOVA_CONNECTIONS.length} total services</span>`;
      container.appendChild(summary);
    }
  },

  devices: {
    title: "Smart Devices",
    subtitle: "Connected hardware and devices in the KOVA ecosystem.",
    cards: [
      { title: "Android S24 Ultra",   body: "Status: Skill Installed. Next: Install Automate app, create webhook flow, provide URL to Manus.", color: "text-violet-400" },
      { title: "Mac / Desktop",       body: "Primary dev machine. GitHub, Supabase, and API tools accessible via CLI and MCP.", color: "text-emerald-400" },
      { title: "Cloudflare Workers",  body: "API Token set. Workers, DNS, R2 storage available. CLOUDFLARE_API_TOKEN configured.", color: "text-sky-400" },
      { title: "Dropbox Storage",     body: "Needs New Key. Current API key invalid. Get new key from dropbox.com/developers.", color: "text-amber-400" },
      { title: "Wix Sites",           body: "11 sites managed: Scribbles, Hope4Anxiety, Fite Club + 8 more. Full MCP access.", color: "text-pink-400" },
      { title: "Neon Database",       body: "Needs Re-Auth. Connection timeout. Reconnect via Manus Settings → Integrations.", color: "text-amber-400" },
    ]
  },

  automation: {
    title: "Automation",
    subtitle: "KOVA OS active automations and skill-based workflows.",
    cards: [
      { title: "12 Automations Ready",     body: "Zapier + Make automations. Zapier needs action config at mcp.zapier.com/mcp/servers/. Make needs OAuth reconnect.", color: "text-emerald-400" },
      { title: "Email Automation",         body: "Scribbles: Order confirmations, welcome sequences on Wix. Domain email via Cloudflare DNS + Google Workspace.", color: "text-sky-400" },
      { title: "Drive Sync",               body: "kova-os-drive-organizer + scribbles-drive-sync: Auto-structure 15 worlds + Scribbles files in Google Drive.", color: "text-violet-400" },
      { title: "AI Content Pipeline",      body: "scribbles-ai-content-generator: Blog posts + social via Gemini + Drive. imagegen + video-generator for creative output.", color: "text-pink-400" },
      { title: "Webhook Routing",          body: "GitHub webhook active at /webhooks/github. Android S24 Ultra webhook flow via Automate app pending.", color: "text-amber-400" },
      { title: "Background Jobs",          body: "persistent-computing + automation-and-scheduling skills deployed. Docker, VMs, recurring execution ready.", color: "text-indigo-300" },
    ]
  }
};

// ─── Card renderer (fallback for non-custom sections) ─────────────────────────
function renderCards(section) {
  const container = document.getElementById("cards");
  container.innerHTML = "";

  if (section.renderCustom) {
    section.renderCustom(container);
    return;
  }

  container.className = "grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-5";
  section.cards.forEach((card) => {
    const article = document.createElement("article");
    article.className = "rounded-2xl border border-white/5 bg-black/30 p-5 backdrop-blur";
    const heading = document.createElement("h3");
    heading.className = "font-bold mb-2 " + (card.color || "text-violet-300");
    heading.textContent = card.title;
    const body = document.createElement("p");
    body.className = "text-sm text-slate-400 leading-relaxed";
    body.textContent = card.body;
    article.appendChild(heading);
    article.appendChild(body);
    container.appendChild(article);
  });
}

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
    el.classList.toggle("active", active);
  });

  renderCards(section);
}

function wireClientRouting() {
  document.querySelectorAll(".dash-link").forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      window.history.pushState({}, "", link.getAttribute("href"));
      render();
      const mob = document.getElementById("mobile-nav");
      if (mob) { mob.classList.add("hidden"); mob.classList.remove("grid"); }
    });
  });
  window.addEventListener("popstate", render);
}

wireClientRouting();
render();

