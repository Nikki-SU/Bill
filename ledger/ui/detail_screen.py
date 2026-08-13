# 明细页面 - 展示所有记录详情
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.metrics import dp, sp

from datetime import datetime


class DetailScreen(Screen):
    """明细页面"""
    
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
            text='明 细',
            size_hint_x=0.6,
            font_size=sp(22),
            bold=True,
            color=(0.15, 0.15, 0.15, 1)
        )
        header.add_widget(title_label)
        
        # 统计概览
        stats_btn = Button(
            text='统计',
            size_hint_x=0.2,
            font_size=sp(14),
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            background_down=''
        )
        stats_btn.bind(on_press=self._show_statistics)
        header.add_widget(stats_btn)
        
        main_layout.add_widget(header)
        
        # 月度过滤器
        filter_bar = self._create_filter_bar()
        main_layout.add_widget(filter_bar)
        
        # 汇总信息
        self.summary_bar = self._create_summary_bar()
        main_layout.add_widget(self.summary_bar)
        
        # 明细列表（滚动）
        scroll_view = ScrollView(
            size_hint=(1, 1),
            bar_width=dp(4),
            scroll_type=['bars', 'content']
        )
        
        self.detail_list = GridLayout(
            cols=1,
            spacing=dp(4),
            padding=[dp(0), dp(4)],
            size_hint_y=None
        )
        self.detail_list.bind(minimum_height=self.detail_list.setter('height'))
        
        scroll_view.add_widget(self.detail_list)
        main_layout.add_widget(scroll_view)
        
        self.add_widget(main_layout)
        self._refresh_details()
    
    def _create_filter_bar(self):
        """创建过滤栏"""
        bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(44),
            spacing=dp(8),
            padding=[dp(8), dp(4)]
        )
        
        # 获取年月列表
        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month
        
        prev_btn = Button(
            text='◀',
            size_hint_x=0.12,
            font_size=sp(14),
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            background_down=''
        )
        prev_btn.bind(on_press=self._prev_month)
        bar.add_widget(prev_btn)
        
        self.month_label = Label(
            text=f'{self.current_year}年{self.current_month}月',
            size_hint_x=0.55,
            font_size=sp(16),
            bold=True,
            color=(0.2, 0.2, 0.2, 1)
        )
        bar.add_widget(self.month_label)
        
        next_btn = Button(
            text='▶',
            size_hint_x=0.12,
            font_size=sp(14),
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            background_down=''
        )
        next_btn.bind(on_press=self._next_month)
        bar.add_widget(next_btn)
        
        # 显示全部按钮
        self.all_btn = Button(
            text='全部',
            size_hint_x=0.21,
            font_size=sp(14),
            background_color=(0.15, 0.15, 0.15, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            background_down='',
            bold=True
        )
        self.all_btn.bind(on_press=self._show_all)
        bar.add_widget(self.all_btn)
        
        self.show_all = False
        return bar
    
    def _prev_month(self, instance):
        """上一月"""
        self.show_all = False
        self.all_btn.background_color = (0.35, 0.35, 0.35, 1)
        self.all_btn.color = (0.6, 0.6, 0.6, 1)
        self.all_btn.bold = False
        
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        
        self.month_label.text = f'{self.current_year}年{self.current_month}月'
        self._refresh_details()
    
    def _next_month(self, instance):
        """下一月"""
        self.show_all = False
        self.all_btn.background_color = (0.35, 0.35, 0.35, 1)
        self.all_btn.color = (0.6, 0.6, 0.6, 1)
        self.all_btn.bold = False
        
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        
        self.month_label.text = f'{self.current_year}年{self.current_month}月'
        self._refresh_details()
    
    def _show_all(self, instance):
        """显示全部"""
        self.show_all = True
        self.all_btn.background_color = (0.15, 0.15, 0.15, 1)
        self.all_btn.color = (1, 1, 1, 1)
        self.all_btn.bold = True
        self.month_label.text = '全部记录'
        self._refresh_details()
    
    def _create_summary_bar(self):
        """创建月度摘要栏"""
        bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(8),
            padding=[dp(12), dp(6)]
        )
        
        # 收入
        income_box = BoxLayout(orientation='vertical', size_hint_x=0.33)
        income_title = Label(
            text='收入',
            font_size=sp(11),
            color=(0.5, 0.5, 0.5, 1)
        )
        self.income_value = Label(
            text='+0.00',
            font_size=sp(16),
            color=(0.15, 0.65, 0.15, 1),
            bold=True
        )
        income_box.add_widget(income_title)
        income_box.add_widget(self.income_value)
        bar.add_widget(income_box)
        
        # 支出
        expense_box = BoxLayout(orientation='vertical', size_hint_x=0.33)
        expense_title = Label(
            text='支出',
            font_size=sp(11),
            color=(0.5, 0.5, 0.5, 1)
        )
        self.expense_value = Label(
            text='-0.00',
            font_size=sp(16),
            color=(0.75, 0.15, 0.15, 1),
            bold=True
        )
        expense_box.add_widget(expense_title)
        expense_box.add_widget(self.expense_value)
        bar.add_widget(expense_box)
        
        # 净收入
        net_box = BoxLayout(orientation='vertical', size_hint_x=0.34)
        net_title = Label(
            text='净收入',
            font_size=sp(11),
            color=(0.5, 0.5, 0.5, 1)
        )
        self.net_value = Label(
            text='+0.00',
            font_size=sp(16),
            color=(0.15, 0.65, 0.15, 1),
            bold=True
        )
        net_box.add_widget(net_title)
        net_box.add_widget(self.net_value)
        bar.add_widget(net_box)
        
        return bar
    
    def _refresh_details(self):
        """刷新明细列表"""
        self.detail_list.clear_widgets()
        
        # 获取记录
        if self.show_all:
            records = self.db.get_all_records()
        else:
            records = self.db.get_records_by_month(self.current_year, self.current_month)
            records.sort(key=lambda r: (r['date'], r['time']), reverse=True)
        
        # 更新摘要
        if self.show_all:
            all_records = self.db.get_all_records()
            income = sum(r['amount'] for r in all_records if r['type'] == 'income')
            expense = sum(r['amount'] for r in all_records if r['type'] == 'expense')
        else:
            income = sum(r['amount'] for r in records if r['type'] == 'income')
            expense = sum(r['amount'] for r in records if r['type'] == 'expense')
        
        net = income - expense
        self.income_value.text = f'+{income:.2f}'
        self.expense_value.text = f'-{expense:.2f}'
        
        net_color = (0.15, 0.65, 0.15, 1) if net >= 0 else (0.75, 0.15, 0.15, 1)
        net_prefix = '+' if net >= 0 else ''
        self.net_value.text = f'{net_prefix}{net:.2f}'
        self.net_value.color = net_color
        
        if not records:
            self.detail_list.add_widget(Label(
                text='暂无记录',
                font_size=sp(16),
                color=(0.6, 0.6, 0.6, 1),
                size_hint_y=None,
                height=dp(80)
            ))
            return
        
        # 按日期分组
        grouped = self._group_by_date(records)
        
        for date, day_records in grouped.items():
            # 日期标题（包含当日小结）
            date_summary = self.db.get_date_summary(date)
            date_header = self._create_date_header(date, date_summary)
            self.detail_list.add_widget(date_header)
            
            # 记录列表
            for record in day_records:
                item = self._create_record_item(record)
                self.detail_list.add_widget(item)
    
    def _group_by_date(self, records):
        """按日期分组"""
        grouped = {}
        for record in records:
            date = record['date']
            if date not in grouped:
                grouped[date] = []
            grouped[date].append(record)
        
        # 按日期降序排序
        sorted_grouped = dict(sorted(grouped.items(), reverse=True))
        
        # 每个日期内按时间降序
        for date in sorted_grouped:
            sorted_grouped[date].sort(key=lambda r: r['time'], reverse=True)
        
        return sorted_grouped
    
    def _create_date_header(self, date, summary):
        """创建日期标题"""
        box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(38),
            spacing=dp(8),
            padding=[dp(10), dp(4)]
        )
        
        # 日期
        date_label = Label(
            text=date,
            size_hint_x=0.35,
            font_size=sp(13),
            color=(0.3, 0.3, 0.3, 1),
            halign='left',
            bold=True
        )
        date_label.bind(size=date_label.setter('text_size'))
        box.add_widget(date_label)
        
        # 星期几
        weekday_label = Label(
            text=summary['weekday'],
            size_hint_x=0.2,
            font_size=sp(12),
            color=(0.5, 0.5, 0.5, 1)
        )
        box.add_widget(weekday_label)
        
        # 当日小结
        summary_text = f'收+{summary["income"]:.2f} 支-{summary["expense"]:.2f}'
        summary_label = Label(
            text=summary_text,
            size_hint_x=0.45,
            font_size=sp(11),
            color=(0.5, 0.5, 0.5, 1),
            halign='right'
        )
        summary_label.bind(size=summary_label.setter('text_size'))
        box.add_widget(summary_label)
        
        return box
    
    def _create_record_item(self, record):
        """创建记录项"""
        is_income = record['type'] == 'income'
        
        box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(44),
            spacing=dp(6),
            padding=[dp(10), dp(2)]
        )
        
        # 类型图标
        type_icon = Label(
            text='↓' if is_income else '↑',
            size_hint_x=0.06,
            font_size=sp(12),
            color=(0.15, 0.65, 0.15, 1) if is_income else (0.75, 0.15, 0.15, 1),
            bold=True
        )
        box.add_widget(type_icon)
        
        # 来源/物品
        source_label = Label(
            text=record['source'][:14],
            size_hint_x=0.40,
            font_size=sp(14),
            color=(0.25, 0.25, 0.25, 1),
            halign='left'
        )
        source_label.bind(size=source_label.setter('text_size'))
        box.add_widget(source_label)
        
        # 时间
        time_label = Label(
            text=record['time'][:5],
            size_hint_x=0.12,
            font_size=sp(12),
            color=(0.5, 0.5, 0.5, 1)
        )
        box.add_widget(time_label)
        
        # 金额
        amount_prefix = '+' if is_income else '-'
        amount_label = Label(
            text=f'{amount_prefix}{record["amount"]:.2f}',
            size_hint_x=0.28,
            font_size=sp(15),
            color=(0.15, 0.65, 0.15, 1) if is_income else (0.75, 0.15, 0.15, 1),
            bold=True,
            halign='right'
        )
        amount_label.bind(size=amount_label.setter('text_size'))
        box.add_widget(amount_label)
        
        # 操作按钮
        action_layout = BoxLayout(
            orientation='horizontal',
            size_hint_x=0.14,
            spacing=dp(4)
        )
        
        edit_btn = Button(
            text='✎',
            size_hint_x=0.5,
            font_size=sp(12),
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            background_down=''
        )
        edit_btn.bind(on_press=lambda x, rid=record['id']: self._on_edit(rid))
        action_layout.add_widget(edit_btn)
        
        delete_btn = Button(
            text='×',
            size_hint_x=0.5,
            font_size=sp(14),
            background_color=(0.5, 0.1, 0.1, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            background_down=''
        )
        delete_btn.bind(on_press=lambda x, rid=record['id']: self._on_delete(rid))
        action_layout.add_widget(delete_btn)
        
        box.add_widget(action_layout)
        return box
    
    def _on_edit(self, record_id):
        """编辑记录"""
        record = None
        for r in self.db.records:
            if r['id'] == record_id:
                record = r
                break
        
        if not record:
            return
        
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(20), dp(20)]
        )
        
        content.add_widget(Label(text='来源/物品:', font_size=sp(14), color=(0.3, 0.3, 0.3, 1)))
        source_input = self._create_text_input(record['source'])
        content.add_widget(source_input)
        
        content.add_widget(Label(text='金额:', font_size=sp(14), color=(0.3, 0.3, 0.3, 1)))
        amount_input = self._create_text_input(str(record['amount']), is_float=True)
        content.add_widget(amount_input)
        
        # 类型显示
        type_text = '收入' if record['type'] == 'income' else '支出'
        type_color = (0.15, 0.65, 0.15, 1) if record['type'] == 'income' else (0.75, 0.15, 0.15, 1)
        content.add_widget(Label(text=f'类型: {type_text}', font_size=sp(14), color=type_color, bold=True))
        
        btn_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(44),
            spacing=dp(10),
            padding=[dp(0), dp(10)]
        )
        
        popup = None
        
        def save_edit(instance):
            new_source = source_input.text.strip()
            new_amount = amount_input.text.strip()
            
            if not new_source:
                self._show_alert('提示', '请输入来源/物品名称')
                return
            
            try:
                new_amount = float(new_amount)
                if new_amount <= 0:
                    self._show_alert('提示', '金额必须大于0')
                    return
            except ValueError:
                self._show_alert('提示', '金额格式错误')
                return
            
            self.db.update_record(record_id, source=new_source, amount=new_amount)
            popup.dismiss()
            self._refresh_details()
        
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
            height=dp(320),
            separator_color=(0.3, 0.3, 0.3, 1),
            title_size=sp(16)
        )
        popup.open()
    
    def _on_delete(self, record_id):
        """删除记录"""
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=[dp(20), dp(20)]
        )
        
        content.add_widget(Label(
            text='确定要删除这条记录吗？',
            font_size=sp(16),
            color=(0.3, 0.3, 0.3, 1)
        ))
        
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
            self._refresh_details()
        
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
    
    def _show_statistics(self, instance):
        """显示统计信息"""
        stats = self.db.get_statistics()
        
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=[dp(20), dp(20)]
        )
        
        content.add_widget(Label(text='数据统计', font_size=sp(18), bold=True, color=(0.2, 0.2, 0.2, 1)))
        content.add_widget(Label(text='', size_hint_y=None, height=dp(10)))
        
        stats_text = f'''总记录数: {stats['total_records']}
总收入: +{stats['total_income']:.2f}
总支出: -{stats['total_expense']:.2f}
净收入: {stats['total_net']:+.2f}'''
        
        content.add_widget(Label(
            text=stats_text,
            font_size=sp(15),
            color=(0.3, 0.3, 0.3, 1),
            halign='left',
            text_size=(dp(250), None)
        ))
        
        content.add_widget(Label(text='', size_hint_y=None, height=dp(10)))
        content.add_widget(Label(text=f'数据文件:\n{self.db.csv_file}', font_size=sp(12), color=(0.5, 0.5, 0.5, 1)))
        
        popup = None
        
        def close_popup(instance):
            popup.dismiss()
        
        close_btn = Button(
            text='关闭',
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
            title='统计信息',
            content=content,
            size_hint=(0.85, None),
            height=dp(300),
            separator_color=(0.3, 0.3, 0.3, 1),
            title_size=sp(16)
        )
        popup.open()
    
    def _create_text_input(self, text, is_float=False):
        """创建文本输入框"""
        from kivy.uix.textinput import TextInput
        return TextInput(
            text=text,
            font_size=sp(14),
            size_hint_y=None,
            height=dp(44),
            padding=[dp(10), dp(12)],
            multiline=False,
            input_filter='float' if is_float else None
        )
    
    def _show_alert(self, title, message):
        """显示警告"""
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
        self._refresh_details()
    
    def go_back(self, instance):
        """返回主菜单"""
        self.manager.current = 'main'
