# 数据存储模块 - 使用CSV格式存储账单数据
import os
import csv
import json
from datetime import datetime, timedelta
from collections import defaultdict


class Database:
    """本地CSV数据库管理类"""
    
    def __init__(self):
        # 数据存储路径
        self.data_dir = self._get_data_dir()
        self.csv_file = os.path.join(self.data_dir, 'records.csv')
        self.records = []
        self._ensure_data_dir()
        self._load_records()
    
    def _get_data_dir(self):
        """获取数据存储目录"""
        # 尝试获取应用数据目录
        data_dir = os.path.join(os.path.expanduser('~'), '.ledger_data')
        return data_dir
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _load_records(self):
        """从CSV文件加载记录"""
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
                            'type': row['type'],  # 'income' 或 'expense'
                            'checked': row.get('checked', 'false') == 'true'
                        }
                        self.records.append(record)
            except Exception as e:
                print(f"加载数据失败: {e}")
                self.records = []
    
    def _save_records(self):
        """保存记录到CSV文件"""
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
        """重新加载数据"""
        self._load_records()
    
    def _get_next_id(self):
        """获取下一个ID"""
        if self.records:
            return max(r['id'] for r in self.records) + 1
        return 1
    
    def add_record(self, source, amount, record_type, checked=False):
        """
        添加新记录
        :param source: 来源/物品名称
        :param amount: 金额
        :param record_type: 'income' 或 'expense'
        :param checked: 是否已完成（打勾状态）
        :return: 新记录的ID
        """
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
        """
        更新记录
        :param record_id: 记录ID
        :param kwargs: 要更新的字段
        """
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
        """删除记录"""
        self.records = [r for r in self.records if r['id'] != record_id]
        self._save_records()
    
    def toggle_checked(self, record_id):
        """切换打勾状态"""
        for record in self.records:
            if record['id'] == record_id:
                record['checked'] = not record['checked']
                self._save_records()
                return True
        return False
    
    def get_all_records(self):
        """获取所有记录"""
        return sorted(self.records, key=lambda r: (r['date'], r['time']), reverse=True)
    
    def get_records_by_date(self, date_str):
        """获取指定日期的记录"""
        return [r for r in self.records if r['date'] == date_str]
    
    def get_records_by_month(self, year, month):
        """获取指定月份的记录"""
        month_str = f'{year}-{month:02d}'
        return [r for r in self.records if r['date'].startswith(month_str)]
    
    def get_records_by_year(self, year):
        """获取指定年份的记录"""
        year_str = f'{year}'
        return [r for r in self.records if r['date'].startswith(year_str)]
    
    def get_today_records(self):
        """获取今日记录"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.get_records_by_date(today)
    
    def get_yesterday_records(self):
        """获取昨日记录"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        return self.get_records_by_date(yesterday)
    
    def get_today_summary(self):
        """获取今日总结"""
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
        """获取月度总结"""
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
        """获取年度总结"""
        if year is None:
            year = datetime.now().year
        
        year_records = self.get_records_by_year(year)
        income = sum(r['amount'] for r in year_records if r['type'] == 'income')
        expense = sum(r['amount'] for r in year_records if r['type'] == 'expense')
        
        # 每月统计
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
    
    def get_date_summary(self, date_str):
        """获取指定日期总结"""
        records = self.get_records_by_date(date_str)
        income = sum(r['amount'] for r in records if r['type'] == 'income')
        expense = sum(r['amount'] for r in records if r['type'] == 'expense')
        
        # 获取星期几
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
        """获取所有有记录的日期（降序）"""
        dates = set(r['date'] for r in self.records)
        return sorted(list(dates), reverse=True)
    
    def get_monthly_dates(self, year, month):
        """获取指定月份有记录的日期"""
        records = self.get_records_by_month(year, month)
        dates = set(r['date'] for r in records)
        return sorted(list(dates), reverse=True)
    
    def export_csv(self, filepath):
        """导出CSV文件"""
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
    
    def import_csv(self, filepath):
        """从CSV文件导入"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                # 清除现有数据
                self.records = []
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
                self._save_records()
            return True
        except Exception as e:
            print(f"导入失败: {e}")
            return False
    
    def get_statistics(self):
        """获取基本统计信息"""
        return {
            'total_records': len(self.records),
            'total_income': sum(r['amount'] for r in self.records if r['type'] == 'income'),
            'total_expense': sum(r['amount'] for r in self.records if r['type'] == 'expense'),
            'total_net': sum(
                r['amount'] if r['type'] == 'income' else -r['amount']
                for r in self.records
            )
        }
    
    def get_available_months(self):
        """获取所有有记录的年月列表"""
        months = set()
        for r in self.records:
            try:
                parts = r['date'].split('-')
                if len(parts) == 2:
                    year_month = f"{parts[0]}-{parts[1]}"
                    months.add(year_month)
            except:
                pass
        return sorted(list(months), reverse=True)
    
    def get_available_years(self):
        """获取所有有记录的年份列表"""
        years = set()
        for r in self.records:
            try:
                year = r['date'].split('-')[0]
                years.add(int(year))
            except:
                pass
        return sorted(list(years), reverse=True)
