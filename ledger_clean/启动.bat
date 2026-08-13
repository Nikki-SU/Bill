@echo off
chcp 65001 >nul
title 账本 - 个人记账应用

echo ====================================================
echo   账本 - 个人记账应用
echo ====================================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python
    echo.
    echo 请先安装 Python: https://www.python.org/downloads/
    echo 安装时请勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

:: 运行应用
echo 正在启动应用...
echo.
python app_tkinter.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 应用运行失败
    echo.
    echo 可能的原因:
    echo 1. Python 版本不兼容
    echo 2. Tkinter 未正确安装
    echo.
    echo 建议: 安装 Python 3.10-3.13 版本
    echo 下载地址: https://www.python.org/downloads/
    pause
)
