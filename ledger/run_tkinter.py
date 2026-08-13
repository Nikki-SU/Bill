#!/usr/bin/env python3
"""账本 - 启动脚本 (Tkinter版本)"""
import sys
import os

# 确保路径正确
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 检查 Tkinter 是否可用
try:
    import tkinter
except ImportError:
    print("错误：无法导入 tkinter")
    print("在 Windows 上，请确保安装了完整的 Python（Tkinter 通常随 Python 一起安装）")
    print("重新安装 Python 时，勾选 'tcl/tk and IDLE' 选项")
    sys.exit(1)

from app_tkinter import LedgerApp


def main():
    print("=" * 50)
    print("  账本 - 个人记账应用")
    print("=" * 50)
    print("  正在启动...")
    print()
    
    app = LedgerApp()
    app.run()


if __name__ == '__main__':
    main()
