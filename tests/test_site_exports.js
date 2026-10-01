const assert = require("node:assert/strict");
const fs = require("node:fs");
const test = require("node:test");
const vm = require("node:vm");

const source = fs.readFileSync("site/app.js", "utf8");
const zipBlob = () =>
  new Blob([Uint8Array.from([0x50, 0x4b, 0x03, 0x04, 0x00])], {
    type: "application/zip",
  });

function loadApp(responses) {
  const fetchCalls = [];
  const links = [];
  const logs = [];
  const revokedUrls = [];
  const elements = new Map();
  let responseIndex = 0;

  const context = {
    console,
    Blob,
    Date,
    Uint8Array,
    setInterval: () => 0,
    setTimeout: (callback) => {
      callback();
      return 0;
    },
    fetch: async (path) => {
      fetchCalls.push(path);
      const response = responses[responseIndex++];
      assert.ok(response, `Unexpected fetch for ${path}`);
      return {
        ok: response.ok,
        status: response.status,
        blob: async () => response.blob,
      };
    },
    document: {
      addEventListener: () => {},
      getElementById: (id) => {
        if (!elements.has(id)) elements.set(id, {
          children: [],
          appendChild(child) { this.children.push(child); },
          scrollHeight: 0,
          scrollTop: 0,
        });
        return elements.get(id);
      },
      createTextNode: (text) => ({ text }),
      createElement: (tag) => {
        const element = {
          tag,
          clickCount: 0,
          children: [],
          appendChild(child) { this.children.push(child); },
          setAttribute(name, value) {
            this[name] = value;
          },
          addEventListener() {},
          click() {
            this.clickCount += 1;
          },
          remove() {},
        };
        if (tag === "a") links.push(element);
        return element;
      },
      body: { appendChild() {} },
    },
    window: {
      location: { protocol: "https:" },
      URL: {
        createObjectURL: () => "blob:test",
        revokeObjectURL: (url) => revokedUrls.push(url),
      },
      setTimeout: (callback) => {
        callback();
        return 0;
      },
    },
  };

  vm.createContext(context);
  vm.runInContext(source, context);
  context.logToConsole = (message, color) => logs.push({ message, color });

  return { context, fetchCalls, links, logs, revokedUrls, elements };
}

test("reference header reflects an unverified configured system", () => {
  const app = loadApp([]);
  app.context.renderSystemStatus({ system_status: "architecture_aligned_runtime_integrations_unverified" });
  assert.equal(app.elements.get("badge-status").textContent, "Needs verification");
  assert.match(app.elements.get("system-status-detail").textContent, /provider connections still need verification/);
  app.context.renderSystemStatus({ system_status: "blocked" });
  assert.equal(app.elements.get("badge-status").textContent, "Blocked");
});

test("digest uses the same configuration snapshot and does not invent live telemetry", () => {
  const app = loadApp([]);
  app.context.renderDigest({ dashboard_date: "2026-10-01", blockers: ["Authentication not verified"] });
  const digest = app.elements.get("digest-content");
  assert.equal(digest.children[0].textContent, "KOVA configuration snapshot — 2026-10-01");
  assert.match(digest.children[1].textContent, /live digest and current calendar reads have not been verified/);
  assert.equal(digest.children[2].children[0].textContent, "Authentication not verified");
});

test("downloads the API archive without requesting the fallback", async () => {
  const app = loadApp([{ ok: true, status: 200, blob: zipBlob() }]);

  const downloaded = await app.context.downloadExport(
    "/api/export/site",
    "../site_final.zip",
    "site_final.zip"
  );

  assert.equal(downloaded, true);
  assert.deepEqual(app.fetchCalls, ["/api/export/site"]);
  assert.equal(app.links.length, 1);
  assert.equal(app.links[0].clickCount, 1);
  assert.match(app.logs[0].message, /Successfully downloaded/);
  assert.deepEqual(app.revokedUrls, ["blob:test"]);
});

test("verifies and downloads the checked-in fallback after an API miss", async () => {
  const app = loadApp([
    { ok: false, status: 404 },
    { ok: true, status: 200, blob: zipBlob() },
  ]);

  const downloaded = await app.context.downloadExport(
    "/api/export/images",
    "../images.zip",
    "images.zip"
  );

  assert.equal(downloaded, true);
  assert.deepEqual(app.fetchCalls, ["/api/export/images", "../images.zip"]);
  assert.equal(app.links.length, 1);
  assert.equal(app.links[0].clickCount, 1);
  assert.match(app.logs[0].message, /checked-in/);
});

