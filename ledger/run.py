#!/usr/bin/env python3
"""账本应用启动脚本"""

import sys
import os

# 确保能找到主模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 检查依赖
try:
    from kivy.app import App
    from kivy.core.window import Window
except ImportError:
    print("错误：缺少 kivy 依赖")
    print("请运行: pip install -r requirements.txt")
    sys.exit(1)

# 导入主应用
from main import LedgerApp


def main():
    """主函数"""
    # 设置窗口初始大小（竖屏比例）
    Window.size = (360, 640)
    Window.clearcolor = (0.95, 0.95, 0.95, 1)
    
    # 运行应用
    LedgerApp().run()


if __name__ == '__main__':
    main()
