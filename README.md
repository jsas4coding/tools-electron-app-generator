# Web AppImage Generator with Electron

## 1. Introduction

**Web AppImage Generator** allows you to transform websites into standalone Linux desktop applications, packaged as isolated AppImages using Electron.

Applications run in independent windows, preserve user sessions (via `user-data`), and behave like native apps (ChatGPT, YouTube, Gmail, etc.) — without tab overload.

This toolchain supports both `make` and a fallback `build.sh` script, ensuring that even environments without Make can easily build everything.

> **Note:** Tested exclusively on **Linux** distributions.

## 1.1 Scope and Disclaimer

> **Important Notice**  
> This project is an **example based on personal needs** and **should not** be considered a production-grade solution.  
> It is provided **as-is**, without warranties, and has **no formal testing** for broader use cases.

The main purpose is similar to a **well-organized Gist**:

- To share ideas and workflows that may help others.
- To serve as a starting point for personal adaptations.

**If you choose to use it for production, you do so at your own risk.**  
Contributions and improvements are welcome, but no production support is guaranteed.

---

## 2. What This Project Solves

- Converts websites into full desktop applications.
- Enables isolated browsing environments.
- Preserves user data per app.
- Removes dependency on browser tabs.
- Supports reproducible builds.

---

## 3. Important Notes

- **Ensure executable permissions**:
  ```bash
  chmod +x generate_apps.py build.sh
  ```
- Designed and tested on **Linux** only.
- Node.js v22+ and Python 3.8+ required.

---

## 4. Setup Instructions

### 4.1 Requirements

- Linux-based OS (Debian/Ubuntu/Arch/etc.)
- Python >= 3.8
- Node.js >= 22
- npm
- (Optional) make

### 4.2 Installing Node.js

#### Using nvm (recommended)

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.nvm/nvm.sh
nvm install 22
nvm use 22
```

#### Without nvm (manual install)

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
```

### 4.3 Installing Python + venv

```bash
sudo apt install python3 python3-venv python3-pip
python3 -m venv .venv
source .venv/bin/activate
```

### 4.4 Installing make (optional)

```bash
sudo apt install make
```

---

## 5. Project Structure

```
apps/
├── icons/                   # PNG icons for apps
├── build/                   # Temporary working directory
├── opt/                     # Final AppImage install location
├── desktop-entries/         # Generated .desktop files
├── user-data/$USER/          # Shared userData per user
├── apps.json                # Configuration file
├── generate_apps.py         # Python build script
├── build.sh                 # Alternative build script
├── Makefile                 # Primary automation (if make installed)
```

---

## 6. Usage: Building Applications

### Option 1: Using Makefile (recommended)

```bash
make setup         # Install Electron + Electron Builder
make prepare       # Create necessary directories
make build         # Generate AppImages
make install-desktop  # Install .desktop shortcuts
```

### Option 2: Using build.sh (for minimal environments)

```bash
bash build.sh
```

This will:

- Install dependencies
- Build apps
- Install desktop entries

### What Happens

- AppImages are created under `opt/{app}`.
- `.desktop` launchers are generated.
- Apps will appear in your system launcher (Gnome/KDE/XFCE).

---

## 7. apps.json Format

Example:

```json
[
  {
    "name": "Telegram",
    "url": "http://web.telegram.org",
    "icon": "telegram",
    "app_name": "telegram",
    "category": "Network;InstantMessaging",
    "description": "Chat via Telegram Web",
    "skip": true
  },
  {
    "name": "WhatsApp",
    "url": "https://web.whatsapp.com",
    "icon": "whatsapp",
    "app_name": "whatsapp",
    "category": "Network;InstantMessaging",
    "description": "Send and receive messages with WhatsApp Web",
    "skip": false
  },
  {
    "name": "RegEx101",
    "url": "https://regex101.com",
    "icon": "regex101",
    "app_name": "regex101",
    "category": "Development;Utility",
    "description": "Test and debug regular expressions",
    "skip": false
  }
]
```

| Field         | Description                     |
| :------------ | :------------------------------ |
| `name`        | Display name                    |
| `url`         | Entry URL                       |
| `icon`        | Icon filename (inside `icons/`) |
| `app_name`    | AppImage executable name        |
| `category`    | Linux app category              |
| `description` | Tooltip / metadata description  |
| `skip`        | Skip generation if true         |

---

## 8. Customization

### Environment Variables

| Variable                            | Description                     | Default               |
| :---------------------------------- | :------------------------------ | :-------------------- |
| `APP_LANG`                          | Locale language for app         | `pt-BR`               |
| `APP_SPELLCHECK_LANGS`              | Spellchecker languages          | `en-US,pt-BR`         |
| `APP_USERDATA`                      | Path to shared user-data folder | `./user-data/$(USER)` |
| `REQUIRED_NODE_MAJOR_VERSION`       | Node.js required major version  | `22`                  |
| `REQUIRED_ELECTRON_VERSION`         | Electron version                | `36.0.0`              |
| `REQUIRED_ELECTRON_BUILDER_VERSION` | Electron Builder version        | `26.0.12`             |

Example overriding at build:

```bash
APP_SPELLCHECK_LANGS=en-US,es-ES make build
```

or

```bash
APP_SPELLCHECK_LANGS=en-US,es-ES bash build.sh
```

---

## 9. Cleaning Up

```bash
make clean
# or manually
rm -rf build opt desktop-entries
```

Full wipe (including user data):

```bash
make purge
# or manually
rm -rf build opt desktop-entries user-data
```

---

## 10. Troubleshooting

### AppImage permission errors

```bash
chmod +x opt/chatgpt/chatgpt.AppImage
```

### Icon missing in launcher

```bash
gtk-update-icon-cache ~/.local/share/icons/hicolor
```

### Cache/quota errors from Electron

Ensure your `user-data` is writable.

### App won't close on Ctrl+W

Apps are configured to close properly — report issues if persists.

---

## 11. Final Notes

- Project focused on **Linux** only.
- WSL, Windows, macOS are **not supported**.
- Full session persistence between launches.
- Full keyboard shortcuts support (F11 fullscreen, Ctrl+W close).

---

## 12. Credits

Made for developers who want clean workflows without browser tabs.  
Built 100% with open-source technology.

MIT License — Contributions welcome!
