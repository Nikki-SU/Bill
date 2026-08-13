@echo off
chcp 65001 >nul
title 账本 - 打包工具

echo ====================================================
echo   账本 APP 打包工具
echo ====================================================
echo.

:: 检查 Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Node.js
    echo.
    echo 请先安装 Node.js: https://nodejs.org/
    echo 建议下载 LTS 版本
    echo.
    pause
    exit /b 1
)

echo [1/5] 安装依赖...
call npm install
if %errorlevel% neq 0 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo.
echo [2/5] 初始化 Capacitor...
if not exist "capacitor.config.ts" (
    call npx cap init "账本" "com.ledger.app" --web-dir "."
)

echo.
echo [3/5] 添加 Android 平台...
if not exist "android" (
    call npx cap add android
    if %errorlevel% neq 0 (
        echo [提示] 如果添加 Android 失败，请检查是否安装了 Android Studio
        echo        下载地址: https://developer.android.com/studio
        pause
        exit /b 1
    )
)

echo.
echo [4/5] 同步文件...
call npx cap sync android
if %errorlevel% neq 0 (
    echo [错误] 同步失败
    pause
    exit /b 1
)

echo.
echo [5/5] 打开 Android Studio...
if exist "android" (
    start android
    echo.
    echo ====================================================
    echo   已打开 Android Studio
    echo   
    echo   在 Android Studio 中:
    echo   1. 等待项目加载完成
    echo   2. 点击 Build - Build APK(s)
    echo   3. APK 文件在 android\app\build\outputs\apk\debug\
    echo ====================================================
    echo.
)

echo.
pause
