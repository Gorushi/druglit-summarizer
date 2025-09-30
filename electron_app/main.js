// fs, ipcMain, dialog 모듈 추가
const { app, BrowserWindow, ipcMain, dialog } = require('electron'); 
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs'); // 파일 저장을 위해 추가

let backendProcess = null;

const createWindow = () => {
  const mainWindow = new BrowserWindow({
    width: 1200, // 너비를 좀 더 넓게 조정
    height: 800,
    webPreferences: {
      // preload 스크립트 경로를 지정
      preload: path.join(__dirname, 'preload.js'),
    }
  });
  mainWindow.loadFile(path.join(__dirname, 'renderer/index.html'));
};

app.whenReady().then(() => {
  // 1. 백엔드 프로세스 실행 
  const backendFileName = process.platform === 'win32' ? 'backend.exe' : 'backend';
  const backendPath = app.isPackaged
    ? path.join(process.resourcesPath, 'backend_dist', backendFileName)
    : path.join(__dirname, '..', 'backend', 'dist', backendFileName);
  
  backendProcess = spawn(backendPath);
  backendProcess.stdout.on('data', (data) => console.log(`Backend: ${data}`));
  backendProcess.stderr.on('data', (data) => console.error(`Backend Error: ${data}`));

  // 2. 프론트엔드 창 생성 
  createWindow();

  // PDF 생성 요청 리스너 추가
  ipcMain.on('print-to-pdf', (event) => {
    const webContents = event.sender;
    const win = BrowserWindow.fromWebContents(webContents);
    
    // 사용자에게 PDF 저장 경로를 묻는 대화상자를 생성
    dialog.showSaveDialog(win, {
      title: '결과를 PDF로 저장',
      defaultPath: 'summary.pdf',
      filters: [{ name: 'PDF 파일', extensions: ['pdf'] }]
    }).then(result => {
      // 사용자가 취소하지 않았다면 PDF 생성 진행
      if (!result.canceled) {
        const pdfPath = result.filePath;
        // 현재 창의 웹 콘텐츠를 PDF로 인쇄
        win.webContents.printToPDF({
          marginsType: 0,
          pageSize: 'A4',
          printBackground: true,
        }).then(data => {
          // 생성된 PDF 데이터를 파일로 작성
          fs.writeFile(pdfPath, data, (error) => {
            if (error) throw error;
            console.log(`PDF 파일이 성공적으로 저장되었습니다: ${pdfPath}`);
            // (선택) 사용자에게 저장 완료 알림을 전송
            dialog.showMessageBox(win, {
                title: "저장 완료",
                message: `PDF 파일이 다음 경로에 저장되었습니다:\n${pdfPath}`
            });
          });
        }).catch(error => {
          console.error(`PDF 생성 실패: ${error}`);
        });
      }
    });
  });

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
