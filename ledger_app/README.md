# 账本 - 极简本地记账应用

## 📱 项目概述

极简本地记账应用，基于 HTML + CSS + JavaScript 开发，使用 IndexedDB 存储数据。

### 功能特点

- ✅ **三页式设计**：记账、总结、明细
- ✅ **收入绿色 / 支出红色**
- ✅ **打勾式记账体验**
- ✅ **日/月/年多维度统计**
- ✅ **IndexedDB 本地存储**（数据可靠）
- ✅ **CSV 格式导出**
- ✅ **极简黑白灰设计**
- ✅ **响应式布局**（手机端优化）
- ✅ **支持深色模式**

---

## 🚀 快速开始（预览模式）

### 方法1：直接打开
双击 `index.html` 即可在浏览器中预览

### 方法2：本地服务器
```bash
# Windows
python -m http.server 8000

# Mac/Linux
./serve.sh
# 或
python3 -m http.server 8000
```

然后访问 http://localhost:8000

---

## 📦 打包成 Android APP

### 前置条件

1. **Node.js** (v18+)
   - 下载: https://nodejs.org/

2. **Android Studio**
   - 下载: https://developer.android.com/studio
   - 安装后需要配置 SDK

3. **Java** (JDK 17+)
   - Android Studio 自带

### 打包步骤

#### 一键打包（Windows）
```
双击 build_android.bat
```

#### 手动打包
```bash
# 1. 进入项目目录
cd ledger_app

# 2. 安装依赖
npm install

# 3. 初始化 Capacitor（首次）
npx cap init "账本" "com.ledger.app" --web-dir "."

# 4. 添加 Android 平台（首次）
npx cap add android

# 5. 同步文件
npx cap sync android

# 6. 打开 Android Studio
npx cap open android

# 7. 在 Android Studio 中打包
# Build -> Build APK(s)
```

### APK 文件位置
```
ledger_app/android/app/build/outputs/apk/debug/app-debug.apk
```

### 安装到手机
1. 将 APK 文件传输到手机
2. 允许"未知来源"安装
3. 点击 APK 安装

---

## 📦 打包成 iOS APP

### 前置条件
- **Mac 电脑**（必须）
- **Xcode** (最新版)
- **Apple 开发者账号** ($99/年)

### 打包步骤
```bash
# 1. 在 Mac 上复制项目
# 2. 安装依赖
npm install

# 3. 添加 iOS 平台
npx cap add ios

# 4. 同步文件
npx cap sync ios

# 5. 打开 Xcode
npx cap open ios

# 6. 在 Xcode 中配置并打包
```

---

## 💾 数据存储

### IndexedDB 存储位置
- **Android**: `/data/data/com.ledger.app/databases/`
- **iOS**: App 沙盒 `Library/WebKit/LocalStorage/`

### 数据特点
- ✅ 完全本地存储，不上传任何服务器
- ✅ 其他 APP 无法访问
- ✅ 清除浏览器数据不影响（打包成APP后）
- ⚠️ 卸载APP会清除数据

### 导出备份
- 在总结页或统计页点击"导出CSV"
- CSV 文件包含所有记录数据

---

## 📁 项目结构

```
ledger_app/
├── index.html              # 主页面
├── style.css               # 样式表
├── app.js                  # 核心逻辑（IndexedDB + 业务）
├── capacitor.config.ts     # Capacitor 配置
├── package.json            # 项目依赖
├── build_android.bat       # Android 打包脚本
├── build_ios.bat           # iOS 打包说明
├── serve.sh                # 预览服务器脚本
└── README.md               # 本文件
```

---

## 📊 CSV 格式

导出的 CSV 文件包含以下列：

| 列名 | 说明 | 示例 |
|------|------|------|
| id | 记录编号 | 1 |
| date | 日期 | 2024-01-15 |
| time | 时间 | 14:30 |
| source | 物品/来源 | 午餐 |
| amount | 金额 | 35.00 |
| type | 类型 | income/expense |
| checked | 完成状态 | true/false |

---

## 🎨 设计规范

### 颜色
- 主背景: `#f5f5f5`
- 卡片背景: `#ffffff`
- 主文字: `#1a1a1a`
- 次要文字: `#666666`
- 收入: `#1f7a1f`（绿色）
- 支出: `#c72c2c`（红色）

### 字体
- 中文: PingFang SC, Microsoft YaHei
- 英文: -apple-system, Helvetica Neue

### 单位
- 全部使用 `rem` / `em` / `vh` / `vw`
- 基准字号: 16px
- 最小支持: 320px 宽度

---

## 🔧 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| HTML5 | - | 页面结构 |
| CSS3 | - | 样式与布局 |
| JavaScript (ES6+) | - | 业务逻辑 |
| IndexedDB | - | 本地数据存储 |
| Capacitor | 5.x | APP 打包 |

---

## ⚠️ 注意事项

1. **Python 3.14 兼容性**
   - 本项目不依赖 Python，完全用 JavaScript 开发
   - 无版本兼容问题

2. **Android 版本要求**
   - 最低支持: Android 7.0 (API 24)
   - 推荐: Android 10+

3. **iOS 版本要求**
   - 最低支持: iOS 13.0

4. **数据安全**
   - 数据存在 APP 内部，其他应用无法访问
   - 建议定期导出 CSV 备份

---

## 📞 常见问题

### Q: 为什么不用 localStorage？
A: localStorage 容量小（5MB），且在某些情况下会被清除。IndexedDB 更可靠，容量更大（几百MB）。

### Q: 数据会上传到服务器吗？
A: 不会。所有数据都存在本地设备上，完全离线可用。

### Q: 换手机怎么办？
A: 用"导出CSV"功能导出数据，在新手机上手动添加记录（目前暂不支持CSV导入）。

### Q: 支持深色模式吗？
A: 支持。会自动跟随系统设置。

---

## 📝 更新日志

### v1.0.0 (2024-01-15)
- 初始版本发布
- 支持记账、总结、明细三大功能
- 支持日/月/年统计
- 支持 CSV 导出
- 支持深色模式

---

## 📄 许可证

MIT License

---

## 🙏 致谢

感谢使用本应用！
