@echo off
chcp 65001 >nul
title 账本 - iOS 打包（需在 Mac 上运行）

echo ====================================================
echo   账本 iOS 打包说明
echo ====================================================
echo.
echo   iOS 打包必须在 Mac 电脑上进行！
echo.
echo   步骤：
echo   1. 在 Mac 上安装 Xcode
echo   2. 安装 Node.js (https://nodejs.org/)
echo   3. 复制本项目到 Mac
echo   4. 执行以下命令：
echo.
echo      cd ledger_app
echo      npm install
echo      npx cap add ios
echo      npx cap sync ios
echo      npx cap open ios
echo.
echo   5. 在 Xcode 中配置签名并打包
echo.
echo ====================================================
echo.

pause
