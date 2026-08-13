#!/usr/bin/env python3
"""账本应用 - 演示脚本：创建示例数据并展示效果"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database


def create_demo_data():
    """创建演示数据"""
    db = Database()
    
    # 检查是否已有数据
    all_records = db.get_all_records()
    if all_records:
        print("已有数据存在，跳过创建演示数据")
        print(f"当前共有 {len(all_records)} 条记录")
        return db
    
    print("📝 创建演示数据...\n")
    
    # 收入记录
    incomes = [
        ('工资', 8500),
        ('项目奖金', 2000),
        ('外快收入', 800),
        ('理财收益', 350),
        ('兼职稿费', 500),
        ('股票分红', 1200),
        ('退款', 128),
    ]
    
    # 支出记录
    expenses = [
        ('早餐', 15),
        ('午餐', 28),
        ('打车', 45),
        ('超市购物', 156),
        ('房租', 3500),
        ('水电费', 280),
        ('话费', 88),
        ('早餐', 18),
        ('咖啡', 32),
        ('电影票', 68),
        ('晚餐', 128),
        ('网购', 299),
        ('健身', 200),
        ('零食', 45),
        ('早餐', 12),
        ('午餐', 35),
        ('公交', 8),
        ('晚餐', 88),
        ('图书', 128),
        ('衣服', 599),
        ('早餐', 16),
        ('午餐', 42),
        ('水果', 68),
        ('饮料', 25),
        ('晚餐', 156),
        ('聚餐', 388),
        ('日用品', 145),
    ]
    
    print("📈 添加收入记录:")
    for source, amount in incomes:
        rid = db.add_record(source, amount, 'income')
        print(f"  + {source}: {amount:.2f}")
    
    print("\n📉 添加支出记录:")
    for source, amount in expenses:
        rid = db.add_record(source, amount, 'expense')
        print(f"  - {source}: {amount:.2f}")
    
    return db


def show_dashboard(db):
    """显示仪表盘"""
    now = __import__('datetime').datetime.now()
    
    print("\n" + "=" * 60)
    print("📊 账本仪表盘")
    print("=" * 60)
    
    # 今日统计
    today = db.get_today_summary()
    print(f"\n📅 今日 ({today['date']} {today['weekday']})")
    print(f"   收入: +{today['income']:.2f}")
    print(f"   支出: -{today['expense']:.2f}")
    print(f"   净收入: {today['net']:+.2f}")
    print(f"   记录数: {len(db.get_today_records())}")
    
    # 本月统计
    month = db.get_month_summary()
    print(f"\n📆 本月 ({month['year']}年{month['month']}月)")
    print(f"   收入: +{month['income']:.2f}")
    print(f"   支出: -{month['expense']:.2f}")
    print(f"   净收入: {month['net']:+.2f}")
    print(f"   记录数: {len(db.get_records_by_month(month['year'], month['month']))}")
    
    # 年度统计
    year = db.get_year_summary()
    print(f"\n📈 年度 ({year['year']}年)")
    print(f"   总收入: +{year['total_income']:.2f}")
    print(f"   总支出: -{year['total_expense']:.2f}")
    print(f"   净收入: {year['total_net']:+.2f}")
    
    # 月度明细
    print(f"\n   月度明细:")
    month_names = ['一月', '二月', '三月', '四月', '五月', '六月',
                   '七月', '八月', '九月', '十月', '十一月', '十二月']
    for m in range(1, 13):
        data = year['monthly'][m]
        if data['income'] > 0 or data['expense'] > 0:
            print(f"     {month_names[m-1]}: 收+{data['income']:.2f} 支-{data['expense']:.2f} 净{data['net']:+.2f}")
    
    # 全局统计
    stats = db.get_statistics()
    print(f"\n📋 数据总览")
    print(f"   总记录数: {stats['total_records']}")
    print(f"   总收入: +{stats['total_income']:.2f}")
    print(f"   总支出: -{stats['total_expense']:.2f}")
    print(f"   净收入: {stats['total_net']:+.2f}")
    print(f"   数据文件: {db.csv_file}")
    
    # 最近记录
    print(f"\n📝 最近记录 (最新10条):")
    all_records = db.get_all_records()
    for i, r in enumerate(all_records[:10], 1):
        type_icon = '📈' if r['type'] == 'income' else '📉'
        amount_sign = '+' if r['type'] == 'income' else '-'
        check = ' ✓' if r['checked'] else ''
        print(f"   {i:2d}. {type_icon} {r['source'][:8]:<8} {amount_sign}{r['amount']:>8.2f}  {r['date']} {check}")


def show_today_records(db):
    """显示今日记录详情"""
    print("\n" + "=" * 60)
    print("📝 今日记账详情 (模拟打勾式列表)")
    print("=" * 60)
    
    today_records = db.get_today_records()
    today_records.sort(key=lambda r: r['time'])
    
    if not today_records:
        print("\n   今日暂无记录")
        return
    
    print(f"\n   {'状态':<4} {'物品/来源':<12} {'时间':<8} {'金额':<10}")
    print(f"   {'─'*4} {'─'*12} {'─'*8} {'─'*10}")
    
    for r in today_records:
        check = '✓' if r['checked'] else '○'
        type_color = '📈' if r['type'] == 'income' else '📉'
        amount_sign = '+' if r['type'] == 'income' else '-'
        print(f"   {check:<4} {type_color} {r['source'][:10]:<10} {r['time'][:5]:<8} {amount_sign}{r['amount']:>8.2f}")
    
    # 汇总
    income = sum(r['amount'] for r in today_records if r['type'] == 'income')
    expense = sum(r['amount'] for r in today_records if r['type'] == 'expense')
    net = income - expense
    
    print(f"\n   当日收入: +{income:.2f}")
    print(f"   当日支出: -{expense:.2f}")
    print(f"   当日结余: {net:+.2f}")


def show_month_summary_detail(db):
    """显示月度汇总详情"""
    print("\n" + "=" * 60)
    print("📆 月度汇总详情")
    print("=" * 60)
    
    month = db.get_month_summary()
    records = db.get_records_by_month(month['year'], month['month'])
    
    if not records:
        print("\n   本月暂无记录")
        return
    
    # 按日期分组
    grouped = {}
    for r in records:
        date = r['date']
        if date not in grouped:
            grouped[date] = []
        grouped[date].append(r)
    
    print(f"\n   {month['year']}年{month['month']}月 共 {len(grouped)} 天有记录\n")
    
    for date in sorted(grouped.keys(), reverse=True):
        day_records = grouped[date]
        income = sum(r['amount'] for r in day_records if r['type'] == 'income')
        expense = sum(r['amount'] for r in day_records if r['type'] == 'expense')
        
        print(f"   📅 {date}:")
        for r in day_records:
            type_icon = '📈' if r['type'] == 'income' else '📉'
            amount_sign = '+' if r['type'] == 'income' else '-'
            print(f"      {type_icon} {r['source'][:10]:<10} {amount_sign}{r['amount']:>8.2f}")
        print(f"      小计: 收+{income:.2f} 支-{expense:.2f}")
        print()
    
    print(f"   月度汇总:")
    print(f"      总收入: +{month['income']:.2f}")
    print(f"      总支出: -{month['expense']:.2f}")
    print(f"      净收入: {month['net']:+.2f}")


def show_year_summary_detail(db):
    """显示年度汇总详情"""
    print("\n" + "=" * 60)
    print("📈 年度汇总详情")
    print("=" * 60)
    
    year = db.get_year_summary()
    print(f"\n   {year['year']}年 总账")
    print(f"   {'─'*50}")
    print(f"   总收入:  +{year['total_income']:>10.2f}")
    print(f"   总支出:  -{year['total_expense']:>10.2f}")
    print(f"   净收入:  {year['total_net']:>+10.2f}")
    
    print(f"\n   月度汇总:")
    month_names = ['一月', '二月', '三月', '四月', '五月', '六月',
                   '七月', '八月', '九月', '十月', '十一月', '十二月']
    
    print(f"   {'月份':<8} {'收入':<12} {'支出':<12} {'净收入':<12}")
    print(f"   {'─'*8} {'─'*12} {'─'*12} {'─'*12}")
    
    for m in range(1, 13):
        data = year['monthly'][m]
        if data['income'] > 0 or data['expense'] > 0:
            print(f"   {month_names[m-1]:<8} +{data['income']:>10.2f}  -{data['expense']:>10.2f}  {data['net']:>+10.2f}")


def show_csv_export(db):
    """显示CSV导出示例"""
    print("\n" + "=" * 60)
    print("📤 CSV导出预览")
    print("=" * 60)
    
    import tempfile
    import os
    
    test_dir = tempfile.mkdtemp()
    export_path = os.path.join(test_dir, 'records.csv')
    db.export_csv(export_path)
    
    print(f"\n   导出文件: {export_path}")
    print(f"\n   前5行预览:")
    
    with open(export_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i < 6:
                print(f"   {line.strip()}")
            else:
                break
    
    print(f"\n   💡 CSV格式说明:")
    print(f"      列1: id (编号)")
    print(f"      列2: date (日期 YYYY-MM-DD)")
    print(f"      列3: time (时间 HH:MM:SS)")
    print(f"      列4: source (来源/物品)")
    print(f"      列5: amount (金额)")
    print(f"      列6: type (类型: income/expense)")
    print(f"      列7: checked (是否完成: true/false)")


def main():
    print("\n" + "=" * 60)
    print("    📒 账本 - 个人记账应用演示")
    print("=" * 60)
    print("\n    功能特点:")
    print("    • 本地存储，隐私安全")
    print("    • CSV格式，方便导入导出")
    print("    • 收入(绿色) / 支出(红色) 区分")
    print("    • 日/月/年 多维度统计")
    print("    • 打勾式记账体验")
    print("    • 极简黑白灰 UI 风格")
    print("    • 响应式设计，适配手机")
    print("\n" + "=" * 60)
    
    # 创建演示数据
    db = create_demo_data()
    
    # 展示仪表盘
    show_dashboard(db)
    
    # 展示今日记录
    show_today_records(db)
    
    # 展示月度汇总
    show_month_summary_detail(db)
    
    # 展示年度汇总
    show_year_summary_detail(db)
    
    # 展示CSV导出
    show_csv_export(db)
    
    # 结尾
    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)
    print("\n📱 运行完整应用 (GUI):")
    print("\n    pip install kivy")
    print("    python run.py")
    print("\n📂 项目结构:")
    print("    ledger/")
    print("    ├── main.py          # 主应用")
    print("    ├── database.py      # 数据管理")
    print("    ├── run.py           # 启动脚本")
    print("    ├── test_app.py      # 测试脚本")
    print("    ├── demo.py          # 演示脚本(本文件)")
    print("    └── ui/              # 界面模块")
    print("        ├── record_screen.py     # 记账页")
    print("        ├── summary_screen.py    # 总结页")
    print("        └── detail_screen.py     # 明细页")
    print("\n📦 数据存储:")
    print("    ~/.ledger_data/records.csv")
    print("\n🔄 打包为APK (手机端):")
    print("    pip install buildozer")
    print("    buildozer init")
    print("    buildozer android debug")
    print("=" * 60)


if __name__ == '__main__':
    main()
