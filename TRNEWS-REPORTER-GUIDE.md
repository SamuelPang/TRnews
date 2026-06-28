# TRnews 每日报告系统 📰

## 概述

TRnews 每日报告系统自动运行新闻稿自动化流程，并通过 Discord 发送执行报告。

## 报告内容

### 每日执行报告

报告包含以下信息：
- **TrendRadar 抓取状态** ✅/❌
- **AI 分析生成状态** ✅/❌
- **稿件生成数量** (篇)
- **Git 推送状态** ✅/❌
- **GitHub 仓库链接**
- **日志文件位置**

## 使用方法

### 手动运行

```bash
cd /home/sai/.openclaw/workspace-selfmng/TRnews
bash trnews-daily-reporter.sh
```

### 定时任务配置

| 时间 | 任务 | 频率 | 命令 |
|------|------|------|------|
| 17:00 | 新闻稿执行 + 报告 | 工作日 | `trnews-daily-reporter.sh` |
| 周日 09:00 | 周汇总版 | 每周日 | `complete-pipeline.sh --weekly` |

## 报告示例

```
📰 TRnews 新闻稿自动化系统 - 每日报告

📅 日期：2026-06-27
📊 状态：✅ 执行成功

🔧 执行状态:
  • TrendRadar 抓取：✅
  • AI 分析生成：✅
  • 稿件生成：7 篇
  • Git 推送：✅

📂 文件位置:
  • 报告：/home/sai/.openclaw/workspace-selfmng/TRnews/reports/2026-06-27/
  • 数据：/home/sai/.openclaw/workspace-selfmng/TRnews/data/2026-06-27/
  • 日志：/home/sai/.openclaw/workspace-selfmng/TRnews/logs/trnews-daily-reporter_20260627.log

🔗 GitHub: https://github.com/SamuelPang/TRnews

🤖 Wall-E-j 自动新闻系统
```

## 文件结构

```
TRnews/
├── trnews-daily-reporter.sh    # 每日报告脚本
├── scripts/
│   └── complete-pipeline.sh    # 完整流程脚本
├── logs/
│   └── trnews-daily-reporter_YYYYMMDD.log
├── data/
│   └── YYYY-MM-DD/
│       ├── ai-analysis-YYYY-MM-DD.md
│       ├── news-YYYY-MM-DD.json
│       └── trendradar-html/
├── reports/
│   └── YYYY-MM-DD/
│       ├── YYYY-MM-DD-wechat.md
│       ├── YYYY-MM-DD-weibo.md
│       ├── YYYY-MM-DD-twitter.md
│       ├── YYYY-MM-DD-zhihu.md
│       └── summary.md
└── platforms/
    └── (各平台稿件)
```

## 故障排查

### 流程执行失败

1. 查看详细日志:
   ```bash
   tail -100 logs/trnews-daily-reporter_YYYYMMDD.log
   ```

2. 检查 TrendRadar 数据源

3. 验证 AI 分析模块

### Discord 发送失败

1. 检查账号配置:
   ```bash
   openclaw status
   ```

2. 验证频道 ID

## 维护

### 查看定时任务状态

```bash
# 查看 crontab
crontab -l | grep TRnews

# 查看 cron 服务状态
systemctl status cron

# 查看最近执行日志
tail -50 logs/cron_trnews.log
```

### 手动测试

```bash
# 测试报告脚本
bash trnews-daily-reporter.sh

# 测试完整流程
bash scripts/complete-pipeline.sh
```

---

**维护者**: Wall-E-j 🤖
**最后更新**: 2026-06-27
