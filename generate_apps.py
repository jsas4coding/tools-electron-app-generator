#!/usr/bin/env python3
"""Generate Electron-based AppImage launchers from JSON definition."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# =========================
# 📦 Global Configuration
# =========================
BASE_DIR = Path(__file__).parent.resolve()
APPS_DIR = BASE_DIR
ICONS_DIR = APPS_DIR / "icons"
JSON_FILE = APPS_DIR / "apps.json"
BUILD_DIR = APPS_DIR / "build"
OPT_DIR = APPS_DIR / "opt"
DESKTOP_ENTRIES_DIR = APPS_DIR / "desktop-entries"
USERDATA_ENV = os.environ.get("APP_USERDATA")

# Build Settings (from environment)
BUILD_TARGET = "AppImage"
REQUIRED_NODE_MAJOR_VERSION = int(os.environ.get("REQUIRED_NODE_MAJOR_VERSION", "22"))
ELECTRON_VERSION = os.environ.get("REQUIRED_ELECTRON_VERSION", "36.0.0")

# Localization Settings
LOCALE_LANG = os.environ.get("APP_LANG", "pt-BR")
LOCALE_ENV = f"{LOCALE_LANG}.UTF-8"
SPELLCHECK_LANGS = os.environ.get("APP_SPELLCHECK_LANGS", "en-US,pt-BR").split(",")

# =========================
# 🛠️ Environment Checks
# =========================
if os.geteuid() == 0:
    print("🛑 Do not run this script as root.")
    sys.exit(1)

if not (sys.version_info.major == 3 and sys.version_info.minor >= 8):
    print(f"🛑 Python 3.8+ required, found {sys.version}")
    sys.exit(1)

def check_node_version():
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        if version.startswith('v'):
            version = version[1:]
        major = int(version.split('.')[0])
        if major < REQUIRED_NODE_MAJOR_VERSION:
            print(f"🛑 Node.js v{REQUIRED_NODE_MAJOR_VERSION}+ required, found v{version}")
            sys.exit(1)
    except Exception:
        print("🛑 Node.js is not installed or not found in PATH.")
        sys.exit(1)

check_node_version()

# =========================
# 🛠️ Utility Functions
# =========================

def run_command(cmd, cwd=None):
    subprocess.run(cmd, check=True, cwd=cwd)

def create_package_json(build_dir, app_name):
    package_json = {
        "name": app_name,
        "version": "1.0.0",
        "main": "main.js",
        "scripts": {"start": "electron ."},
        "devDependencies": {"electron": ELECTRON_VERSION}
    }
    (build_dir / "package.json").write_text(json.dumps(package_json, indent=2))

def create_main_js(build_dir, app_name, product_name, url):
    spellcheck_langs_formatted = ', '.join([f'\'{lang}\'' for lang in SPELLCHECK_LANGS])

    set_userdata = """
const userDataPath = process.env.APP_USERDATA;
if (userDataPath) {
  app.setPath('userData', userDataPath);
  app.setPath('logs', require('path').join(userDataPath, 'logs'));
  app.setPath('crashDumps', require('path').join(userDataPath, 'crashDumps'));
}"""

    main_js = f"""const {{ app, BrowserWindow, session, Menu }} = require('electron');
const path = require('path');
{set_userdata}

function createWindow() {{
  const chromeVersion = process.versions.chrome;
  const userAgent = `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/${{chromeVersion}} Safari/537.36`;

  const win = new BrowserWindow({{
    width: 1200,
    height: 800,
    fullscreenable: true,
    title: '{product_name}',
    icon: path.join(__dirname, 'icon.png'),
    backgroundColor: '#ffffff',
    autoHideMenuBar: true,
    webPreferences: {{
      spellcheck: true,
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      webSecurity: true,
      enableRemoteModule: false,
    }},
  }});

  session.defaultSession.setSpellCheckerLanguages([{spellcheck_langs_formatted}]);
  win.webContents.setUserAgent(userAgent);
  win.loadURL('{url}');
  win.on('page-title-updated', (e) => e.preventDefault());

  win.webContents.on('before-input-event', (event, input) => {{
    if (input.type === 'keyDown') {{
      const key = input.key.toLowerCase();
      if (key === 'f11') {{
        win.setFullScreen(!win.isFullScreen());
        event.preventDefault();
      }}
      if ((input.control || input.meta) && (key === 'w' || key === 'f4')) {{
        win.destroy();
        app.quit();
        process.exit(0);
        event.preventDefault();
      }}
      if ((input.control || input.meta) && key === 'r') {{
        win.reload();
        event.preventDefault();
      }}
      if (key === 'f5') {{
        win.reload();
        event.preventDefault();
      }}
    }}
  }});

  win.webContents.on('context-menu', (e, params) => {{
    const menu = Menu.buildFromTemplate([
      {{ role: 'reload' }},
      {{ role: 'copy' }},
      {{ role: 'paste' }},
      {{ role: 'selectAll' }},
    ]);
    menu.popup();
  }});

  win.webContents.setWindowOpenHandler(({{ url }}) => {{
    win.loadURL(url);
    console.log(`🔗 Opening inside app: ${{url}}`);
    return {{ action: 'deny' }};
  }});

  win.removeMenu();
}}

