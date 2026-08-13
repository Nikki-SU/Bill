#!/usr/bin/env python3
"""
账本 - 本地记账应用 (Tkinter 版本)
极简黑白灰风格
"""

import os
import sys
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime, timedelta
from collections import defaultdict


class Database:
    """CSV数据库管理"""
    
    def __init__(self):
        self.data_dir = self._get_data_dir()
        self.csv_file = os.path.join(self.data_dir, 'records.csv')
        self.records = []
        self._ensure_data_dir()
        self._load_records()
    
    def _get_data_dir(self):
        return os.path.join(os.path.expanduser('~'), '.ledger_data')
    
    def _ensure_data_dir(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _load_records(self):
        self.records = []
        if os.path.exists(self.csv_file):
            try:
                with open(self.csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        record = {
                            'id': int(row['id']),
                            'date': row['date'],
                            'time': row['time'],
                            'source': row['source'],
                            'amount': float(row['amount']),
                            'type': row['type'],
                            'checked': row.get('checked', 'false') == 'true'
                        }
                        self.records.append(record)
            except Exception as e:
                print(f"加载数据失败: {e}")
    
    def _save_records(self):
        try:
            fieldnames = ['id', 'date', 'time', 'source', 'amount', 'type', 'checked']
            with open(self.csv_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for record in self.records:
                    row = record.copy()
                    row['checked'] = 'true' if record['checked'] else 'false'
                    writer.writerow(row)
        except Exception as e:
            print(f"保存数据失败: {e}")
    
    def reload(self):
        self._load_records()
    
    def _get_next_id(self):
        if self.records:
            return max(r['id'] for r in self.records) + 1
        return 1
    
    def add_record(self, source, amount, record_type, checked=False):
        now = datetime.now()
        record = {
            'id': self._get_next_id(),
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M:%S'),
            'source': source,
            'amount': float(amount),
            'type': record_type,
            'checked': checked
        }
        self.records.append(record)
        self._save_records()
        return record['id']
    
    def update_record(self, record_id, **kwargs):
        for record in self.records:
            if record['id'] == record_id:
                for key, value in kwargs.items():
                    if key in record:
                        if key == 'checked':
                            record['checked'] = value if isinstance(value, bool) else value == 'true'
                        elif key == 'amount':
                            record['amount'] = float(value)
                        else:
                            record[key] = value
                self._save_records()
                return True
        return False
    
    def delete_record(self, record_id):
        self.records = [r for r in self.records if r['id'] != record_id]
        self._save_records()
    
    def toggle_checked(self, record_id):
        for record in self.records:
            if record['id'] == record_id:
                record['checked'] = not record['checked']
                self._save_records()
                return True
        return False
    
    def get_all_records(self):
        return sorted(self.records, key=lambda r: (r['date'], r['time']), reverse=True)
    
    def get_records_by_date(self, date_str):
        return [r for r in self.records if r['date'] == date_str]
    
    def get_records_by_month(self, year, month):
        month_str = f'{year}-{month:02d}'
        return [r for r in self.records if r['date'].startswith(month_str)]
    
    def get_today_records(self):
        today = datetime.now().strftime('%Y-%m-%d')
        return self.get_records_by_date(today)
    
    def get_today_summary(self):
        today_records = self.get_today_records()
        income = sum(r['amount'] for r in today_records if r['type'] == 'income')
        expense = sum(r['amount'] for r in today_records if r['type'] == 'expense')
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'weekday': ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][datetime.now().weekday()],
            'income': income,
            'expense': expense,
            'net': income - expense
        }
    
    def get_month_summary(self, year=None, month=None):
        now = datetime.now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month
        
        month_records = self.get_records_by_month(year, month)
        income = sum(r['amount'] for r in month_records if r['type'] == 'income')
        expense = sum(r['amount'] for r in month_records if r['type'] == 'expense')
        
        return {
            'year': year,
            'month': month,
            'income': income,
            'expense': expense,
            'net': income - expense
        }
    
    def get_year_summary(self, year=None):
        if year is None:
            year = datetime.now().year
        
        year_records = self.get_records_by_year(year)
        income = sum(r['amount'] for r in year_records if r['type'] == 'income')
        expense = sum(r['amount'] for r in year_records if r['type'] == 'expense')
        
        monthly = {}
        for month in range(1, 13):
            month_records = self.get_records_by_month(year, month)
            m_income = sum(r['amount'] for r in month_records if r['type'] == 'income')
            m_expense = sum(r['amount'] for r in month_records if r['type'] == 'expense')
            monthly[month] = {
                'income': m_income,
                'expense': m_expense,
                'net': m_income - m_expense
            }
        
        return {
            'year': year,
            'total_income': income,
            'total_expense': expense,
            'total_net': income - expense,
            'monthly': monthly
        }
    
    def get_records_by_year(self, year):
        year_str = f'{year}'
        return [r for r in self.records if r['date'].startswith(year_str)]
    
    def get_date_summary(self, date_str):
        records = self.get_records_by_date(date_str)
        income = sum(r['amount'] for r in records if r['type'] == 'income')
        expense = sum(r['amount'] for r in records if r['type'] == 'expense')
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][date_obj.weekday()]
        except:
            weekday = ''
        
        return {
            'date': date_str,
            'weekday': weekday,
            'income': income,
            'expense': expense,
            'net': income - expense,
            'count': len(records)
        }
    
    def get_all_dates_sorted(self):
        dates = set(r['date'] for r in self.records)
        return sorted(list(dates), reverse=True)
    
    def export_csv(self, filepath):
        try:
            fieldnames = ['id', 'date', 'time', 'source', 'amount', 'type', 'checked']
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for record in self.records:
                    row = record.copy()
                    row['checked'] = 'true' if record['checked'] else 'false'
                    writer.writerow(row)
            return True
        except Exception as e:
            print(f"导出失败: {e}")
            return False
    
    def get_statistics(self):
        return {
            'total_records': len(self.records),
            'total_income': sum(r['amount'] for r in self.records if r['type'] == 'income'),
            'total_expense': sum(r['amount'] for r in self.records if r['type'] == 'expense'),
            'total_net': sum(
                r['amount'] if r['type'] == 'income' else -r['amount']
                for r in self.records
            )
        }


