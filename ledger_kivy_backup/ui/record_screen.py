# 记账页面 - 打勾式列表
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.metrics import dp, sp
from kivy.core.window import Window

from datetime import datetime


class RecordItem(BoxLayout):
    """单条记账记录项"""
    
    def __init__(self, record, on_toggle=None, on_edit=None, on_delete=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = dp(8)
        self.size_hint_y = None
        self.height = dp(56)
        self.padding = [dp(8), dp(4)]
        
        self.record = record
        self.on_toggle_callback = on_toggle
        self.on_edit_callback = on_edit
        self.on_delete_callback = on_delete
        
        self._build_ui()
    
    def _build_ui(self):
        # 打勾按钮（颜色表示类型）
        is_income = self.record['type'] == 'income'
        base_color = (0.2, 0.7, 0.2, 1) if is_income else (0.8, 0.2, 0.2, 1)
        bg_color = (0.15, 0.15, 0.15, 1) if is_income else (0.6, 0.15, 0.15, 1)
        
        self.check_btn = Button(
            text='✓' if self.record['checked'] else '○',
            size_hint_x=0.12,
            font_size=sp(20),
            color=bg_color,
            background_color=(0.9, 0.9, 0.9, 1) if not self.record['checked'] else base_color,
            background_normal='',
            background_down='',
            bold=True
        )
        self.check_btn.bind(on_press=self._on_toggle)
        self.add_widget(self.check_btn)
        
        # 来源/物品名称
        source_label = Label(
            text=self.record['source'][:12],
            size_hint_x=0.45,
            font_size=sp(16),
            halign='left',
            valign='middle',
            color=(0.2, 0.2, 0.2, 1),
            bold=self.record['checked']
        )
        source_label.bind(size=source_label.setter('text_size'))
        self.add_widget(source_label)
        
        # 金额（红绿色标识）
        amount_color = (0.15, 0.65, 0.15, 1) if is_income else (0.75, 0.15, 0.15, 1)
        amount_prefix = '+' if is_income else '-'
        amount_label = Label(
            text=f'{amount_prefix}{self.record["amount"]:.2f}',
            size_hint_x=0.25,
            font_size=sp(18),
            halign='right',
            valign='middle',
            color=amount_color,
            bold=True
        )
        amount_label.bind(size=amount_label.setter('text_size'))
        self.add_widget(amount_label)
        
        # 操作按钮
        action_layout = BoxLayout(
            orientation='horizontal',
            size_hint_x=0.18,
            spacing=dp(4)
        )
        
        # 编辑按钮
        edit_btn = Button(
            text='✎',
            size_hint_x=0.5,
            font_size=sp(16),
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            background_down=''
        )
        edit_btn.bind(on_press=self._on_edit)
        action_layout.add_widget(edit_btn)
        
        # 删除按钮
        delete_btn = Button(
            text='×',
            size_hint_x=0.5,
            font_size=sp(18),
            background_color=(0.5, 0.1, 0.1, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            background_down=''
        )
        delete_btn.bind(on_press=self._on_delete)
        action_layout.add_widget(delete_btn)
        
        self.add_widget(action_layout)
    
    def _on_toggle(self, instance):
        if self.on_toggle_callback:
            self.on_toggle_callback(self.record['id'])
    
    def _on_edit(self, instance):
        if self.on_edit_callback:
            self.on_edit_callback(self.record['id'])
    
    def _on_delete(self, instance):
        if self.on_delete_callback:
            self.on_delete_callback(self.record['id'])


class RecordScreen(Screen):
    """记账页面"""
    
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self._build_ui()
    
    def _build_ui(self):
        main_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(16), dp(20), dp(16), dp(16)]
        )
        
        # 顶部标题栏
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50)
        )
        
        back_btn = Button(
            text='← 返回',
            size_hint_x=0.2,
            font_size=sp(16),
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            background_down=''
        )
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        
        title_label = Label(
            text='记 账',
            size_hint_x=0.6,
            font_size=sp(22),
            bold=True,
            color=(0.15, 0.15, 0.15, 1)
        )
        header.add_widget(title_label)
        
        # 今日日期
        now = datetime.now()
        date_text = now.strftime('%Y/%m/%d')
        weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][now.weekday()]
        date_label = Label(
            text=f'{date_text} {weekday}',
            size_hint_x=0.2,
            font_size=sp(12),
            color=(0.5, 0.5, 0.5, 1)
        )
        header.add_widget(date_label)
        
        main_layout.add_widget(header)
        
        # 今日统计栏
        self.summary_bar = self._create_summary_bar()
        main_layout.add_widget(self.summary_bar)
        
        # 输入区域
        input_area = self._create_input_area()
        main_layout.add_widget(input_area)
        
        # 记录列表（滚动）
        scroll_view = ScrollView(
            size_hint=(1, 1),
            bar_width=dp(4),
            scroll_type=['bars', 'content']
        )
        
        self.record_list = GridLayout(
            cols=1,
            spacing=dp(6),
            padding=[dp(0), dp(4)],
            size_hint_y=None
        )
        self.record_list.bind(minimum_height=self.record_list.setter('height'))
        
        scroll_view.add_widget(self.record_list)
        main_layout.add_widget(scroll_view)
        
        self.add_widget(main_layout)
        self._refresh_records()
    
    def _create_summary_bar(self):
        """创建今日统计栏"""
        now = datetime.now()
        today_records = self.db.get_records_by_date(now.strftime('%Y-%m-%d'))
        
        income = sum(r['amount'] for r in today_records if r['type'] == 'income')
        expense = sum(r['amount'] for r in today_records if r['type'] == 'expense')
        net = income - expense
        
        bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(8),
            padding=[dp(12), dp(8)]
        )
        
        # 收入
        income_box = BoxLayout(orientation='vertical', size_hint_x=0.33)
        income_label = Label(
            text='收入',
            font_size=sp(12),
            color=(0.5, 0.5, 0.5, 1)
        )
        income_value = Label(
            text=f'+{income:.2f}',
            font_size=sp(16),
            color=(0.15, 0.65, 0.15, 1),
            bold=True
        )
        income_box.add_widget(income_label)
        income_box.add_widget(income_value)
        bar.add_widget(income_box)
        
        # 支出
        expense_box = BoxLayout(orientation='vertical', size_hint_x=0.33)
        expense_label = Label(
            text='支出',
            font_size=sp(12),
            color=(0.5, 0.5, 0.5, 1)
        )
        expense_value = Label(
            text=f'-{expense:.2f}',
            font_size=sp(16),
            color=(0.75, 0.15, 0.15, 1),
            bold=True
        )
        expense_box.add_widget(expense_label)
        expense_box.add_widget(expense_value)
        bar.add_widget(expense_box)
        
        # 结余
        net_box = BoxLayout(orientation='vertical', size_hint_x=0.34)
        net_label = Label(
            text='结余',
            font_size=sp(12),
            color=(0.5, 0.5, 0.5, 1)
        )
        net_color = (0.15, 0.65, 0.15, 1) if net >= 0 else (0.75, 0.15, 0.15, 1)
        net_value = Label(
            text=f'{net:+.2f}',
            font_size=sp(16),
            color=net_color,
            bold=True
        )
        net_box.add_widget(net_label)
        net_box.add_widget(net_value)
        bar.add_widget(net_box)
        
        return bar
    
    def _create_input_area(self):
        """创建输入区域"""
        area = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(140),
            spacing=dp(8),
            padding=[dp(0), dp(8)]
        )
        
        # 类型选择（收入/支出）
        type_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(36),
            spacing=dp(8)
        )
        
        self.income_btn = Button(
            text='收入',
            size_hint_x=0.5,
            font_size=sp(14),
            background_color=(0.15, 0.65, 0.15, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            background_down='',
            bold=True
        )
        self.income_btn.bind(on_press=lambda x: self._set_type('income'))
        type_layout.add_widget(self.income_btn)
        
        self.expense_btn = Button(
            text='支出',
            size_hint_x=0.5,
            font_size=sp(14),
            background_color=(0.35, 0.35, 0.35, 1),
            color=(0.7, 0.7, 0.7, 1),
            background_normal='',
            background_down=''
        )
        self.expense_btn.bind(on_press=lambda x: self._set_type('expense'))
        type_layout.add_widget(self.expense_btn)
        
        area.add_widget(type_layout)
        
        # 输入框
        input_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(48)
        )
        
        self.source_input = TextInput(
            hint_text='物品/来源',
            size_hint_x=0.55,
            font_size=sp(14),
            padding=[dp(10), dp(12)],
            multiline=False
        )
        input_layout.add_widget(self.source_input)
        
        self.amount_input = TextInput(
            hint_text='金额',
            size_hint_x=0.35,
            font_size=sp(14),
            padding=[dp(10), dp(12)],
            multiline=False,
            input_filter='float'
        )
        input_layout.add_widget(self.amount_input)
        
        # 添加按钮
        add_btn = Button(
            text='+',
            size_hint_x=0.1,
            font_size=sp(20),
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            background_down='',
            bold=True
        )
        add_btn.bind(on_press=self._add_record)
        input_layout.add_widget(add_btn)
        
        area.add_widget(input_layout)
        
        # 提示
        self.current_type = 'expense'
        
        return area
    
    def _set_type(self, record_type):
        """设置当前类型"""
        self.current_type = record_type
        if record_type == 'income':
            self.income_btn.background_color = (0.15, 0.65, 0.15, 1)
            self.income_btn.color = (1, 1, 1, 1)
            self.income_btn.bold = True
            self.expense_btn.background_color = (0.35, 0.35, 0.35, 1)
            self.expense_btn.color = (0.7, 0.7, 0.7, 1)
            self.expense_btn.bold = False
        else:
            self.expense_btn.background_color = (0.75, 0.15, 0.15, 1)
            self.expense_btn.color = (1, 1, 1, 1)
            self.expense_btn.bold = True
            self.income_btn.background_color = (0.35, 0.35, 0.35, 1)
            self.income_btn.color = (0.7, 0.7, 0.7, 1)
            self.income_btn.bold = False
    
    def _add_record(self, instance):
        """添加新记录"""
        source = self.source_input.text.strip()
        amount_text = self.amount_input.text.strip()
        
        if not source:
            self._show_popup('提示', '请输入物品/来源名称')
            return
        
        if not amount_text:
            self._show_popup('提示', '请输入金额')
            return
        
        try:
            amount = float(amount_text)
            if amount <= 0:
                self._show_popup('提示', '金额必须大于0')
                return
        except ValueError:
            self._show_popup('提示', '金额格式错误')
            return
        
        self.db.add_record(source, amount, self.current_type)
        
        # 清空输入
        self.source_input.text = ''
        self.amount_input.text = ''
        
        # 刷新
        self._refresh_records()
    
    def _refresh_records(self):
        """刷新记录列表"""
        self.record_list.clear_widgets()
        
        # 重新创建统计栏
        self.summary_bar.clear_widgets()
        new_bar = self._create_summary_bar()
        for widget in new_bar.children:
            self.summary_bar.add_widget(widget)
        
        # 获取今日记录
        now = datetime.now()
        today_records = self.db.get_records_by_date(now.strftime('%Y-%m-%d'))
        today_records.sort(key=lambda r: r['time'], reverse=True)
        
        if not today_records:
            empty_label = Label(
                text='今日暂无记录',
                font_size=sp(16),
                color=(0.6, 0.6, 0.6, 1),
                size_hint_y=None,
                height=dp(60)
            )
            self.record_list.add_widget(empty_label)
            return
        
        for record in today_records:
            item = RecordItem(
                record=record,
                on_toggle=self._on_toggle,
                on_edit=self._on_edit,
                on_delete=self._on_delete
            )
            self.record_list.add_widget(item)
    
    def _on_toggle(self, record_id):
        """切换打勾状态"""
        self.db.toggle_checked(record_id)
        self._refresh_records()
    
    def _on_edit(self, record_id):
        """编辑记录"""
        record = None
        for r in self.db.records:
            if r['id'] == record_id:
                record = r
                break
        
        if not record:
            return
        
        # 创建编辑弹窗
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(20), dp(20)]
        )
        
        content.add_widget(Label(text='来源/物品:', font_size=sp(14), color=(0.3, 0.3, 0.3, 1)))
        source_input = TextInput(
            text=record['source'],
            font_size=sp(14),
            size_hint_y=None,
            height=dp(44)
        )
        content.add_widget(source_input)
        
        content.add_widget(Label(text='金额:', font_size=sp(14), color=(0.3, 0.3, 0.3, 1)))
        amount_input = TextInput(
            text=str(record['amount']),
            font_size=sp(14),
            size_hint_y=None,
            height=dp(44),
            input_filter='float'
        )
        content.add_widget(amount_input)
        
        # 类型选择
        type_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(44),
            spacing=dp(10)
        )
        
        type_label = Label(text='类型:', font_size=sp(14), color=(0.3, 0.3, 0.3, 1), size_hint_x=0.2)
        type_layout.add_widget(type_label)
        
        type_val = '收入' if record['type'] == 'income' else '支出'
        type_color = (0.15, 0.65, 0.15, 1) if record['type'] == 'income' else (0.75, 0.15, 0.15, 1)
        type_display = Label(text=type_val, font_size=sp(14), color=type_color, size_hint_x=0.8, bold=True)
        type_layout.add_widget(type_display)
        
        content.add_widget(type_layout)
        
        # 按钮
        btn_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(44),
            spacing=dp(10),
            padding=[dp(0), dp(10)]
        )
        
        popup = None  # 稍后赋值
        
        def save_edit(instance):
            new_source = source_input.text.strip()
            new_amount = amount_input.text.strip()
            
            if not new_source:
                self._show_popup('提示', '请输入来源/物品名称')
                return
            
            try:
                new_amount = float(new_amount)
                if new_amount <= 0:
                    self._show_popup('提示', '金额必须大于0')
                    return
            except ValueError:
                self._show_popup('提示', '金额格式错误')
                return
            
            self.db.update_record(record_id, source=new_source, amount=new_amount)
            popup.dismiss()
            self._refresh_records()
        
        def cancel_edit(instance):
            popup.dismiss()
        
        save_btn = Button(
            text='保存',
            size_hint_x=0.5,
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            background_down=''
        )
        save_btn.bind(on_press=save_edit)
        
        cancel_btn = Button(
            text='取消',
            size_hint_x=0.5,
            background_color=(0.5, 0.5, 0.5, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            background_down=''
        )
        cancel_btn.bind(on_press=cancel_edit)
        
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='编辑记录',
            content=content,
            size_hint=(0.85, None),
            height=dp(350),
            separator_color=(0.3, 0.3, 0.3, 1),
            title_size=sp(16)
        )
        popup.open()
    
    def _on_delete(self, record_id):
        """删除记录"""
        # 确认弹窗
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=[dp(20), dp(20)]
        )
        
        content.add_widget(Label(text='确定要删除这条记录吗？', font_size=sp(16), color=(0.3, 0.3, 0.3, 1)))
        
        btn_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(44),
            spacing=dp(10),
            padding=[dp(0), dp(10)]
        )
        
        popup = None
        
        def confirm_delete(instance):
            self.db.delete_record(record_id)
            popup.dismiss()
            self._refresh_records()
        
        def cancel_delete(instance):
            popup.dismiss()
        
        confirm_btn = Button(
            text='删除',
            size_hint_x=0.5,
            background_color=(0.7, 0.1, 0.1, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            background_down=''
        )
        confirm_btn.bind(on_press=confirm_delete)
        
        cancel_btn = Button(
            text='取消',
            size_hint_x=0.5,
            background_color=(0.5, 0.5, 0.5, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            background_down=''
        )
        cancel_btn.bind(on_press=cancel_delete)
        
        btn_layout.add_widget(confirm_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='确认删除',
            content=content,
            size_hint=(0.8, None),
            height=dp(180),
            separator_color=(0.3, 0.3, 0.3, 1),
            title_size=sp(16)
        )
        popup.open()
    
    def _show_popup(self, title, message):
        """显示提示弹窗"""
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=[dp(20), dp(20)]
        )
        
        content.add_widget(Label(text=message, font_size=sp(14), color=(0.3, 0.3, 0.3, 1)))
        
        popup = None
        
        def close_popup(instance):
            popup.dismiss()
        
        close_btn = Button(
            text='知道了',
            size_hint_y=None,
            height=dp(44),
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            background_down=''
        )
        close_btn.bind(on_press=close_popup)
        content.add_widget(close_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, None),
            height=dp(180),
            separator_color=(0.3, 0.3, 0.3, 1),
            title_size=sp(16)
        )
        popup.open()
    
    def on_pre_enter(self, *args):
        """页面进入前刷新数据"""
        self._refresh_records()
    
    def go_back(self, instance):
        """返回主菜单"""
        self.manager.current = 'main'