app.commandLine.appendSwitch('lang', '{LOCALE_LANG}');
process.env.LANG = '{LOCALE_ENV}';
process.env.LC_ALL = '{LOCALE_ENV}';

app.whenReady().then(() => {{
  createWindow();
  app.on('activate', () => {{
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  }});
}});

app.on('window-all-closed', () => {{
  if (process.platform !== 'darwin') {{
    app.quit();
    process.exit(0);
  }}
}});
"""
    (build_dir / "main.js").write_text(main_js)

def create_desktop_entry(app_name, product_name, category, description):
    env_part = f"env APP_USERDATA={USERDATA_ENV} " if USERDATA_ENV else ""
    entry = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={product_name}
Comment={description}
Exec={env_part}{OPT_DIR}/{app_name}/{app_name}.AppImage --no-sandbox
Icon={OPT_DIR}/{app_name}/icon.png
Terminal=false
Categories={category};
StartupWMClass={app_name}
"""
    desktop_path = DESKTOP_ENTRIES_DIR / f"{app_name}.desktop"
    desktop_path.write_text(entry)
    desktop_path.chmod(0o644)


# =========================
# 🚀 Main Execution
# =========================

DESKTOP_ENTRIES_DIR.mkdir(parents=True, exist_ok=True)
OPT_DIR.mkdir(parents=True, exist_ok=True)
BUILD_DIR.mkdir(parents=True, exist_ok=True)
if USERDATA_ENV:
    Path(USERDATA_ENV).mkdir(parents=True, exist_ok=True)

with JSON_FILE.open() as f:
    apps = json.load(f)

for app_cfg in apps:
    if app_cfg.get("skip"):
        print(f"⏩ Skipping {app_cfg['name']}")
        continue

    app_name = app_cfg["app_name"]
    product_name = app_cfg["name"]
    url = app_cfg["url"]
    icon_name = app_cfg["icon"]
    category = app_cfg["category"]
    description = app_cfg.get("description", f"Launch {product_name}")

    print(f"🚀 Building {product_name}...")

    build_dir = BUILD_DIR / app_name
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)

    create_package_json(build_dir, app_name)
    create_main_js(build_dir, app_name, product_name, url)

    src_icon = ICONS_DIR / f"{icon_name}.png"
    dst_icon = build_dir / "icon.png"
    if src_icon.exists():
        shutil.copy(src_icon, dst_icon)
        os.chmod(dst_icon, 0o644)
    else:
        print(f"⚠️ Icon not found for {product_name}: {src_icon}")

    run_command(["npx", "electron-builder", "--linux", BUILD_TARGET], cwd=build_dir)

    dist_dir = build_dir / "dist"
    appimage_files = list(dist_dir.glob("*.AppImage"))
    if not appimage_files:
        print(f"❌ AppImage not created for {product_name}")
        continue

    appimage_file = appimage_files[0]

    opt_app_dir = OPT_DIR / app_name
    if opt_app_dir.exists():
        shutil.rmtree(opt_app_dir)
    opt_app_dir.mkdir(parents=True)

    shutil.copy(appimage_file, opt_app_dir / f"{app_name}.AppImage")
    shutil.copy(dst_icon, opt_app_dir / "icon.png")
    os.chmod(opt_app_dir / f"{app_name}.AppImage", 0o755)

    create_desktop_entry(app_name, product_name, category, description)

    print(f"🧹 Cleaning up {product_name}...")
    shutil.rmtree(build_dir)

    print(f"✅ {product_name} ready at {opt_app_dir}")

print("🏋️ All apps processed successfully.")
