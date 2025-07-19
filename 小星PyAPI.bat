@echo off
chcp 65001 >nul
title 启动小星 API（llama-cpp-python）

python -m llama_cpp.server ^
  --model E:\xiaoxing\llama.cpp\models\qwen1_5-7b-chat-q5_k_m.gguf ^
  --host 127.0.0.1 ^
  --port 8000 ^
  --n_ctx 4096 ^
  --n_threads 4
  

pause
