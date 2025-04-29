# Variables
REQUIRED_NODE_MAJOR_VERSION ?= 22
REQUIRED_ELECTRON_VERSION ?= 36.0.0
REQUIRED_ELECTRON_BUILDER_VERSION ?= 26.0.12
APP_SPELLCHECK_LANGS ?= en-US,pt-BR
APP_USERDATA ?= $(CURDIR)/user-data/$(USER)
APP_LANG ?= pt-BR

# Targets

.PHONY: all setup prepare build install-desktop clean purge check

all: build

setup:
	@echo "📦 Installing Electron and Electron-Builder..."
	npm install -g electron@$(REQUIRED_ELECTRON_VERSION) electron-builder@$(REQUIRED_ELECTRON_BUILDER_VERSION)

prepare:
	@echo "📂 Creating necessary directories..."
	mkdir -p build opt desktop-entries icons user-data/$(USER)

build: prepare setup
	@echo "🚀 Building applications..."
	APP_SPELLCHECK_LANGS=$(APP_SPELLCHECK_LANGS) \
	APP_USERDATA=$(APP_USERDATA) \
	APP_LANG=$(APP_LANG) \
	REQUIRED_ELECTRON_VERSION=$(REQUIRED_ELECTRON_VERSION) \
	REQUIRED_NODE_MAJOR_VERSION=$(REQUIRED_NODE_MAJOR_VERSION) \
	python3 generate_apps.py
	$(MAKE) install-desktop

install-desktop:
	@echo "🖥️ Installing desktop entries..."
	mkdir -p ~/.local/share/applications
	cp desktop-entries/*.desktop ~/.local/share/applications/
	-update-desktop-database ~/.local/share/applications || true

clean:
	@echo "🧹 Cleaning project..."
	rm -rf build opt desktop-entries
	find ~/.local/share/applications -name '*.desktop' -exec grep -l '/opt/' {} \; | xargs rm -f || true

purge: clean
	@echo "🧹 Purging user data..."
	rm -rf user-data

check:
	@echo "🔎 Checking environment versions..."
	node --version
	npm --version
	python3 --version
	which electron-builder || true

