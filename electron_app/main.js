const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process'); // 자식 프로세스를 위한 모듈 추가

let backendProcess = null; // 백엔드 프로세스를 저장할 변수

// createWindow 함수 (이전과 동일)
const createWindow = () => {
  const mainWindow = new BrowserWindow({ /* ... 옵션 ... */ });
  mainWindow.loadFile(path.join(__dirname, 'renderer/index.html'));
};

// Electron 앱이 준비되면 실행
app.whenReady().then(() => {
  // 1. 백엔드 프로세스 실행
  const backendFileName = process.platform === 'win32' ? 'backend.exe' : 'backend';

  const backendPath = app.isPackaged
    ? path.join(process.resourcesPath, 'backend_dist', backendFileName)
    : path.join(__dirname, '..', 'backend', 'dist', backendFileName);
  
  backendProcess = spawn(backendPath);

  backendProcess.stdout.on('data', (data) => {
    console.log(`Backend: ${data}`); // 백엔드 로그 출력 (디버깅용)
  });
  backendProcess.stderr.on('data', (data) => {
    console.error(`Backend Error: ${data}`);
  });

  // 2. 프론트엔드 창 생성
  createWindow();

  // ... (activate 이벤트 리스너) ...
});

// 모든 창이 닫혔을 때 실행
app.on('window-all-closed', () => {
  // 3. 백엔드 프로세스 종료
  if (backendProcess) {
    backendProcess.kill();
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
