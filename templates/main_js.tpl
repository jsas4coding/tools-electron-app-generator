const { app, BrowserWindow, session, Menu } = require('electron');
const path = require('path');

function createWindow() {
  const chromeVersion = process.versions.chrome;
  const userAgent = `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/$${chromeVersion} Safari/537.36`;

  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    fullscreenable: true,
    title: '${product_name}',
    icon: path.join(__dirname, 'icon.png'),
    backgroundColor: '#ffffff',
    autoHideMenuBar: true,
    webPreferences: {
      spellcheck: true,
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      webSecurity: true,
      enableRemoteModule: false
    }
  });

  session.defaultSession.setSpellCheckerLanguages([${spellcheck_langs}]);
  win.webContents.setUserAgent(userAgent);
  win.loadURL('${url}');
  win.on('page-title-updated', (e) => e.preventDefault());

  win.webContents.on('before-input-event', (event, input) => {
    if (input.type === 'keyDown') {
      const key = input.key.toLowerCase();
      if (key === 'f11') {
        win.setFullScreen(!win.isFullScreen());
        event.preventDefault();
      }
      if ((input.control || input.meta) && (key === 'w' || key === 'f4')) {
        event.preventDefault();
        win.destroy();
        app.quit();
        process.exit(0);
      }
      if ((input.control || input.meta) && key === 'r') {
        win.reload();
        event.preventDefault();
      }
      if (key === 'f5') {
        win.reload();
        event.preventDefault();
      }
    }
  });

  win.webContents.on('context-menu', (e, params) => {
    const menu = Menu.buildFromTemplate([
      { role: 'reload' },
      { role: 'copy' },
      { role: 'paste' },
      { role: 'selectAll' },
      ...(params.linkURL ? [{
        label: 'Copy Link Address',
        click: () => {
          require('electron').clipboard.writeText(params.linkURL);
        }
      }] : []),
      ...(params.misspelledWord ? [{
        label: `Spelling Suggestions for "$${params.misspelledWord}"`,
        submenu: (params.dictionarySuggestions || []).map(suggestion => ({
          label: suggestion,
          click: () => {
            win.webContents.replaceMisspelling(suggestion);
          }
        }))
      }] : [])
    ]);
    menu.popup();
  }); 

  win.webContents.setWindowOpenHandler(({ url }) => {
    win.loadURL(url);
    console.log(`🔗 Opening inside app: $${url}`);
    return { action: 'deny' };
  });

  win.removeMenu();
}

app.commandLine.appendSwitch('lang', '${locale_lang}');
process.env.LANG = '${locale_env}';
process.env.LC_ALL = '${locale_env}';

app.whenReady().then(() => {
  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
    process.exit(0);
  }
});

// vi: ft=javascript
