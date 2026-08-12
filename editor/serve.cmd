@echo off
setlocal
set "NODE_EXE=C:\Users\Donghyun\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
if not exist "%NODE_EXE%" (
  echo Node.js was not found at the configured Codex runtime path.
  echo Install Node.js LTS, then run: node server.mjs
  pause
  exit /b 1
)
"%NODE_EXE%" "%~dp0server.mjs"
pause
