@echo off
chcp 65001 >nul
title 启动小星 API（llama-cpp-python）

echo [🚀] 正在启动小星模型服务...

python -m llama_cpp.server ^
  --model E:\xiaoxing\llama.cpp\models\qwen1_5-7b-chat-q5_k_m.gguf ^
  --host 127.0.0.1 ^
  --port 8000 ^
  --n_ctx 4096 ^
  --n_gpu_layers 100 ^
  --n_threads 16 ^
  --chat_format chatml ^
  --cache true

REM ✅ 启动失败检测
if %errorlevel% neq 0 (
    echo [❌] 启动失败，请检查模型路径、CUDA 是否可用、是否为 GPU 版本。
    pause
    exit /b %errorlevel%
)

echo [✅] 小星模型服务已关闭或退出。
pause
