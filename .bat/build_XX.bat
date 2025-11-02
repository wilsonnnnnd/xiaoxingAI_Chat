@echo off
setlocal ENABLEDELAYEDEXPANSION
chcp 65001 >nul
title 启动小星 - llama.cpp (Ninja + GGML_CUDA GPU, CUDA=E:\cuda)

:: =========================
:: 1) VS C++ 编译环境
:: =========================
for %%E in (Enterprise Professional Community BuildTools) do (
  if exist "C:\Program Files\Microsoft Visual Studio\2022\%%E\Common7\Tools\VsDevCmd.bat" (
    call "C:\Program Files\Microsoft Visual Studio\2022\%%E\Common7\Tools\VsDevCmd.bat" -arch=amd64
    goto :vs_ok
  )
)
for %%E in (Enterprise Professional Community BuildTools) do (
  if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\%%E\Common7\Tools\VsDevCmd.bat" (
    call "C:\Program Files (x86)\Microsoft Visual Studio\2019\%%E\Common7\Tools\VsDevCmd.bat" -arch=amd64
    goto :vs_ok
  )
)
:vs_ok
where cl >nul 2>&1 || (echo [ERROR] 未检测到 cl.exe；请在 "x64 Native Tools Command Prompt for VS" 里运行。& pause & exit /b 1)

:: =========================
:: 2) CUDA 定位（你装在 E:\cuda）
:: =========================
set "CUDA_PATH=E:\cuda"
if not exist "%CUDA_PATH%\bin\nvcc.exe" (
  echo [ERROR] 未在 %CUDA_PATH% 找到 nvcc.exe
  echo        請確認 CUDA 安裝路徑或修改本腳本中的 CUDA_PATH。
  pause & exit /b 1
)
set "PATH=%CUDA_PATH%\bin;%PATH%"
echo [INFO] CUDA_PATH=%CUDA_PATH%

:: =========================
:: 3) 基本路径/参数
:: =========================
set "SCRIPT_DIR=E:\development\xiaoxing"
set "BASE_DIR=E:\development\xiaoxing\llama.cpp"
set "BUILD_DIR=%BASE_DIR%\build"
set "MODEL_PATH=%BASE_DIR%\models\qwen1_5-7b-chat-q5_k_m.gguf"
set "PROMPT_FILE=%SCRIPT_DIR%\config\prompt.txt"
set "GENERATOR=Ninja"
set "BUILD_TYPE=Release"

:: GPU 设置
set "GPU_LAYERS=20"                 :: 按显存调
set "CMAKE_CUDA_ARCH=89"            :: 4070 = Ada (SM 89)
rmdir /s /q "%BUILD_DIR%"           :: 在配置前清一次（或在 NEED_CLEAR 判断为 ON 时清）

if not exist "%MODEL_PATH%" (echo [ERROR] 模型缺失：%MODEL_PATH% & pause & exit /b 1)
if not exist "%PROMPT_FILE%" (echo [ERROR] system prompt 缺失：%PROMPT_FILE% & pause & exit /b 1)

:: =========================
:: 4) 线程 & prompt 缓存（带指纹）
:: =========================
for /f "tokens=2 delims==" %%a in ('wmic cpu get NumberOfCores /value ^| find "="') do set "CORES=%%a"
if not defined CORES set "CORES=%NUMBER_OF_PROCESSORS%"
set "THREADS=%CORES%"

set "CTX=8192"
set "CACHE_DIR=%SCRIPT_DIR%\cache"
if not exist "%CACHE_DIR%" mkdir "%CACHE_DIR%"

for %%F in ("%MODEL_PATH%") do set "MODEL_NAME=%%~nF"
:: 模型名 + ctx + ngl + 架构 + 生成器 + 构建类型 + CUDA后端
set "CACHE_TAG=%MODEL_NAME%_ctx%CTX%_ngl%GPU_LAYERS%_sm%CMAKE_CUDA_ARCH%_%GENERATOR%_%BUILD_TYPE%_GGMLCUDA.llamacache"
set "CACHE_FILE=%CACHE_DIR%\%CACHE_TAG%"

:: =========================
:: 5) 准备构建（Ninja + GGML_CUDA）
:: =========================
where ninja >nul 2>&1 || (echo [ERROR] 未找到 ninja；winget install Ninja-build.Ninja & pause & exit /b 1)
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"

echo [STEP] 预清理占用进程...
for %%P in (llama-cli.exe llama-server.exe ninja.exe cmake.exe cl.exe link.exe mspdbsrv.exe) do (
  tasklist | findstr /i "%%P" >nul && taskkill /F /IM %%P >nul 2>&1
)

