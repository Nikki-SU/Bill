# 账本 - 个人记账应用

极简本地记账工具，基于 Python + Tkinter 开发。

## 功能特点

- ✅ 三页式设计：记账、总结、明细
- ✅ 收入(绿色) / 支出(红色) 区分
- ✅ 打勾式记账体验
- ✅ 日/月/年多维度统计
- ✅ CSV 格式数据存储
- ✅ 支持增删改查
- ✅ 无需安装任何第三方库

## 运行方法

### 方法1：双击运行（推荐）

双击 `启动.bat` 即可

### 方法2：命令行运行

```bash
python app_tkinter.py
```

或

```bash
python run_tkinter.py
```

## 系统要求

- Python 3.8 或更高版本
- Windows: Python 自带 Tkinter
- Mac/Linux: 通常也自带 Tkinter

## 数据存储

数据文件保存在：
- Windows: `C:\Users\你的用户名\.ledger_data\records.csv`
- Mac/Linux: `~/.ledger_data/records.csv`

## 文件说明

| 文件 | 说明 |
|------|------|
| `app_tkinter.py` | 主程序（单文件，包含所有功能） |
| `run_tkinter.py` | 启动脚本 |
| `启动.bat` | Windows 双击启动文件 |

## CSV 格式

CSV 文件包含以下列：
- id: 编号
- date: 日期 (YYYY-MM-DD)
- time: 时间 (HH:MM:SS)
- source: 来源/物品名称
- amount: 金额
- type: 类型 (income 收入 / expense 支出)
- checked: 是否完成 (true / false)
