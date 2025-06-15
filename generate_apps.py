import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from string import Template

BASE_DIR = Path(__file__).parent.resolve()
APPS_DIR = BASE_DIR
ICONS_DIR = APPS_DIR / "icons"
JSON_FILE = APPS_DIR / "apps.json"
BUILD_DIR = APPS_DIR / "build"
OPT_DIR = APPS_DIR / "opt"
DESKTOP_ENTRIES_DIR = APPS_DIR / "desktop-entries"
TEMPLATES_DIR = BASE_DIR / "templates"

BUILD_TARGET = "AppImage"
REQUIRED_NODE_MAJOR_VERSION = int(os.environ.get("REQUIRED_NODE_MAJOR_VERSION", "22"))
ELECTRON_VERSION = os.environ.get("REQUIRED_ELECTRON_VERSION", "36.0.0")

LOCALE_LANG = os.environ.get("APP_LANG", "pt-BR")
LOCALE_ENV = f"{LOCALE_LANG}.UTF-8"
SPELLCHECK_LANGS = os.environ.get("APP_SPELLCHECK_LANGS", "en-US,pt-BR").split(",")

if os.geteuid() == 0:
    print("🔝 Do not run this script as root.")
    sys.exit(1)

if not (sys.version_info.major == 3 and sys.version_info.minor >= 8):
    print(f"🔝 Python 3.8+ required, found {sys.version}")
    sys.exit(1)


def check_node_version():
    try:
        result = subprocess.run(
            ["node", "--version"], capture_output=True, text=True, check=True
        )
        version = result.stdout.strip().lstrip("v")
        major = int(version.split(".")[0])
        if major < REQUIRED_NODE_MAJOR_VERSION:
            print(
                f"🔝 Node.js v{REQUIRED_NODE_MAJOR_VERSION}+ required, found v{version}"
            )
            sys.exit(1)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("🔝 Node.js is not installed or not found in PATH.")
        sys.exit(1)


check_node_version()


def run_command(cmd, cwd=None):
    subprocess.run(cmd, check=True, cwd=cwd)


def render_template(template_file, context):
    template_path = TEMPLATES_DIR / template_file
    template_content = template_path.read_text()
    return Template(template_content).substitute(context)


def create_package_json(build_path, app_name):
    context = {"app_name": app_name, "electron_version": ELECTRON_VERSION}
    result = render_template("package_json.tpl", context)
    (build_path / "package.json").write_text(result)


def create_main_js(build_path, product_name, url):
    context = {
        "product_name": product_name,
        "url": url,
        "spellcheck_langs": ", ".join(f"'{lang}'" for lang in SPELLCHECK_LANGS),
        "locale_lang": LOCALE_LANG,
        "locale_env": LOCALE_ENV,
    }
    result = render_template("main_js.tpl", context)
    (build_path / "main.js").write_text(result)


def create_desktop_entry(app_name, product_name, category, description):
    context = {
        "app_name": app_name,
        "product_name": product_name,
        "category": category,
        "description": description,
        "opt_dir": OPT_DIR,
    }
    result = render_template("desktop_entry.tpl", context)
    desktop_path = DESKTOP_ENTRIES_DIR / f"{app_name}.desktop"
    desktop_path.write_text(result)
    desktop_path.chmod(0o644)


def process_app(app_cfg):
    app_name = app_cfg["app_name"]
    product_name = app_cfg["name"]
    url = app_cfg["url"]
    icon_name = app_cfg["icon"]
    category = app_cfg["category"]
    description = app_cfg.get("description", f"Launch {product_name}")

    print(f"🚀 Building {product_name}...")

    build_path = BUILD_DIR / app_name
    if build_path.exists():
        shutil.rmtree(build_path)
    build_path.mkdir(parents=True)

    create_package_json(build_path, app_name)
    create_main_js(build_path, product_name, url)

    src_icon = ICONS_DIR / f"{icon_name}.png"
    dst_icon = build_path / "icon.png"
    if src_icon.exists():
        shutil.copy(src_icon, dst_icon)
        os.chmod(dst_icon, 0o644)
    else:
        print(f"⚠️ Icon not found for {product_name}: {src_icon}")

    run_command(["npx", "electron-builder", "--linux", BUILD_TARGET], cwd=build_path)

    dist_dir = build_path / "dist"
    appimage_files = list(dist_dir.glob("*.AppImage"))
    if not appimage_files:
        print(f"❌ AppImage not created for {product_name}")
        return

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
    shutil.rmtree(build_path)

    print(f"✅ {product_name} ready at {opt_app_dir}")


def main():
    """Main function."""
    DESKTOP_ENTRIES_DIR.mkdir(parents=True, exist_ok=True)
    OPT_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    with JSON_FILE.open() as f:
        apps = json.load(f)

    for app_cfg in apps:
        if app_cfg.get("skip"):
            print(f"⏩ Skipping {app_cfg['name']}")
            continue
        process_app(app_cfg)

    print("🏋️ All apps processed successfully.")


if __name__ == "__main__":
    main()
