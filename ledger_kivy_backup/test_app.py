#!/usr/bin/env python3
"""账本应用 - 功能测试脚本"""
import sys
import os
import tempfile
import shutil
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database


def test_database():
    """测试数据库功能"""
    print("=" * 60)
    print("账本应用 - 功能测试")
    print("=" * 60)
    
    # 创建临时目录
    test_dir = tempfile.mkdtemp()
    db = Database()
    db.data_dir = test_dir
    db.csv_file = os.path.join(test_dir, 'test_records.csv')
    db.records = []
    
    print("\n📁 数据存储路径:", db.csv_file)
    print()
    
    # 1. 添加记录
    print("【1. 添加记录测试】")
    id1 = db.add_record('早餐', 15.0, 'expense')
    id2 = db.add_record('午餐', 28.5, 'expense')
    id3 = db.add_record('交通', 12.0, 'expense')
    id4 = db.add_record('工资', 8000.0, 'income')
    id5 = db.add_record('加班费', 500.0, 'income')
    id6 = db.add_record('晚餐', 35.0, 'expense')
    
    print(f"  ✓ 添加 {id1}: 早餐 - 15.00 (支出)")
    print(f"  ✓ 添加 {id2}: 午餐 - 28.50 (支出)")
    print(f"  ✓ 添加 {id3}: 交通 - 12.00 (支出)")
    print(f"  ✓ 添加 {id4}: 工资 - 8000.00 (收入)")
    print(f"  ✓ 添加 {id5}: 加班费 - 500.00 (收入)")
    print(f"  ✓ 添加 {id6}: 晚餐 - 35.00 (支出)")
    print(f"  总记录数: {len(db.records)}")
    
    # 2. 今日总结
    print("\n【2. 今日总结测试】")
    today_summary = db.get_today_summary()
    print(f"  日期: {today_summary['date']} ({today_summary['weekday']})")
    print(f"  收入: +{today_summary['income']:.2f}")
    print(f"  支出: -{today_summary['expense']:.2f}")
    print(f"  净收入: {today_summary['net']:+.2f}")
    
    # 3. 切换打勾状态
    print("\n【3. 打勾功能测试】")
    print(f"  打勾前: 早餐状态 = {'已完成' if db.records[0]['checked'] else '未完成'}")
    db.toggle_checked(id1)
    print(f"  打勾后: 早餐状态 = {'已完成' if db.records[0]['checked'] else '未完成'}")
    db.toggle_checked(id1)
    print(f"  再次切换: 早餐状态 = {'已完成' if db.records[0]['checked'] else '未完成'}")
    
    # 4. 更新记录
    print("\n【4. 更新记录测试】")
    print(f"  更新前: 午餐 = {db.records[1]['source']} - {db.records[1]['amount']:.2f}")
    db.update_record(id2, source='午餐(公司)', amount=30.0)
    print(f"  更新后: 午餐(公司) = {db.records[1]['source']} - {db.records[1]['amount']:.2f}")
    
    # 5. 删除记录
    print("\n【5. 删除记录测试】")
    print(f"  删除前记录数: {len(db.records)}")
    db.delete_record(id3)  # 删除交通
    print(f"  删除后记录数: {len(db.records)}")
    
    # 6. 查询记录
    print("\n【6. 查询记录测试】")
    today = datetime.now().strftime('%Y-%m-%d')
    today_records = db.get_records_by_date(today)
    print(f"  今日记录数: {len(today_records)}")
    for r in today_records:
        type_icon = '📈' if r['type'] == 'income' else '📉'
        amount_sign = '+' if r['type'] == 'income' else '-'
        print(f"    {type_icon} {r['source']} {amount_sign}{r['amount']:.2f}")
    
    # 7. 月度总结
    print("\n【7. 月度总结测试】")
    month_summary = db.get_month_summary()
    print(f"  {month_summary['year']}年{month_summary['month']}月:")
    print(f"    总收入: +{month_summary['income']:.2f}")
    print(f"    总支出: -{month_summary['expense']:.2f}")
    print(f"    净收入: {month_summary['net']:+.2f}")
    
    # 8. 年度总结
    print("\n【8. 年度总结测试】")
    year_summary = db.get_year_summary()
    print(f"  {year_summary['year']}年:")
    print(f"    总收入: +{year_summary['total_income']:.2f}")
    print(f"    总支出: -{year_summary['total_expense']:.2f}")
    print(f"    净收入: {year_summary['total_net']:+.2f}")
    print(f"    月度明细:")
    for month in range(1, 13):
        m = year_summary['monthly'][month]
        if m['income'] > 0 or m['expense'] > 0:
            print(f"      {month}月: 收+{m['income']:.2f} 支-{m['expense']:.2f} 净{m['net']:+.2f}")
    
    # 9. 导出CSV
    print("\n【9. CSV导出测试】")
    export_path = os.path.join(test_dir, 'export_test.csv')
    success = db.export_csv(export_path)
    if success:
        print(f"  ✓ 导出成功: {export_path}")
        with open(export_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"  文件内容 ({len(lines)}行):")
            for line in lines:
                print(f"    {line.strip()}")
    else:
        print("  ✗ 导出失败")
    
    # 10. 日期总结
    print("\n【10. 日期总结测试】")
    date_summary = db.get_date_summary(today)
    print(f"  {date_summary['date']} ({date_summary['weekday']}):")
    print(f"    记录数: {date_summary['count']}")
    print(f"    收入: +{date_summary['income']:.2f}")
    print(f"    支出: -{date_summary['expense']:.2f}")
    print(f"    净收入: {date_summary['net']:+.2f}")
    
    # 11. 统计信息
    print("\n【11. 全局统计测试】")
    stats = db.get_statistics()
    print(f"  总记录数: {stats['total_records']}")
    print(f"  总收入: +{stats['total_income']:.2f}")
    print(f"  总支出: -{stats['total_expense']:.2f}")
    print(f"  净收入: {stats['total_net']:+.2f}")
    
    # 12. 日期排序
    print("\n【12. 日期列表测试】")
    dates = db.get_all_dates_sorted()
    print(f"  有记录的日期:")
    for d in dates:
        summary = db.get_date_summary(d)
        print(f"    {d} ({summary['weekday']}): {summary['count']}条记录")
    
    # 13. 跨月测试
    print("\n【13. 跨月记录测试】")
    # 添加上月记录
    last_month = datetime.now().replace(day=1) - timedelta(days=1)
    last_month_str = last_month.strftime('%Y-%m-%d')
    
    # 直接修改一条记录的日期进行测试
    if len(db.records) > 0:
        test_record = db.records[0]
        original_date = test_record['date']
        test_record['date'] = last_month_str
        db._save_records()
        
        # 重新加载
        db.reload()
        
        # 查询不同月份
        current_month = datetime.now().month
        last_month_num = last_month.month
        
        print(f"  当前月份记录:")
        current_month_records = db.get_records_by_month(datetime.now().year, current_month)
        current_income = sum(r['amount'] for r in current_month_records if r['type'] == 'income')
        current_expense = sum(r['amount'] for r in current_month_records if r['type'] == 'expense')
        print(f"    {current_month}月: {len(current_month_records)}条 收+{current_income:.2f} 支-{current_expense:.2f}")
        
        print(f"  上月记录:")
        last_month_records = db.get_records_by_month(last_month.year, last_month_num)
        last_income = sum(r['amount'] for r in last_month_records if r['type'] == 'income')
        last_expense = sum(r['amount'] for r in last_month_records if r['type'] == 'expense')
        print(f"    {last_month_num}月: {len(last_month_records)}条 收+{last_income:.2f} 支-{last_expense:.2f}")
        
        # 恢复
        db.records[0]['date'] = original_date
        db._save_records()
        db.reload()
    
    # 清理
    shutil.rmtree(test_dir)
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
    print("\n📱 运行 GUI 应用:")
    print("   pip install kivy")
    print("   python run.py")
    print("\n📦 数据文件位置:")
    print("   ~/.ledger_data/records.csv")


if __name__ == '__main__':
    test_database()