# ==================== UI 部分 ====================

# 颜色常量 - 极简黑白灰风格
COLORS = {
    'bg': '#f5f5f5',
    'fg': '#1a1a1a',
    'fg_muted': '#666666',
    'accent': '#333333',
    'accent_2': '#555555',
    'income': '#1f7a1f',  # 深绿
    'expense': '#c72c2c',  # 深红
    'border': '#dddddd',
    'card': '#ffffff',
    'highlight': '#e8e8e8',
}

WEEKDAYS = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']


class LedgerApp:
    """主应用类"""
    
    def __init__(self):
        self.db = Database()
        self.current_frame = None
        self.root = tk.Tk()
        self.root.title('账本')
        self.root.configure(bg=COLORS['bg'])
        
        # 响应式尺寸
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # 设置初始窗口大小（竖屏比例）
        win_w = min(400, self.screen_width)
        win_h = min(700, self.screen_height)
        self.root.geometry(f'{win_w}x{win_h}')
        self.root.minsize(320, 560)
        
        # 容器
        self.container = tk.Frame(self.root, bg=COLORS['bg'])
        self.container.pack(fill='both', expand=True)
        
        self.show_main()
    
    def run(self):
        self.root.mainloop()
    
    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()
    
    def show_main(self):
        """显示主菜单"""
        self.clear_container()
        
        # 标题
        title = tk.Label(
            self.container, text='账本',
            font=('Microsoft YaHei', 36, 'bold'),
            bg=COLORS['bg'], fg=COLORS['fg']
        )
        title.pack(pady=(60, 40))
        
        # 按钮
        btn_config = {
            'font': ('Microsoft YaHei', 16),
            'width': 18,
            'height': 2,
            'border': 'none',
            'cursor': 'hand2',
        }
        
        btn_record = tk.Button(
            self.container, text='记账',
            bg=COLORS['fg'], fg='white',
            activebackground=COLORS['accent'],
            command=self.show_record,
            **btn_config
        )
        btn_record.pack(pady=12)
        
        btn_summary = tk.Button(
            self.container, text='总结',
            bg=COLORS['accent'], fg='white',
            activebackground=COLORS['accent_2'],
            command=self.show_summary,
            **btn_config
        )
        btn_summary.pack(pady=12)
        
        btn_detail = tk.Button(
            self.container, text='明细',
            bg=COLORS['accent_2'], fg='white',
            activebackground=COLORS['fg_muted'],
            command=self.show_detail,
            **btn_config
        )
        btn_detail.pack(pady=12)
        
        # 版本信息
        version = tk.Label(
            self.container, text='v1.0 本地记账',
            font=('Microsoft YaHei', 9),
            bg=COLORS['bg'], fg=COLORS['fg_muted']
        )
        version.pack(side='bottom', pady=20)
    
    def show_record(self):
        """显示记账页面"""
        self.clear_container()
        
        # 顶部导航
        nav_frame = tk.Frame(self.container, bg=COLORS['bg'])
        nav_frame.pack(fill='x', padx=10, pady=10)
        
        btn_back = tk.Button(
            nav_frame, text='← 返回',
            font=('Microsoft YaHei', 12),
            bg=COLORS['accent'], fg='white',
            relief='flat', cursor='hand2',
            command=self.show_main
        )
        btn_back.pack(side='left')
        
        title = tk.Label(
            nav_frame, text='记 账',
            font=('Microsoft YaHei', 18, 'bold'),
            bg=COLORS['bg'], fg=COLORS['fg']
        )
        title.pack(side='left', expand=True)
        
        # 日期显示
        now = datetime.now()
        date_text = f"{now.strftime('%Y/%m/%d')} {WEEKDAYS[now.weekday()]}"
        date_label = tk.Label(
            nav_frame, text=date_text,
            font=('Microsoft YaHei', 9),
            bg=COLORS['bg'], fg=COLORS['fg_muted']
        )
        date_label.pack(side='right')
        
        # 统计栏
        summary_frame = self._create_summary_bar(self.container)
        summary_frame.pack(fill='x', padx=10, pady=5)
        
        # 输入区域
        input_frame = self._create_input_area(self.container)
        input_frame.pack(fill='x', padx=10, pady=5)
        
        # 记录列表（Canvas + Scrollbar）
        list_container = tk.Frame(self.container, bg=COLORS['bg'])
        list_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(list_container, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient='vertical', command=canvas.yview)
        self.record_list_frame = tk.Frame(canvas, bg=COLORS['bg'])
        
        self.record_list_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=self.record_list_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self._refresh_records()
    
    def _create_summary_bar(self, parent):
        """创建统计栏"""
        now = datetime.now()
        today_records = self.db.get_records_by_date(now.strftime('%Y-%m-%d'))
        
        income = sum(r['amount'] for r in today_records if r['type'] == 'income')
        expense = sum(r['amount'] for r in today_records if r['type'] == 'expense')
        net = income - expense
        
        frame = tk.Frame(parent, bg=COLORS['card'], highlightbackground=COLORS['border'], highlightthickness=1)
        frame.pack_propagate(False)
        frame.config(height=60)
        
        # 收入
        income_frame = tk.Frame(frame, bg=COLORS['card'])
        income_frame.pack(side='left', expand=True, fill='both', padx=10, pady=5)
        
        tk.Label(income_frame, text='收入', font=('Microsoft YaHei', 9), bg=COLORS['card'], fg=COLORS['fg_muted']).pack()
        tk.Label(income_frame, text=f'+{income:.2f}', font=('Microsoft YaHei', 14, 'bold'), bg=COLORS['card'], fg=COLORS['income']).pack()
        
        # 支出
        expense_frame = tk.Frame(frame, bg=COLORS['card'])
        expense_frame.pack(side='left', expand=True, fill='both', padx=10, pady=5)
        
        tk.Label(expense_frame, text='支出', font=('Microsoft YaHei', 9), bg=COLORS['card'], fg=COLORS['fg_muted']).pack()
        tk.Label(expense_frame, text=f'-{expense:.2f}', font=('Microsoft YaHei', 14, 'bold'), bg=COLORS['card'], fg=COLORS['expense']).pack()
        
        # 结余
        net_frame = tk.Frame(frame, bg=COLORS['card'])
        net_frame.pack(side='left', expand=True, fill='both', padx=10, pady=5)
        
        tk.Label(net_frame, text='结余', font=('Microsoft YaHei', 9), bg=COLORS['card'], fg=COLORS['fg_muted']).pack()
        net_color = COLORS['income'] if net >= 0 else COLORS['expense']
        tk.Label(net_frame, text=f'{net:+.2f}', font=('Microsoft YaHei', 14, 'bold'), bg=COLORS['card'], fg=net_color).pack()
        
        return frame
    
    def _create_input_area(self, parent):
        """创建输入区域"""
        frame = tk.Frame(parent, bg=COLORS['bg'])
        
        # 类型切换
        self.current_type = 'expense'
        
        type_frame = tk.Frame(frame, bg=COLORS['bg'])
        type_frame.pack(fill='x', pady=(0, 8))
        
        self.btn_income_type = tk.Button(
            type_frame, text='收入',
            font=('Microsoft YaHei', 11),
            bg=COLORS['expense'], fg='white',
            relief='flat', cursor='hand2',
            command=lambda: self._set_type('income')
        )
        self.btn_income_type.pack(side='left', expand=True, fill='x', padx=(0, 4))
        
        self.btn_expense_type = tk.Button(
            type_frame, text='支出',
            font=('Microsoft YaHei', 11),
            bg=COLORS['fg'], fg='white',
            relief='flat', cursor='hand2',
            command=lambda: self._set_type('expense')
        )
        self.btn_expense_type.pack(side='left', expand=True, fill='x', padx=(4, 0))
        
        # 输入框
        input_frame = tk.Frame(frame, bg=COLORS['bg'])
        input_frame.pack(fill='x')
        
        self.source_entry = tk.Entry(
            input_frame, font=('Microsoft YaHei', 12),
            bg=COLORS['card'], fg=COLORS['fg'],
            relief='solid', bd=1
        )
        self.source_entry.pack(side='left', expand=True, fill='x', padx=(0, 4), ipady=5)
        self.source_entry.insert(0, '物品/来源')
        self.source_entry.bind('<FocusIn>', lambda e: self.source_entry.delete(0, 'end') if self.source_entry.get() == '物品/来源' else None)
        
        self.amount_entry = tk.Entry(
            input_frame, font=('Microsoft YaHei', 12),
            bg=COLORS['card'], fg=COLORS['fg'],
            relief='solid', bd=1, width=8
        )
        self.amount_entry.pack(side='left', padx=(0, 4), ipady=5)
        self.amount_entry.insert(0, '金额')
        self.amount_entry.bind('<FocusIn>', lambda e: self.amount_entry.delete(0, 'end') if self.amount_entry.get() == '金额' else None)
        
        btn_add = tk.Button(
            input_frame, text='+',
            font=('Microsoft YaHei', 16, 'bold'),
            bg=COLORS['fg'], fg='white',
            relief='flat', cursor='hand2',
            width=2, command=self._add_record
        )
        btn_add.pack(side='left')
        
        return frame
    
    def _set_type(self, record_type):
        self.current_type = record_type
        if record_type == 'income':
            self.btn_income_type.config(bg=COLORS['income'])
            self.btn_expense_type.config(bg=COLORS['accent_2'])
        else:
            self.btn_expense_type.config(bg=COLORS['expense'])
            self.btn_income_type.config(bg=COLORS['accent_2'])
    
    def _add_record(self):
        source = self.source_entry.get().strip()
        amount_text = self.amount_entry.get().strip()
        
        if not source or source == '物品/来源':
            messagebox.showwarning('提示', '请输入物品/来源名称')
            return
        if not amount_text or amount_text == '金额':
            messagebox.showwarning('提示', '请输入金额')
            return
        
        try:
            amount = float(amount_text)
            if amount <= 0:
                messagebox.showwarning('提示', '金额必须大于0')
                return
        except ValueError:
            messagebox.showwarning('提示', '金额格式错误')
            return
        
        self.db.add_record(source, amount, self.current_type)
        
        self.source_entry.delete(0, 'end')
        self.source_entry.insert(0, '物品/来源')
        self.amount_entry.delete(0, 'end')
        self.amount_entry.insert(0, '金额')
        
        self._refresh_records()
    
    def _refresh_records(self):
        """刷新记录列表"""
        # 重新创建统计栏
        for widget in self.container.winfo_children():
            if isinstance(widget, tk.Frame) and widget != self.container.winfo_children()[0]:
                if hasattr(self, '_summary_frame_ref'):
                    break
        
        # 刷新统计
        now = datetime.now()
        today_records = self.db.get_records_by_date(now.strftime('%Y-%m-%d'))
        income = sum(r['amount'] for r in today_records if r['type'] == 'income')
        expense = sum(r['amount'] for r in today_records if r['type'] == 'expense')
        net = income - expense
        
        # 更新统计显示（简单方式：重新创建整个页面会更复杂，这里用全局更新）
        # 简化处理：重新渲染列表
        self._render_record_list(today_records)
    
    def _render_record_list(self, records):
        """渲染记录列表"""
        for widget in self.record_list_frame.winfo_children():
            widget.destroy()
        
        if not records:
            empty_label = tk.Label(
                self.record_list_frame, text='今日暂无记录',
                font=('Microsoft YaHei', 12),
                bg=COLORS['bg'], fg=COLORS['fg_muted']
            )
            empty_label.pack(pady=30)
            return
        
        records = sorted(records, key=lambda r: r['time'], reverse=True)
        
        for record in records:
            item_frame = self._create_record_item(record)
            item_frame.pack(fill='x', pady=2, padx=5)
    
    def _create_record_item(self, record):
        """创建单条记录项"""
        is_income = record['type'] == 'income'
        amount_color = COLORS['income'] if is_income else COLORS['expense']
        type_bg = COLORS['income'] if is_income else COLORS['expense']
        
        frame = tk.Frame(
            self.record_list_frame,
            bg=COLORS['card'],
            highlightbackground=COLORS['border'],
            highlightthickness=1
        )
        
        # 打勾按钮
        check_text = '✓' if record['checked'] else '○'
        check_bg = type_bg if record['checked'] else COLORS['highlight']
        
        btn_check = tk.Button(
            frame, text=check_text,
            font=('Microsoft YaHei', 12, 'bold'),
            bg=check_bg,
            fg='white' if record['checked'] else COLORS['fg_muted'],
            relief='flat', cursor='hand2',
            width=3, command=lambda: self._toggle_record(record['id'])
        )
        btn_check.pack(side='left', padx=5, pady=8)
        
        # 来源
        source_label = tk.Label(
            frame, text=record['source'][:12],
            font=('Microsoft YaHei', 11, 'bold' if record['checked'] else 'normal'),
            bg=COLORS['card'], fg=COLORS['fg']
        )
        source_label.pack(side='left', expand=True, fill='x', padx=5)
        
        # 时间
        time_label = tk.Label(
            frame, text=record['time'][:5],
            font=('Microsoft YaHei', 9),
            bg=COLORS['card'], fg=COLORS['fg_muted']
        )
        time_label.pack(side='left', padx=5)
        
        # 金额
        amount_prefix = '+' if is_income else '-'
        amount_label = tk.Label(
            frame, text=f'{amount_prefix}{record["amount"]:.2f}',
            font=('Microsoft YaHei', 12, 'bold'),
            bg=COLORS['card'], fg=amount_color
        )
        amount_label.pack(side='left', padx=5)
        
        # 编辑按钮
        btn_edit = tk.Button(
            frame, text='✎',
            font=('Microsoft YaHei', 10),
            bg=COLORS['accent'], fg='white',
            relief='flat', cursor='hand2',
            width=2, command=lambda: self._edit_record(record['id'])
        )
        btn_edit.pack(side='left', padx=2)
        
        # 删除按钮
        btn_delete = tk.Button(
            frame, text='×',
            font=('Microsoft YaHei', 12, 'bold'),
            bg=COLORS['expense'], fg='white',
            relief='flat', cursor='hand2',
            width=2, command=lambda: self._delete_record(record['id'])
        )
        btn_delete.pack(side='left', padx=(2, 8))
        
        return frame
    
    def _toggle_record(self, record_id):
        self.db.toggle_checked(record_id)
        self._refresh_records()
    
    def _edit_record(self, record_id):
        record = next((r for r in self.db.records if r['id'] == record_id), None)
        if not record:
            return
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title('编辑记录')
        edit_window.geometry('300x250')
        edit_window.configure(bg=COLORS['bg'])
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        tk.Label(edit_window, text='来源/物品:', font=('Microsoft YaHei', 11), bg=COLORS['bg']).pack(pady=(15, 5))
        source_entry = tk.Entry(edit_window, font=('Microsoft YaHei', 12), width=25)
        source_entry.insert(0, record['source'])
        source_entry.pack()
        
        tk.Label(edit_window, text='金额:', font=('Microsoft YaHei', 11), bg=COLORS['bg']).pack(pady=(15, 5))
        amount_entry = tk.Entry(edit_window, font=('Microsoft YaHei', 12), width=25)
        amount_entry.insert(0, str(record['amount']))
        amount_entry.pack()
        
        type_text = '收入' if record['type'] == 'income' else '支出'
        type_color = COLORS['income'] if record['type'] == 'income' else COLORS['expense']
        tk.Label(edit_window, text=f'类型: {type_text}', font=('Microsoft YaHei', 11), bg=COLORS['bg'], fg=type_color).pack(pady=(15, 5))
        
        def save():
            new_source = source_entry.get().strip()
            new_amount_text = amount_entry.get().strip()
            
            if not new_source:
                messagebox.showwarning('提示', '请输入来源/物品名称', parent=edit_window)
                return
            
            try:
                new_amount = float(new_amount_text)
                if new_amount <= 0:
                    messagebox.showwarning('提示', '金额必须大于0', parent=edit_window)
                    return
            except ValueError:
                messagebox.showwarning('提示', '金额格式错误', parent=edit_window)
                return
            
            self.db.update_record(record_id, source=new_source, amount=new_amount)
            edit_window.destroy()
            self._refresh_records()
        
        btn_frame = tk.Frame(edit_window, bg=COLORS['bg'])
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text='保存', font=('Microsoft YaHei', 10),
                 bg=COLORS['fg'], fg='white', relief='flat', cursor='hand2',
                 width=8, command=save).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text='取消', font=('Microsoft YaHei', 10),
                 bg=COLORS['accent_2'], fg='white', relief='flat', cursor='hand2',
                 width=8, command=edit_window.destroy).pack(side='left', padx=5)
    
    def _delete_record(self, record_id):
        if messagebox.askyesno('确认', '确定要删除这条记录吗？'):
            self.db.delete_record(record_id)
            self._refresh_records()
    
    def show_summary(self):
        """显示总结页面"""
        self.clear_container()
        
        # 顶部导航
        nav_frame = tk.Frame(self.container, bg=COLORS['bg'])
        nav_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(
            nav_frame, text='← 返回',
            font=('Microsoft YaHei', 12),
            bg=COLORS['accent'], fg='white',
            relief='flat', cursor='hand2',
            command=self.show_main
        ).pack(side='left')
        
        tk.Label(
            nav_frame, text='总 结',
            font=('Microsoft YaHei', 18, 'bold'),
            bg=COLORS['bg'], fg=COLORS['fg']
        ).pack(side='left', expand=True)
        
        tk.Button(
            nav_frame, text='导出',
            font=('Microsoft YaHei', 11),
            bg=COLORS['accent_2'], fg='white',
            relief='flat', cursor='hand2',
            command=self._export_data
        ).pack(side='right')
        
        # 视图切换
        self.summary_view = 'day'
        self.summary_year = datetime.now().year
        self.summary_month = datetime.now().month
        self.summary_date = datetime.now().strftime('%Y-%m-%d')
        
        switch_frame = tk.Frame(self.container, bg=COLORS['bg'])
        switch_frame.pack(fill='x', padx=10, pady=5)
        
        self.btn_day = tk.Button(
            switch_frame, text='日',
            font=('Microsoft YaHei', 14, 'bold'),
            bg=COLORS['fg'], fg='white',
            relief='flat', cursor='hand2',
            command=lambda: self._switch_summary_view('day')
        )
        self.btn_day.pack(side='left', expand=True, fill='x', padx=(0, 3))
        
        self.btn_month = tk.Button(
            switch_frame, text='月',
            font=('Microsoft YaHei', 14),
            bg=COLORS['accent_2'], fg=COLORS['fg_muted'],
            relief='flat', cursor='hand2',
            command=lambda: self._switch_summary_view('month')
        )
        self.btn_month.pack(side='left', expand=True, fill='x', padx=3)
        
        self.btn_year = tk.Button(
            switch_frame, text='年',
            font=('Microsoft YaHei', 14),
            bg=COLORS['accent_2'], fg=COLORS['fg_muted'],
            relief='flat', cursor='hand2',
            command=lambda: self._switch_summary_view('year')
        )
        self.btn_year.pack(side='left', expand=True, fill='x', padx=(3, 0))
        
        # 导航栏
        nav2_frame = tk.Frame(self.container, bg=COLORS['bg'])
        nav2_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(
            nav2_frame, text='◀',
            font=('Microsoft YaHei', 10),
            bg=COLORS['accent_2'], fg='white',
            relief='flat', cursor='hand2',
            width=3, command=lambda: self._nav_summary(-1)
        ).pack(side='left')
        
        self.nav_label = tk.Label(
            nav2_frame, text='',
            font=('Microsoft YaHei', 14, 'bold'),
            bg=COLORS['bg'], fg=COLORS['fg']
        )
        self.nav_label.pack(side='left', expand=True)
        
        tk.Button(
            nav2_frame, text='▶',
            font=('Microsoft YaHei', 10),
            bg=COLORS['accent_2'], fg='white',
            relief='flat', cursor='hand2',
            width=3, command=lambda: self._nav_summary(1)
        ).pack(side='right')
        
        # 统计卡片
        self.summary_stats_frame = self._create_summary_stats()
        self.summary_stats_frame.pack(fill='x', padx=10, pady=5)
        
        # 内容区域
        content_container = tk.Frame(self.container, bg=COLORS['bg'])
        content_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(content_container, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_container, orient='vertical', command=canvas.yview)
        self.summary_content_frame = tk.Frame(canvas, bg=COLORS['bg'])
        
        self.summary_content_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=self.summary_content_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self._update_summary_view()
    
    def _switch_summary_view(self, view):
        self.summary_view = view
        
        self.btn_day.config(bg=COLORS['fg'] if view == 'day' else COLORS['accent_2'],
                          fg='white' if view == 'day' else COLORS['fg_muted'],
                          font=('Microsoft YaHei', 14, 'bold' if view == 'day' else 'normal'))
        self.btn_month.config(bg=COLORS['fg'] if view == 'month' else COLORS['accent_2'],
                             fg='white' if view == 'month' else COLORS['fg_muted'],
                             font=('Microsoft YaHei', 14, 'bold' if view == 'month' else 'normal'))
        self.btn_year.config(bg=COLORS['fg'] if view == 'year' else COLORS['accent_2'],
                            fg='white' if view == 'year' else COLORS['fg_muted'],
                            font=('Microsoft YaHei', 14, 'bold' if view == 'year' else 'normal'))
        
        if view == 'day':
            self.summary_date = datetime.now().strftime('%Y-%m-%d')
        elif view == 'month':
            self.summary_year = datetime.now().year
            self.summary_month = datetime.now().month
        else:
            self.summary_year = datetime.now().year
        
        self._update_summary_view()
    
    def _nav_summary(self, direction):
        if self.summary_view == 'day':
            date_obj = datetime.strptime(self.summary_date, '%Y-%m-%d')
            date_obj += timedelta(days=direction)
            self.summary_date = date_obj.strftime('%Y-%m-%d')
        elif self.summary_view == 'month':
            self.summary_month += direction
            if self.summary_month < 1:
                self.summary_month = 12
                self.summary_year -= 1
            elif self.summary_month > 12:
                self.summary_month = 1
                self.summary_year += 1
        else:
            self.summary_year += direction
        
        self._update_summary_view()
    
    def _update_summary_view(self):
        # 更新导航标签
        if self.summary_view == 'day':
            date_obj = datetime.strptime(self.summary_date, '%Y-%m-%d')
            weekday = WEEKDAYS[date_obj.weekday()]
            self.nav_label.config(text=f'{self.summary_date} {weekday}')
        elif self.summary_view == 'month':
            self.nav_label.config(text=f'{self.summary_year}年{self.summary_month}月')
        else:
            self.nav_label.config(text=f'{self.summary_year}年')
        
        # 更新统计
        self._update_summary_stats()
        # 更新内容
        self._render_summary_content()
    
    def _create_summary_stats(self):
        frame = tk.Frame(self.container, bg=COLORS['card'],
                        highlightbackground=COLORS['border'], highlightthickness=1)
        frame.pack_propagate(False)
        frame.config(height=70)
        return frame
    
    def _update_summary_stats(self):
        for widget in self.summary_stats_frame.winfo_children():
            widget.destroy()
        
        if self.summary_view == 'day':
            summary = self.db.get_date_summary(self.summary_date)
        elif self.summary_view == 'month':
            summary = self.db.get_month_summary(self.summary_year, self.summary_month)
        else:
            year_summary = self.db.get_year_summary(self.summary_year)
            summary = {
                'income': year_summary['total_income'],
                'expense': year_summary['total_expense'],
                'net': year_summary['total_net']
            }
        
        income = summary['income']
        expense = summary['expense']
        net = summary['net']
        
        # 收入
        f1 = tk.Frame(self.summary_stats_frame, bg=COLORS['card'])
        f1.pack(side='left', expand=True, fill='both', padx=10, pady=8)
        tk.Label(f1, text='收入', font=('Microsoft YaHei', 9), bg=COLORS['card'], fg=COLORS['fg_muted']).pack()
        tk.Label(f1, text=f'+{income:.2f}', font=('Microsoft YaHei', 14, 'bold'), bg=COLORS['card'], fg=COLORS['income']).pack()
        
        # 支出
        f2 = tk.Frame(self.summary_stats_frame, bg=COLORS['card'])
        f2.pack(side='left', expand=True, fill='both', padx=10, pady=8)
        tk.Label(f2, text='支出', font=('Microsoft YaHei', 9), bg=COLORS['card'], fg=COLORS['fg_muted']).pack()
        tk.Label(f2, text=f'-{expense:.2f}', font=('Microsoft YaHei', 14, 'bold'), bg=COLORS['card'], fg=COLORS['expense']).pack()
        
        # 净收入
        f3 = tk.Frame(self.summary_stats_frame, bg=COLORS['card'])
        f3.pack(side='left', expand=True, fill='both', padx=10, pady=8)
        tk.Label(f3, text='净收入', font=('Microsoft YaHei', 9), bg=COLORS['card'], fg=COLORS['fg_muted']).pack()
        net_color = COLORS['income'] if net >= 0 else COLORS['expense']
        tk.Label(f3, text=f'{net:+.2f}', font=('Microsoft YaHei', 14, 'bold'), bg=COLORS['card'], fg=net_color).pack()
    
    def _render_summary_content(self):
        for widget in self.summary_content_frame.winfo_children():
            widget.destroy()
        
        if self.summary_view == 'day':
            self._render_day_summary()
        elif self.summary_view == 'month':
            self._render_month_summary()
        else:
            self._render_year_summary()
    
    def _render_day_summary(self):
        records = self.db.get_records_by_date(self.summary_date)
        records.sort(key=lambda r: r['time'])
        
        if not records:
            tk.Label(self.summary_content_frame, text='该日暂无记录',
                    font=('Microsoft YaHei', 12), bg=COLORS['bg'], fg=COLORS['fg_muted']).pack(pady=30)
            return
        
        for record in records:
            self._create_summary_item(record).pack(fill='x', pady=2, padx=5)
    
    def _render_month_summary(self):
        records = self.db.get_records_by_month(self.summary_year, self.summary_month)
        
        if not records:
            tk.Label(self.summary_content_frame, text='该月暂无记录',
                    font=('Microsoft YaHei', 12), bg=COLORS['bg'], fg=COLORS['fg_muted']).pack(pady=30)
            return
        
        # 按日期分组
        grouped = defaultdict(list)
        for r in records:
            grouped[r['date']].append(r)
        
        for date in sorted(grouped.keys(), reverse=True):
            day_records = grouped[date]
            income = sum(r['amount'] for r in day_records if r['type'] == 'income')
            expense = sum(r['amount'] for r in day_records if r['type'] == 'expense')
            
            # 日期标题
            date_header = tk.Frame(self.summary_content_frame, bg=COLORS['bg'])
            date_header.pack(fill='x', padx=5, pady=(10, 2))
            
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                weekday = WEEKDAYS[date_obj.weekday()]
            except:
                weekday = ''
            
            tk.Label(date_header, text=f'{date} {weekday}',
                    font=('Microsoft YaHei', 10, 'bold'), bg=COLORS['bg'], fg=COLORS['fg']).pack(side='left')
            tk.Label(date_header, text=f'收+{income:.2f}  支-{expense:.2f}',
                    font=('Microsoft YaHei', 9), bg=COLORS['bg'], fg=COLORS['fg_muted']).pack(side='right')
            
            for record in sorted(day_records, key=lambda r: r['time']):
                self._create_summary_item(record).pack(fill='x', pady=1, padx=5)
    
    def _render_year_summary(self):
        year_summary = self.db.get_year_summary(self.summary_year)
        monthly = year_summary['monthly']
        
        has_data = any(m['income'] > 0 or m['expense'] > 0 for m in monthly.values())
        
        if not has_data:
            tk.Label(self.summary_content_frame, text='该年暂无记录',
                    font=('Microsoft YaHei', 12), bg=COLORS['bg'], fg=COLORS['fg_muted']).pack(pady=30)
            return
        
        month_names = ['一月', '二月', '三月', '四月', '五月', '六月',
                       '七月', '八月', '九月', '十月', '十一月', '十二月']
        
        for month in range(1, 13):
            data = monthly[month]
            if data['income'] == 0 and data['expense'] == 0:
                continue
            
            net_color = COLORS['income'] if data['net'] >= 0 else COLORS['expense']
            
            frame = tk.Frame(self.summary_content_frame, bg=COLORS['card'],
                            highlightbackground=COLORS['border'], highlightthickness=1)
            frame.pack(fill='x', padx=5, pady=3)
            
            tk.Label(frame, text=month_names[month - 1],
                    font=('Microsoft YaHei', 13, 'bold'), bg=COLORS['card'], fg=COLORS['fg']).pack(anchor='w', padx=10, pady=(8, 2))
            
            data_frame = tk.Frame(frame, bg=COLORS['card'])
            data_frame.pack(fill='x', padx=10, pady=(0, 8))
            
            tk.Label(data_frame, text=f'收 +{data["income"]:.2f}',
                    font=('Microsoft YaHei', 11), bg=COLORS['card'], fg=COLORS['income']).pack(side='left', expand=True)
            tk.Label(data_frame, text=f'支 -{data["expense"]:.2f}',
                    font=('Microsoft YaHei', 11), bg=COLORS['card'], fg=COLORS['expense']).pack(side='left', expand=True)
            tk.Label(data_frame, text=f'净 {data["net"]:+.2f}',
                    font=('Microsoft YaHei', 11, 'bold'), bg=COLORS['card'], fg=net_color).pack(side='left', expand=True)
    
    def _create_summary_item(self, record):
        is_income = record['type'] == 'income'
        amount_color = COLORS['income'] if is_income else COLORS['expense']
        
        frame = tk.Frame(self.summary_content_frame, bg=COLORS['card'],
                        highlightbackground=COLORS['border'], highlightthickness=1)
        
        icon = '↓' if is_income else '↑'
        tk.Label(frame, text=icon, font=('Microsoft YaHei', 11, 'bold'),
                bg=COLORS['card'], fg=amount_color).pack(side='left', padx=8)
        
        tk.Label(frame, text=record['source'][:12], font=('Microsoft YaHei', 11),
                bg=COLORS['card'], fg=COLORS['fg']).pack(side='left', padx=5)
        
        tk.Label(frame, text=record['time'][:5], font=('Microsoft YaHei', 9),
                bg=COLORS['card'], fg=COLORS['fg_muted']).pack(side='left', padx=10)
        
        prefix = '+' if is_income else '-'
        tk.Label(frame, text=f'{prefix}{record["amount"]:.2f}', font=('Microsoft YaHei', 11, 'bold'),
                bg=COLORS['card'], fg=amount_color).pack(side='right', padx=10, pady=8)
        
        return frame
    
    def _export_data(self):
        if messagebox.askyesno('导出', f'确定要将数据导出到CSV文件吗？\n\n文件路径: {self.db.csv_file}'):
            if self.db.export_csv(self.db.csv_file):
                messagebox.showinfo('成功', f'数据已导出到:\n{self.db.csv_file}')
            else:
                messagebox.showerror('失败', '导出过程中出现错误')
    
    def show_detail(self):
        """显示明细页面"""
        self.clear_container()
        
        # 顶部导航
        nav_frame = tk.Frame(self.container, bg=COLORS['bg'])
        nav_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(
            nav_frame, text='← 返回',
            font=('Microsoft YaHei', 12),
            bg=COLORS['accent'], fg='white',
            relief='flat', cursor='hand2',
            command=self.show_main
        ).pack(side='left')
        
        tk.Label(
            nav_frame, text='明 细',
            font=('Microsoft YaHei', 18, 'bold'),
            bg=COLORS['bg'], fg=COLORS['fg']
        ).pack(side='left', expand=True)
        
        tk.Button(
            nav_frame, text='统计',
            font=('Microsoft YaHei', 11),
            bg=COLORS['accent_2'], fg='white',
            relief='flat', cursor='hand2',
            command=self._show_statistics
        ).pack(side='right')
        
        # 月份过滤
        filter_frame = tk.Frame(self.container, bg=COLORS['bg'])
        filter_frame.pack(fill='x', padx=10, pady=5)
        
        now = datetime.now()
        self.detail_year = now.year
        self.detail_month = now.month
        self.detail_show_all = False
        
        tk.Button(
            filter_frame, text='◀',
            font=('Microsoft YaHei', 10),
            bg=COLORS['accent_2'], fg='white',
            relief='flat', cursor='hand2',
            width=3, command=self._detail_prev_month
        ).pack(side='left')
        
        self.detail_month_label = tk.Label(
            filter_frame, text=f'{self.detail_year}年{self.detail_month}月',
            font=('Microsoft YaHei', 12, 'bold'),
            bg=COLORS['bg'], fg=COLORS['fg']
        )
        self.detail_month_label.pack(side='left', expand=True)
        
        tk.Button(
            filter_frame, text='▶',
            font=('Microsoft YaHei', 10),
            bg=COLORS['accent_2'], fg='white',
            relief='flat', cursor='hand2',
            width=3, command=self._detail_next_month
        ).pack(side='right', padx=(3, 4))
        
        self.btn_all = tk.Button(
            filter_frame, text='全部',
            font=('Microsoft YaHei', 11),
            bg=COLORS['accent'], fg='white',
            relief='flat', cursor='hand2',
            width=4, command=self._detail_toggle_all
        )
        self.btn_all.pack(side='right', padx=(4, 0))
        
        # 月度统计
        self.detail_stats_frame = self._create_detail_stats()
        self.detail_stats_frame.pack(fill='x', padx=10, pady=5)
        
        # 明细列表
        content_container = tk.Frame(self.container, bg=COLORS['bg'])
        content_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(content_container, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_container, orient='vertical', command=canvas.yview)
        self.detail_content_frame = tk.Frame(canvas, bg=COLORS['bg'])
        
        self.detail_content_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=self.detail_content_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self._refresh_details()
    
    def _create_detail_stats(self):
        frame = tk.Frame(self.container, bg=COLORS['card'],
                        highlightbackground=COLORS['border'], highlightthickness=1)
        frame.pack_propagate(False)
        frame.config(height=60)
        return frame
    
    def _detail_prev_month(self):
        self.detail_show_all = False
        self.btn_all.config(bg=COLORS['accent_2'], fg=COLORS['fg_muted'])
        self.detail_month -= 1
        if self.detail_month < 1:
            self.detail_month = 12
            self.detail_year -= 1
        self.detail_month_label.config(text=f'{self.detail_year}年{self.detail_month}月')
        self._refresh_details()
    
    def _detail_next_month(self):
        self.detail_show_all = False
        self.btn_all.config(bg=COLORS['accent_2'], fg=COLORS['fg_muted'])
        self.detail_month += 1
        if self.detail_month > 12:
            self.detail_month = 1
            self.detail_year += 1
        self.detail_month_label.config(text=f'{self.detail_year}年{self.detail_month}月')
        self._refresh_details()
    
    def _detail_toggle_all(self):
        self.detail_show_all = not self.detail_show_all
        if self.detail_show_all:
            self.btn_all.config(bg=COLORS['fg'], fg='white', text='全部')
            self.detail_month_label.config(text='全部记录')
        else:
            self.btn_all.config(bg=COLORS['accent_2'], fg=COLORS['fg_muted'], text='全部')
            self.detail_month_label.config(text=f'{self.detail_year}年{self.detail_month}月')
        self._refresh_details()
    
    def _refresh_details(self):
        # 更新统计
        for widget in self.detail_stats_frame.winfo_children():
            widget.destroy()
        
        if self.detail_show_all:
            records = self.db.get_all_records()
        else:
            records = self.db.get_records_by_month(self.detail_year, self.detail_month)
        
        income = sum(r['amount'] for r in records if r['type'] == 'income')
        expense = sum(r['amount'] for r in records if r['type'] == 'expense')
        net = income - expense
        
        # 收入
        f1 = tk.Frame(self.detail_stats_frame, bg=COLORS['card'])
        f1.pack(side='left', expand=True, fill='both', padx=8, pady=6)
        tk.Label(f1, text='收入', font=('Microsoft YaHei', 9), bg=COLORS['card'], fg=COLORS['fg_muted']).pack()
        tk.Label(f1, text=f'+{income:.2f}', font=('Microsoft YaHei', 13, 'bold'), bg=COLORS['card'], fg=COLORS['income']).pack()
        
        # 支出
        f2 = tk.Frame(self.detail_stats_frame, bg=COLORS['card'])
        f2.pack(side='left', expand=True, fill='both', padx=8, pady=6)
        tk.Label(f2, text='支出', font=('Microsoft YaHei', 9), bg=COLORS['card'], fg=COLORS['fg_muted']).pack()
        tk.Label(f2, text=f'-{expense:.2f}', font=('Microsoft YaHei', 13, 'bold'), bg=COLORS['card'], fg=COLORS['expense']).pack()
        
        # 净收入
        f3 = tk.Frame(self.detail_stats_frame, bg=COLORS['card'])
        f3.pack(side='left', expand=True, fill='both', padx=8, pady=6)
        tk.Label(f3, text='净收入', font=('Microsoft YaHei', 9), bg=COLORS['card'], fg=COLORS['fg_muted']).pack()
        net_color = COLORS['income'] if net >= 0 else COLORS['expense']
        tk.Label(f3, text=f'{net:+.2f}', font=('Microsoft YaHei', 13, 'bold'), bg=COLORS['card'], fg=net_color).pack()
        
        # 渲染明细
        for widget in self.detail_content_frame.winfo_children():
            widget.destroy()
        
        if not records:
            tk.Label(self.detail_content_frame, text='暂无记录',
                    font=('Microsoft YaHei', 12), bg=COLORS['bg'], fg=COLORS['fg_muted']).pack(pady=30)
            return
        
        # 按日期分组
        grouped = defaultdict(list)
        for r in records:
            grouped[r['date']].append(r)
        
        for date in sorted(grouped.keys(), reverse=True):
            day_records = grouped[date]
            date_summary = self.db.get_date_summary(date)
            
            # 日期标题
            date_header = tk.Frame(self.detail_content_frame, bg=COLORS['bg'])
            date_header.pack(fill='x', padx=5, pady=(10, 2))
            
            tk.Label(date_header, text=date,
                    font=('Microsoft YaHei', 11, 'bold'), bg=COLORS['bg'], fg=COLORS['fg']).pack(side='left')
            tk.Label(date_header, text=date_summary['weekday'],
                    font=('Microsoft YaHei', 9), bg=COLORS['bg'], fg=COLORS['fg_muted']).pack(side='left', padx=5)
            tk.Label(date_header, text=f'收+{date_summary["income"]:.2f}  支-{date_summary["expense"]:.2f}',
                    font=('Microsoft YaHei', 9), bg=COLORS['bg'], fg=COLORS['fg_muted']).pack(side='right')
            
            # 记录项
            for record in sorted(day_records, key=lambda r: r['time'], reverse=True):
                self._create_detail_item(record).pack(fill='x', pady=1, padx=5)
    
    def _create_detail_item(self, record):
        is_income = record['type'] == 'income'
        amount_color = COLORS['income'] if is_income else COLORS['expense']
        
        frame = tk.Frame(self.detail_content_frame, bg=COLORS['card'],
                        highlightbackground=COLORS['border'], highlightthickness=1)
        
        icon = '↓' if is_income else '↑'
        tk.Label(frame, text=icon, font=('Microsoft YaHei', 9, 'bold'),
                bg=COLORS['card'], fg=amount_color).pack(side='left', padx=6)
        
        tk.Label(frame, text=record['source'][:14], font=('Microsoft YaHei', 11),
                bg=COLORS['card'], fg=COLORS['fg']).pack(side='left', padx=4)
        
        tk.Label(frame, text=record['time'][:5], font=('Microsoft YaHei', 9),
                bg=COLORS['card'], fg=COLORS['fg_muted']).pack(side='left', padx=8)
        
        prefix = '+' if is_income else '-'
        tk.Label(frame, text=f'{prefix}{record["amount"]:.2f}', font=('Microsoft YaHei', 11, 'bold'),
                bg=COLORS['card'], fg=amount_color).pack(side='right', padx=4)
        
        # 编辑按钮
        tk.Button(frame, text='✎', font=('Microsoft YaHei', 9),
                 bg=COLORS['accent'], fg='white', relief='flat', cursor='hand2',
                 width=2, command=lambda rid=record['id']: self._edit_record(rid)).pack(side='right', padx=1)
        
        # 删除按钮
        tk.Button(frame, text='×', font=('Microsoft YaHei', 11, 'bold'),
                 bg=COLORS['expense'], fg='white', relief='flat', cursor='hand2',
                 width=2, command=lambda rid=record['id']: self._delete_record(rid)).pack(side='right', padx=1)
        
        return frame
    
    def _show_statistics(self):
        stats = self.db.get_statistics()
        
        window = tk.Toplevel(self.root)
        window.title('统计信息')
        window.geometry('320x280')
        window.configure(bg=COLORS['bg'])
        window.transient(self.root)
        
        tk.Label(window, text='数据统计', font=('Microsoft YaHei', 14, 'bold'),
                bg=COLORS['bg'], fg=COLORS['fg']).pack(pady=15)
        
        stats_text = f'''总记录数: {stats['total_records']}
总收入: +{stats['total_income']:.2f}
总支出: -{stats['total_expense']:.2f}
净收入: {stats['total_net']:+.2f}

数据文件路径:
{self.db.csv_file}'''
        
        tk.Label(window, text=stats_text, font=('Microsoft YaHei', 11),
                bg=COLORS['bg'], fg=COLORS['fg'], justify='left').pack(pady=10)
        
        tk.Button(window, text='关闭', font=('Microsoft YaHei', 11),
                 bg=COLORS['fg'], fg='white', relief='flat', cursor='hand2',
                 width=10, command=window.destroy).pack(pady=15)


if __name__ == '__main__':
    app = LedgerApp()
    app.run()
