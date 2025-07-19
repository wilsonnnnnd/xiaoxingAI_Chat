@echo off
chcp 65001 >nul
title 启动小星 - llama.cpp AI 女友聊天助手（快速启动）

:: 设置路径
set SCRIPT_DIR=E:\xiaoxing
set BASE_DIR=E:\xiaoxing\llama.cpp
set BUILD_DIR=%BASE_DIR%\build
set EXECUTABLE=%BUILD_DIR%\bin\llama-cli.exe
set MODEL_PATH=%BASE_DIR%\models\qwen1_5-7b-chat-q5_k_m.gguf
set PROMPT_FILE=%SCRIPT_DIR%\prompt.txt

:: 检查 llama-cli.exe 是否存在
if not exist "%EXECUTABLE%" (
    echo ❌ 未找到 llama-cli.exe，请先运行构建脚本！
    pause
    exit /b
)

:: 检查 prompt.txt 是否存在
if not exist "%PROMPT_FILE%" (
    echo ❌ 未找到 prompt.txt，请确认 system prompt 文件存在！
    pause
    exit /b
)

:: 启动小星
cd /d "%BUILD_DIR%\bin\Release"
"%EXECUTABLE%" ^
  -m "%MODEL_PATH%" ^
  -i -n 512 -c 8192 ^
  --system-prompt-file "%PROMPT_FILE%" ^
  --top_k 50 ^
  --top_p 0.9 ^
  --temp 0.7 ^
  --repeat_penalty 1.1 ^
  -p "小星～我来找你聊天啦～"

pause