:: 若缓存里不是 Ninja 或没开 GGML_CUDA，则清缓存
set "CACHE_FILE_PATH=%BUILD_DIR%\CMakeCache.txt"
set "NEED_CLEAR="
if exist "%CACHE_FILE_PATH%" (
  for /f "usebackq tokens=1,* delims==" %%A in (`findstr /b "CMAKE_GENERATOR:" "%CACHE_FILE_PATH%"`) do set "CACHED_GEN=%%B"
  for /f "tokens=2 delims==" %%G in ("!CACHED_GEN!") do set "CACHED_GEN_VAL=%%G"
  set "CACHED_GEN_VAL=!CACHED_GEN_VAL: =!"
  if /i not "!CACHED_GEN_VAL!"=="%GENERATOR%" set "NEED_CLEAR=1"

  for /f "usebackq tokens=1,* delims==" %%A in (`findstr /b "GGML_CUDA:" "%CACHE_FILE_PATH%"`) do set "CUDA_LINE=%%B"
  for /f "tokens=2 delims==" %%G in ("!CUDA_LINE!") do set "CUDA_VAL=%%G"
  set "CUDA_VAL=!CUDA_VAL: =!"
  if /i not "!CUDA_VAL!"=="ON" set "NEED_CLEAR=1"
)
if defined NEED_CLEAR (
  echo [WARN] 生成器/后端改变，清理 CMakeCache/CMakeFiles...
  del /f /q "%BUILD_DIR%\CMakeCache.txt" >nul 2>&1
  rmdir /s /q "%BUILD_DIR%\CMakeFiles" >nul 2>&1
  :: 同模型的历史 prompt-cache 一并清掉，避免撞格式
  for %%F in ("%MODEL_PATH%") do set "MODEL_NAME=%%~nF"
  del /f /q "%CACHE_DIR%\%MODEL_NAME%_*.llamacache" >nul 2>&1
)

:: =========================
:: 6) CMake 配置 + 构建（GGML_CUDA）
:: =========================
echo [STEP] 配置 CMake (GGML_CUDA=ON)...
cmake -S "%BASE_DIR%" -B "%BUILD_DIR%" -G "%GENERATOR%" ^
  -DCMAKE_BUILD_TYPE=%BUILD_TYPE% ^
  -DLLAMA_CURL=OFF ^
  -DGGML_CUDA=ON ^
  -DCUDAToolkit_ROOT="%CUDA_PATH%" ^
  -DCMAKE_CUDA_COMPILER="%CUDA_PATH%\bin\nvcc.exe" ^
  -DCMAKE_CUDA_ARCHITECTURES=%CMAKE_CUDA_ARCH%

if errorlevel 1 (echo [ERROR] CMake 配置失败。& pause & exit /b 1)

echo [STEP] 开始构建（并行）...
cmake --build "%BUILD_DIR%" --parallel
if errorlevel 1 (echo [ERROR] 构建失败。& pause & exit /b 1)

:: =========================
:: 7) 启动本地 API（llama-server）
:: =========================
set "BIN_DIR=%BUILD_DIR%\bin"
set "EXEC_SERVER=%BIN_DIR%\llama-server.exe"
if not exist "%EXEC_SERVER%" (echo [ERROR] 未找到可执行文件：%EXEC_SERVER% & dir /b "%BIN_DIR%" & pause & exit /b 1)

call :ensure_unlocked "%EXEC_SERVER%" || (echo [ERROR] EXE 被占用，放弃启动。& pause & exit /b 1)

set "HOST=127.0.0.1"
set "PORT=8000"

:: ========= 生成时间戳 & 日志路径 =========
for /f %%I in ('powershell -NoProfile -Command "(Get-Date).ToString('yyyyMMdd_HHmmss')"') do set "STAMP=%%I"
for %%F in ("%MODEL_PATH%") do set "MODEL_NAME=%%~nF"

set "LOG_DIR=%SCRIPT_DIR%\logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

set "SRV_LOG=%LOG_DIR%\server_%MODEL_NAME%_ctx%CTX%_ngl%GPU_LAYERS%_sm%CMAKE_CUDA_ARCH%_%STAMP%.log"

:: 先预创建日志文件，避免 PowerShell 找不到
type nul > "%SRV_LOG%"

:: ========= 启动 API 服务器 =========
set "HOST=127.0.0.1"
set "PORT=8000"
cd /d "%BIN_DIR%"

echo [INFO] 日志：%SRV_LOG%
start "" cmd /c ^
"\"%EXEC_SERVER%\" --host %HOST% --port %PORT% --model \"%MODEL_PATH%\" ^
 -c %CTX% --threads %THREADS% --gpu-layers %GPU_LAYERS% -np 2 ^
 1>>\"%SRV_LOG%\" 2>>&1"

echo ✅ 已尝试启动：http://%HOST%:%PORT%
echo 🔎 实时查看（Ctrl+C 停止跟随，不会关服务器）：
powershell -NoProfile -Command "Get-Content -Path '%SRV_LOG%' -Tail 80 -Wait"



:: ============ 子程序 ============
:ensure_unlocked
set "TARGET=%~1"
for %%F in ("%TARGET%") do (set "EXE_DIR=%%~dpF" & set "EXE_NAME=%%~nxF")
set "TEST_NAME=%EXE_NAME%.locktest"
rename "%EXE_DIR%%EXE_NAME%" "%TEST_NAME%" >nul 2>&1 && (rename "%EXE_DIR%%TEST_NAME%" "%EXE_NAME%" >nul 2>&1 & exit /b 0)
for %%P in (llama-cli.exe llama-server.exe ninja.exe cmake.exe cl.exe link.exe mspdbsrv.exe) do taskkill /F /IM %%P >nul 2>&1
timeout /t 1 >nul
rename "%EXE_DIR%%EXE_NAME%" "%TEST_NAME%" >nul 2>&1 && (rename "%EXE_DIR%%TEST_NAME%" "%EXE_NAME%" >nul 2>&1 & exit /b 0)
exit /b 1
