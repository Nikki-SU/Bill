# 账本 - 本地记账应用
# 使用 Kivy 框架，支持 Android/iOS/桌面

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database
from ui.record_screen import RecordScreen
from ui.summary_screen import SummaryScreen
from ui.detail_screen import DetailScreen


class MainScreen(Screen):
    """主界面 - 三按钮导航"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        # 主容器
        main_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=[dp(30), dp(40), dp(30), dp(30)]
        )
        
        # 标题
        title = Label(
            text='账本',
            font_size=sp(48),
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=0.2
        )
        main_layout.add_widget(title)
        
        # 按钮区域
        button_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(16),
            size_hint_y=0.6
        )
        
        # 记账按钮
        btn_record = Button(
            text='记账',
            font_size=sp(22),
            background_color=(0.15, 0.15, 0.15, 1),
            color=(1, 1, 1, 1),
            size_hint_y=0.2,
            background_normal='',
            background_down=''
        )
        btn_record.bind(on_press=self.go_to_record)
        button_layout.add_widget(btn_record)
        
        # 总结按钮
        btn_summary = Button(
            text='总结',
            font_size=sp(22),
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            size_hint_y=0.2,
            background_normal='',
            background_down=''
        )
        btn_summary.bind(on_press=self.go_to_summary)
        button_layout.add_widget(btn_summary)
        
        # 明细按钮
        btn_detail = Button(
            text='明细',
            font_size=sp(22),
            background_color=(0.45, 0.45, 0.45, 1),
            color=(1, 1, 1, 1),
            size_hint_y=0.2,
            background_normal='',
            background_down=''
        )
        btn_detail.bind(on_press=self.go_to_detail)
        button_layout.add_widget(btn_detail)
        
        main_layout.add_widget(button_layout)
        self.add_widget(main_layout)
    
    def go_to_record(self, instance):
        self.manager.current = 'record'
    
    def go_to_summary(self, instance):
        self.manager.current = 'summary'
    
    def go_to_detail(self, instance):
        self.manager.current = 'detail'


class LedgerApp(App):
    """账本应用主类"""
    
    def build(self):
        self.title = '账本'
        
        # 设置窗口背景色（浅灰色）
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        
        # 初始化数据库
        self.db = Database()
        
        # 创建屏幕管理器
        sm = ScreenManager()
        
        # 添加各个屏幕
        main_screen = MainScreen(name='main')
        record_screen = RecordScreen(name='record', db=self.db)
        summary_screen = SummaryScreen(name='summary', db=self.db)
        detail_screen = DetailScreen(name='detail', db=self.db)
        
        sm.add_widget(main_screen)
        sm.add_widget(record_screen)
        sm.add_widget(summary_screen)
        sm.add_widget(detail_screen)
        
        return sm
    
    # 重新加载数据（从详情页返回时）
    def reload_data(self):
        if hasattr(self, 'db'):
            self.db.reload()


if __name__ == '__main__':
    LedgerApp().run()
