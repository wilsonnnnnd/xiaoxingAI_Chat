@echo off
chcp 65001 >nul
title 启动小星 - llama.cpp API 模式（持续服务）

:: 设置路径
set BASE_DIR=E:\xiaoxing\llama.cpp
set MODEL_PATH=%BASE_DIR%\models\qwen1_5-7b-chat-q5_k_m.gguf
set SERVER_EXE=%BASE_DIR%\build\bin\llama-server.exe

:: 检查 server.exe 是否存在
if not exist "%SERVER_EXE%" (
    echo ❌ 未找到 llama-server.exe，请确认已构建！
    pause
    exit /b
)

:: 启动 API 模型服务
cd /d "%BASE_DIR%\build\bin"
start "" "%SERVER_EXE%" ^
  --host 127.0.0.1 ^
  --port 8000 ^
  --model "%MODEL_PATH%" ^
  --ctx-size 8192 ^
  --mlock ^
  --threads 4

echo ✅ llama.cpp 模型服务已启动在 http://127.0.0.1:8000
pause
