@echo off
chcp 65001 >nul
title 启动小星 - llama.cpp API 模式（持续服务，GPU 简版）

:: 路径
set "BASE_DIR=E:\development\xiaoxing\llama.cpp"
set "MODEL_PATH=%BASE_DIR%\models\qwen1_5-7b-chat-q5_k_m.gguf"
set "SERVER_EXE=%BASE_DIR%\build\bin\llama-server.exe"
set "LOG_FILE=%BASE_DIR%\build\bin\server_log.txt"

:: CUDA 放入 PATH（确保能找到 cudart/cublas）
set "CUDA_PATH=E:\cuda"
set "PATH=%CUDA_PATH%\bin;%PATH%"

:: 检查
if not exist "%SERVER_EXE%" (
  echo ❌ 未找到 llama-server.exe，请先构建带 CUDA 的版本
  pause & exit /b
)
if not exist "%MODEL_PATH%" (
  echo ❌ 模型缺失：%MODEL_PATH%
  pause & exit /b
)

:: 启动（按显存调整 --gpu-layers: 8/12/16/20/28...）
cd /d "%BASE_DIR%\build\bin"
echo [INFO] 日志：%LOG_FILE%
if exist "%LOG_FILE%" del /f /q "%LOG_FILE%" >nul 2>&1

:: 关键修复：用一行命令传给 cmd /c，参数不会被拆开，日志正确写入
start "" /d "%BASE_DIR%\build\bin" cmd /c ^
""%SERVER_EXE%" --host 127.0.0.1 --port 8000 --model "%MODEL_PATH%" --ctx-size 8192 --threads 4 --mlock --gpu-layers 20 1>>"%LOG_FILE%" 2>>&1"

echo ✅ 已尝试启动： http://127.0.0.1:8000
echo 🔎 如未起来，请查看日志末尾：
powershell -NoProfile -Command "Get-Content -Path '%LOG_FILE%' -Tail 30"
echo.
pause
