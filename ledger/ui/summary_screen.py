# 总结页面 - 支持日/月/年视图切换
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.metrics import dp, sp

from datetime import datetime, timedelta


class SummaryScreen(Screen):
    """总结页面"""
    
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.current_view = 'day'  # day, month, year
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
            text='总 结',
            size_hint_x=0.6,
            font_size=sp(22),
            bold=True,
            color=(0.15, 0.15, 0.15, 1)
        )
        header.add_widget(title_label)
        
        # 导出按钮
        export_btn = Button(
            text='导出',
            size_hint_x=0.2,
            font_size=sp(14),
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            background_down=''
        )
        export_btn.bind(on_press=self._export_data)
        header.add_widget(export_btn)
        
        main_layout.add_widget(header)
        
        # 视图切换按钮
        view_switch = self._create_view_switch()
        main_layout.add_widget(view_switch)
        
        # 日期导航
        nav_bar = self._create_nav_bar()
        main_layout.add_widget(nav_bar)
        
        # 统计摘要
        self.summary_widget = self._create_summary_widget()
        main_layout.add_widget(self.summary_widget)
        
        # 详细内容区域
        scroll_view = ScrollView(
            size_hint=(1, 1),
            bar_width=dp(4),
            scroll_type=['bars', 'content']
        )
        
        self.content_widget = GridLayout(
            cols=1,
            spacing=dp(8),
            padding=[dp(0), dp(4)],
            size_hint_y=None
        )
        self.content_widget.bind(minimum_height=self.content_widget.setter('height'))
        
        scroll_view.add_widget(self.content_widget)
        main_layout.add_widget(scroll_view)
        
        self.add_widget(main_layout)
        self._update_content()
    
    def _create_view_switch(self):
        """创建视图切换按钮"""
        switch = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(44),
            spacing=dp(4),
            padding=[dp(0), dp(0), dp(0), dp(8)]
        )
        
        self.day_btn = Button(
            text='日',
            size_hint_x=0.33,
            font_size=sp(16),
            background_color=(0.15, 0.15, 0.15, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            background_down='',
            bold=True
        )
        self.day_btn.bind(on_press=lambda x: self._switch_view('day'))
        switch.add_widget(self.day_btn)
        
        self.month_btn = Button(
            text='月',
            size_hint_x=0.33,
            font_size=sp(16),
            background_color=(0.35, 0.35, 0.35, 1),
            color=(0.6, 0.6, 0.6, 1),
            background_normal='',
            background_down=''
        )
        self.month_btn.bind(on_press=lambda x: self._switch_view('month'))
        switch.add_widget(self.month_btn)
        
        self.year_btn = Button(
            text='年',
            size_hint_x=0.34,
            font_size=sp(16),
            background_color=(0.35, 0.35, 0.35, 1),
            color=(0.6, 0.6, 0.6, 1),
            background_normal='',
            background_down=''
        )
        self.year_btn.bind(on_press=lambda x: self._switch_view('year'))
        switch.add_widget(self.year_btn)
        
        return switch
    
    def _switch_view(self, view):
        """切换视图"""
        self.current_view = view
        
        # 更新按钮样式
        buttons = {
            'day': self.day_btn,
            'month': self.month_btn,
            'year': self.year_btn
        }
        
        for key, btn in buttons.items():
            if key == view:
                btn.background_color = (0.15, 0.15, 0.15, 1)
                btn.color = (1, 1, 1, 1)
                btn.bold = True
            else:
                btn.background_color = (0.35, 0.35, 0.35, 1)
                btn.color = (0.6, 0.6, 0.6, 1)
                btn.bold = False
        
        # 重置导航日期
        now = datetime.now()
        if view == 'day':
            self.current_date = now.strftime('%Y-%m-%d')
        elif view == 'month':
            self.current_year = now.year
            self.current_month = now.month
        else:
            self.current_year = now.year
        
        # 重新创建导航栏
        self._recreate_nav_bar()
        self._update_content()
    
    def _create_nav_bar(self):
        """创建日期导航栏"""
        nav = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(44),
            spacing=dp(8),
            padding=[dp(8), dp(4)]
        )
        
        prev_btn = Button(
            text='◀',
            size_hint_x=0.15,
            font_size=sp(14),
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            background_down=''
        )
        prev_btn.bind(on_press=self._prev_period)
        nav.add_widget(prev_btn)
        
        self.nav_label = Label(
            text='',
            size_hint_x=0.7,
            font_size=sp(16),
            bold=True,
            color=(0.2, 0.2, 0.2, 1)
        )
        nav.add_widget(self.nav_label)
        
        next_btn = Button(
            text='▶',
            size_hint_x=0.15,
            font_size=sp(14),
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            background_down=''
        )
        next_btn.bind(on_press=self._next_period)
        nav.add_widget(next_btn)
        
        # 初始化日期
        now = datetime.now()
        if self.current_view == 'day':
            self.current_date = now.strftime('%Y-%m-%d')
        elif self.current_view == 'month':
            self.current_year = now.year
            self.current_month = now.month
        else:
            self.current_year = now.year
        
        self._update_nav_label()
        return nav
    
    def _recreate_nav_bar(self):
        """重新创建导航栏"""
        # 移除旧的导航栏
        parent = self.nav_label.parent.parent
        parent.clear_widgets()
        
        # 重新创建
        new_nav = self._create_nav_bar()
        
        # 需要重新构建整个界面...
        # 为简化，直接更新标签
        self._update_nav_label()
    
    def _update_nav_label(self):
        """更新导航标签"""
        if self.current_view == 'day':
            try:
                date_obj = datetime.strptime(self.current_date, '%Y-%m-%d')
                weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][date_obj.weekday()]
                self.nav_label.text = f'{self.current_date} {weekday}'
            except:
                self.nav_label.text = self.current_date
        elif self.current_view == 'month':
            self.nav_label.text = f'{self.current_year}年{self.current_month}月'
        else:
            self.nav_label.text = f'{self.current_year}年'
    
    def _prev_period(self, instance):
        """上一期"""
        if self.current_view == 'day':
            date_obj = datetime.strptime(self.current_date, '%Y-%m-%d')
            date_obj -= timedelta(days=1)
            self.current_date = date_obj.strftime('%Y-%m-%d')
        elif self.current_view == 'month':
            self.current_month -= 1
            if self.current_month < 1:
                self.current_month = 12
                self.current_year -= 1
        else:
            self.current_year -= 1
        
        self._update_nav_label()
        self._update_content()
    
    def _next_period(self, instance):
        """下一期"""
        if self.current_view == 'day':
            date_obj = datetime.strptime(self.current_date, '%Y-%m-%d')
            date_obj += timedelta(days=1)
            self.current_date = date_obj.strftime('%Y-%m-%d')
        elif self.current_view == 'month':
            self.current_month += 1
            if self.current_month > 12:
                self.current_month = 1
                self.current_year += 1
        else:
            self.current_year += 1
        
        self._update_nav_label()
        self._update_content()
    
    def _create_summary_widget(self):
        """创建统计摘要组件"""
        summary = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            spacing=dp(4),
            padding=[dp(12), dp(8)]
        )
        
        # 标题行
        title_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(28))
        title_row.add_widget(Label(
            text='收  入',
            size_hint_x=0.33,
            font_size=sp(12),
            color=(0.5, 0.5, 0.5, 1),
            halign='left'
        ))
        title_row.add_widget(Label(
            text='支  出',
            size_hint_x=0.33,
            font_size=sp(12),
            color=(0.5, 0.5, 0.5, 1)
        ))
        title_row.add_widget(Label(
            text='净 收 入',
            size_hint_x=0.34,
            font_size=sp(12),
            color=(0.5, 0.5, 0.5, 1),
            halign='right'
        ))
        summary.add_widget(title_row)
        
        # 数值行
        self.value_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        self.income_label = Label(
            text='+0.00',
            size_hint_x=0.33,
            font_size=sp(22),
            color=(0.15, 0.65, 0.15, 1),
            bold=True,
            halign='left'
        )
        self.income_label.bind(size=self.income_label.setter('text_size'))
        self.value_row.add_widget(self.income_label)
        
        self.expense_label = Label(
            text='-0.00',
            size_hint_x=0.33,
            font_size=sp(22),
            color=(0.75, 0.15, 0.15, 1),
            bold=True
        )
        self.expense_label.bind(size=self.expense_label.setter('text_size'))
        self.value_row.add_widget(self.expense_label)
        
        self.net_label = Label(
            text='+0.00',
            size_hint_x=0.34,
            font_size=sp(22),
            color=(0.15, 0.65, 0.15, 1),
            bold=True,
            halign='right'
        )
        self.net_label.bind(size=self.net_label.setter('text_size'))
        self.value_row.add_widget(self.net_label)
        
        summary.add_widget(self.value_row)
        
        return summary
    
    def _update_content(self):
        """更新内容"""
        self._update_summary()
        self._update_details()
    
    def _update_summary(self):
        """更新统计摘要"""
        if self.current_view == 'day':
            summary = self.db.get_date_summary(self.current_date)
            income = summary['income']
            expense = summary['expense']
            net = summary['net']
        elif self.current_view == 'month':
            summary = self.db.get_month_summary(self.current_year, self.current_month)
            income = summary['income']
            expense = summary['expense']
            net = summary['net']
        else:
            summary = self.db.get_year_summary(self.current_year)
            income = summary['total_income']
            expense = summary['total_expense']
            net = summary['total_net']
        
        self.income_label.text = f'+{income:.2f}'
        self.expense_label.text = f'-{expense:.2f}'
        
        net_color = (0.15, 0.65, 0.15, 1) if net >= 0 else (0.75, 0.15, 0.15, 1)
        net_prefix = '+' if net >= 0 else ''
        self.net_label.text = f'{net_prefix}{net:.2f}'
        self.net_label.color = net_color
    
    def _update_details(self):
        """更新详细内容"""
        self.content_widget.clear_widgets()
        
        if self.current_view == 'day':
            self._show_day_details()
        elif self.current_view == 'month':
            self._show_month_details()
        else:
            self._show_year_details()
    
    def _show_day_details(self):
        """显示日视图详情"""
        records = self.db.get_records_by_date(self.current_date)
        records.sort(key=lambda r: r['time'])
        
        if not records:
            self.content_widget.add_widget(self._create_empty_label('该日暂无记录'))
            return
        
        # 显示每条记录
        for record in records:
            item = self._create_record_item(record)
            self.content_widget.add_widget(item)
    
    def _show_month_details(self):
        """显示月视图详情"""
        # 按日期分组显示
        dates = self.db.get_monthly_dates(self.current_year, self.current_month)
        
        if not dates:
            self.content_widget.add_widget(self._create_empty_label('该月暂无记录'))
            return
        
        for date in dates:
            date_records = self.db.get_records_by_date(date)
            
            # 日期标题
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][date_obj.weekday()]
                date_title = f'{date} {weekday}'
            except:
                date_title = date
            
            # 日期小计
            income = sum(r['amount'] for r in date_records if r['type'] == 'income')
            expense = sum(r['amount'] for r in date_records if r['type'] == 'expense')
            
            # 日期标题组件
            date_header = self._create_date_header(date_title, income, expense)
            self.content_widget.add_widget(date_header)
            
            # 记录列表
            for record in date_records:
                item = self._create_record_item(record)
                self.content_widget.add_widget(item)
    
    def _show_year_details(self):
        """显示年视图详情"""
        year_summary = self.db.get_year_summary(self.current_year)
        monthly = year_summary['monthly']
        
        has_data = any(m['income'] > 0 or m['expense'] > 0 for m in monthly.values())
        
        if not has_data:
            self.content_widget.add_widget(self._create_empty_label('该年暂无记录'))
            return
        
        # 每月统计
        month_names = ['一月', '二月', '三月', '四月', '五月', '六月',
                       '七月', '八月', '九月', '十月', '十一月', '十二月']
        
        for month in range(1, 13):
            data = monthly[month]
            if data['income'] == 0 and data['expense'] == 0:
                continue
            
            month_item = self._create_month_item(
                month_names[month - 1],
                data['income'],
                data['expense'],
                data['net']
            )
            self.content_widget.add_widget(month_item)
    
    def _create_empty_label(self, text):
        """创建空状态标签"""
        return Label(
            text=text,
            font_size=sp(16),
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None,
            height=dp(80)
        )
    
    def _create_date_header(self, date_text, income, expense):
        """创建日期标题组件"""
        box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(36),
            spacing=dp(8),
            padding=[dp(8), dp(4)]
        )
        
        date_label = Label(
            text=date_text,
            size_hint_x=0.5,
            font_size=sp(13),
            color=(0.3, 0.3, 0.3, 1),
            halign='left',
            bold=True
        )
        date_label.bind(size=date_label.setter('text_size'))
        box.add_widget(date_label)
        
        # 当日小计
        summary_text = f'+{income:.2f} / -{expense:.2f}'
        summary_label = Label(
            text=summary_text,
            size_hint_x=0.5,
            font_size=sp(12),
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
            height=dp(40),
            spacing=dp(8),
            padding=[dp(8), dp(2)]
        )
        
        # 类型标识
        type_icon = Label(
            text='↓' if is_income else '↑',
            size_hint_x=0.08,
            font_size=sp(14),
            color=(0.15, 0.65, 0.15, 1) if is_income else (0.75, 0.15, 0.15, 1),
            bold=True
        )
        box.add_widget(type_icon)
        
        # 来源
        source_label = Label(
            text=record['source'][:12],
            size_hint_x=0.45,
            font_size=sp(14),
            color=(0.25, 0.25, 0.25, 1),
            halign='left'
        )
        source_label.bind(size=source_label.setter('text_size'))
        box.add_widget(source_label)
        
        # 时间
        time_label = Label(
            text=record['time'][:5],
            size_hint_x=0.15,
            font_size=sp(12),
            color=(0.5, 0.5, 0.5, 1)
        )
        box.add_widget(time_label)
        
        # 金额
        amount_prefix = '+' if is_income else '-'
        amount_label = Label(
            text=f'{amount_prefix}{record["amount"]:.2f}',
            size_hint_x=0.32,
            font_size=sp(15),
            color=(0.15, 0.65, 0.15, 1) if is_income else (0.75, 0.15, 0.15, 1),
            bold=True,
            halign='right'
        )
        amount_label.bind(size=amount_label.setter('text_size'))
        box.add_widget(amount_label)
        
        return box
    
    def _create_month_item(self, month_name, income, expense, net):
        """创建月份统计项"""
        box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(80),
            spacing=dp(4),
            padding=[dp(12), dp(8)]
        )
        
        # 月份标题
        title_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(28)
        )
        month_label = Label(
            text=month_name,
            font_size=sp(16),
            color=(0.2, 0.2, 0.2, 1),
            bold=True,
            halign='left'
        )
        month_label.bind(size=month_label.setter('text_size'))
        title_layout.add_widget(month_label)
        box.add_widget(title_layout)
        
        # 统计数据
        data_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(32)
        )
        
        income_box = BoxLayout(orientation='horizontal', size_hint_x=0.33)
        income_label = Label(
            text=f'收: +{income:.2f}',
            font_size=sp(13),
            color=(0.15, 0.65, 0.15, 1)
        )
        income_box.add_widget(income_label)
        data_layout.add_widget(income_box)
        
        expense_box = BoxLayout(orientation='horizontal', size_hint_x=0.33)
        expense_label = Label(
            text=f'支: -{expense:.2f}',
            font_size=sp(13),
            color=(0.75, 0.15, 0.15, 1)
        )
        expense_box.add_widget(expense_label)
        data_layout.add_widget(expense_box)
        
        net_color = (0.15, 0.65, 0.15, 1) if net >= 0 else (0.75, 0.15, 0.15, 1)
        net_box = BoxLayout(orientation='horizontal', size_hint_x=0.34)
        net_label = Label(
            text=f'净: {net:+.2f}',
            font_size=sp(13),
            color=net_color,
            bold=True
        )
        net_box.add_widget(net_label)
        data_layout.add_widget(net_box)
        
        box.add_widget(data_layout)
        return box
    
    def _export_data(self, instance):
        """导出数据为CSV"""
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=[dp(20), dp(20)]
        )
        
        content.add_widget(Label(
            text='导出数据为CSV文件',
            font_size=sp(16),
            color=(0.3, 0.3, 0.3, 1)
        ))
        
        content.add_widget(Label(
            text=f'数据将保存到:\n{self.db.csv_file}',
            font_size=sp(13),
            color=(0.5, 0.5, 0.5, 1)
        ))
        
        btn_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(44),
            spacing=dp(10),
            padding=[dp(0), dp(10)]
        )
        
        popup = None
        
        def do_export(instance):
            success = self.db.export_csv(self.db.csv_file)
            popup.dismiss()
            
            if success:
                self._show_message('导出成功', f'数据已导出到:\n{self.db.csv_file}')
            else:
                self._show_message('导出失败', '导出过程中出现错误')
        
        def cancel_export(instance):
            popup.dismiss()
        
        export_btn = Button(
            text='导出',
            size_hint_x=0.5,
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            background_down=''
        )
        export_btn.bind(on_press=do_export)
        
        cancel_btn = Button(
            text='取消',
            size_hint_x=0.5,
            background_color=(0.5, 0.5, 0.5, 1),
            color=(1, 1, 1, 1),
            background_normal='',
            background_down=''
        )
        cancel_btn.bind(on_press=cancel_export)
        
        btn_layout.add_widget(export_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='导出数据',
            content=content,
            size_hint=(0.85, None),
            height=dp(220),
            separator_color=(0.3, 0.3, 0.3, 1),
            title_size=sp(16)
        )
        popup.open()
    
    def _show_message(self, title, message):
        """显示消息弹窗"""
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=[dp(20), dp(20)]
        )
        
        content.add_widget(Label(
            text=message,
            font_size=sp(14),
            color=(0.3, 0.3, 0.3, 1)
        ))
        
        popup = None
        
        def close_popup(instance):
            popup.dismiss()
        
        close_btn = Button(
            text='确定',
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
        self._update_content()
    
    def go_back(self, instance):
        """返回主菜单"""
        self.manager.current = 'main'
