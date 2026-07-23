# Running KOVA OS Outside of Manus

This guide provides a comprehensive manual and operational reference for running **KOVA OS** completely outside of the Manus agent environment, enabling local deployment, direct MCP (Model Context Protocol) file access, API integrations, and direct uploads/syncing to **Google Drive**.

---

## 📋 Architecture Overview

When running outside of Manus, the KOVA OS system operates as a self-contained personal command center:

```
Kova-ai-SYSTEM/
├── site/                     # Premium Static Dashboard v1 Website
│   ├── index.html            # Main User Interface
│   ├── app.js                # Core JS logic & fallbacks
│   └── images/               # Compiled SVG Icons (for kovoas.com)
├── kova-ai/                  # FastAPI Backend API Server (Dockerized)
│   └── app/api/
│       └── export_endpoints.py # Download & Google Drive Export API
├── site_final.zip            # Packaged Website Distribution
└── images.zip                # Compiled Images Archive
```

---

## 🛠️ Step 1: Local Installation & Bootstrap

To launch the backend API and visual dashboard locally:

```bash
# 1. Run the setup script to build and launch Docker services
chmod +x setup_kova_system.sh
./setup_kova_system.sh

# 2. Verify everything is running correctly
docker compose ps
curl http://localhost:8000/health
```

---

## 📊 Step 2: Accessing Dashboard v1

The command center dashboard can be opened in two ways:

### Option A: Direct Local Access (Zero Dependencies)
You do not need to run a server to view your dashboard! 
1. Open a browser and navigate to the file path:
   - On Linux/macOS: `file:///path/to/your/Kova-ai-SYSTEM/site/index.html`
   - On Windows: `file:///C:/path/to/your/Kova-ai-SYSTEM/site/index.html` (or open `site\index.html` in your file explorer).
2. The dashboard runs as a premium Single Page App (SPA) with a built-in high-fidelity fallback database to bypass CORS and load all system state instantly.

### Option B: Hosting on `kovoas.com`
To deploy the dashboard publicly:
1. Unzip `site_final.zip` into your static hosting provider root (e.g., Netlify, Vercel, GitHub Pages, or any standard web server).
2. Point your domain `kovoas.com` or `kovaos.com` to the hosting provider.
3. Access your secure, beautiful command center from any device!

---

## 📦 Step 3: Compiling & Downloading ZIP Archives

You can package and download the completed website and image assets using multiple integrations:

### 1. Model Context Protocol (MCP) / CLI Download
If you are interacting with KOVA via an AI assistant or terminal, you can package the latest files directly inside the workspace:

```bash
# Compile latest changes into zip archives
python3 scripts/export_kova_os.py
```
This generates:
- `site_final.zip` (Complete site, code, stylesheets, and images)
- `images.zip` (Standalone directory of clean, scalable SVG icons)

These files are immediately ready for copy/download from your workspace.

### 2. Live API Endpoints
If the FastAPI server is running, you can use these custom REST endpoints to download the compiled packages dynamically:

- **Get Compilation Status**: `GET http://localhost:8000/api/export/status`
- **Download Full Site ZIP**: `GET http://localhost:8000/api/export/site`
- **Download Standalone Images**: `GET http://localhost:8000/api/export/images`

---

## ☁️ Step 4: Google Drive Sync Integration

To enable direct exports of your final packages to Google Drive:

1. Obtain your `credentials.json` from the Google Cloud Console (enabled for Google Drive API).
2. Save `credentials.json` in the root of the repository.
3. Run the export script with the upload environment variable set to `true`:

```bash
export UPLOAD_TO_GDRIVE=true
python3 scripts/export_kova_os.py
```

Or trigger it programmatically using the API:
```bash
curl -X POST http://localhost:8000/api/export/gdrive-upload
```

The script will automatically authenticate with Google, package the latest site and images, upload them directly to your Google Drive, and return the web view links!

---

## 🤝 Need Help?

- Check out **[KOVA_DASHBOARD_V1_SPEC.md](KOVA_DASHBOARD_V1_SPEC.md)** for layout design goals.
- Check out **[KOVA_OS_INTEGRATION_MATRIX.md](KOVA_OS_INTEGRATION_MATRIX.md)** for connection statuses.
- Use the **Kova Neural Console** on the dashboard to test command simulations!