test("reports failure and does not click a link when both archives are missing", async () => {
  const app = loadApp([
    { ok: false, status: 404 },
    { ok: false, status: 404 },
  ]);

  const downloaded = await app.context.downloadExport(
    "/api/export/site",
    "../site_final.zip",
    "site_final.zip"
  );

  assert.equal(downloaded, false);
  assert.deepEqual(app.fetchCalls, ["/api/export/site", "../site_final.zip"]);
  assert.equal(app.links.length, 0);
  assert.match(app.logs[0].message, /Unable to download/);
  assert.equal(app.logs[0].color, "rose");
});

test("rejects a successful HTML response instead of reporting an archive", async () => {
  const app = loadApp([
    { ok: true, status: 200, blob: new Blob(["<html>not a zip</html>"]) },
    { ok: false, status: 404 },
  ]);

  const downloaded = await app.context.downloadExport(
    "/api/export/site",
    "../site_final.zip",
    "site_final.zip"
  );

  assert.equal(downloaded, false);
  assert.equal(app.links.length, 0);
  assert.match(app.logs[0].message, /Unable to download/);
});

test("uses an explicitly unverified direct link in local file mode", async () => {
  const app = loadApp([]);
  app.context.window.location.protocol = "file:";

  const requested = await app.context.downloadExport(
    "/api/export/site",
    "../site_final.zip",
    "site_final.zip"
  );

  assert.equal(requested, true);
  assert.deepEqual(app.fetchCalls, []);
  assert.equal(app.links.length, 1);
  assert.equal(app.links[0].href, "../site_final.zip");
  assert.equal(app.links[0].clickCount, 1);
  assert.match(app.logs[0].message, /cannot be verified in local file mode/);
});

test("export buttons describe retrieval rather than compilation", async () => {
  const app = loadApp([
    { ok: true, status: 200, blob: zipBlob() },
    { ok: true, status: 200, blob: zipBlob() },
  ]);

  await app.context.triggerLocalExport();
  await app.context.triggerImagesExport();

  assert.match(app.logs[0].message, /Preparing.*site package download/);
  assert.match(app.logs[2].message, /Preparing.*images package download/);
  assert.doesNotMatch(
    app.logs.map(({ message }) => message).join(" "),
    /compil/i
  );
});

test("maps new dashboard integration evidence states to non-blocked labels", () => {
  const app = loadApp([]);

  assert.equal(app.context.describeIntegrationStatus("partial").label, "Partial");
  assert.equal(app.context.describeIntegrationStatus("unverified").label, "Unverified");
  assert.equal(
    app.context.describeIntegrationStatus("implemented_not_production_verified").label,
    "Implemented"
  );
  assert.equal(
    app.context.describeIntegrationStatus("disabled_until_named_gap").label,
    "Optional"
  );
});

test("renders safe external integration source links", () => {
  const app = loadApp([]);
  app.context.renderDashboard({
    system_status: "architecture_aligned_runtime_integrations_unverified",
    top_priorities: [],
    blockers: [],
    next_actions: [],
    integrations: [
      {
        name: "KOVA Voice (Manus Export)",
        status: "unverified",
        evidence: "External surface",
        next_action: "Review",
        source_url: "https://kovavoice-2deymnxc.manus.space",
      },
    ],
  });

  assert.equal(app.links.length, 1);
  assert.equal(app.links[0].href, "https://kovavoice-2deymnxc.manus.space");
  assert.equal(app.links[0].target, "_blank");
  assert.equal(app.links[0].rel, "noopener noreferrer");
});

test("ignores unsafe integration source links", () => {
  const app = loadApp([]);
  app.context.renderDashboard({
    system_status: "architecture_aligned_runtime_integrations_unverified",
    top_priorities: [],
    blockers: [],
    next_actions: [],
    integrations: [
      {
        name: "Unsafe Source",
        status: "unverified",
        evidence: "Untrusted input",
        next_action: "Reject",
        source_url: "javascript:alert(1)",
      },
    ],
  });

  assert.equal(app.links.length, 0);
});
