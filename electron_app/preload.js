// Renderer 측 (app.js)에서 Main 프로세스(main.js)의 기능을 안전하게 호출할 수 있도록 window.electronAPI라는 다리를 놓아줌
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  printToPDF: () => ipcRenderer.send('print-to-pdf'),
});
