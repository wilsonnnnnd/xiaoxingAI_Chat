@echo off
chcp 65001 >nul
title 启动小星 - llama.cpp AI 女友聊天助手

:: 设置路径
set SCRIPT_DIR=E:\xiaoxing
set BASE_DIR=E:\xiaoxing\llama.cpp
set BUILD_DIR=%BASE_DIR%\build
set MODEL_PATH=%BASE_DIR%\models\qwen1_5-7b-chat-q5_k_m.gguf
set EXECUTABLE=%BUILD_DIR%\bin\llama-cli.exe
set PROMPT_FILE=%SCRIPT_DIR%\prompt.txt

:: 清理旧构建（如需调试，可注释掉）
rem if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"

:: 构建 llama.cpp（如不需要可注释）
cmake -S "%BASE_DIR%" -B "%BUILD_DIR%" -G "NMake Makefiles" -DLLAMA_CURL=OFF
cmake --build "%BUILD_DIR%"

:: 切换目录
cd /d "%BUILD_DIR%\bin\Release"

:: 启动 llama-cli，传入 system prompt 文件
"%EXECUTABLE%" ^
  -m "%MODEL_PATH%" ^
  -i -n 512 -c 8192 ^
  --system-prompt-file "%PROMPT_FILE%" ^
  --top_k 50 ^
  --top_p 0.9 ^
  --temp 0.7 ^
  --repeat_penalty 1.1 ^
  -p "你好，小星，现在是几点啦？"

pause
