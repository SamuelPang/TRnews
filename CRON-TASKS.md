# TRnews 定时任务说明

## 📅 完整定时任务配置

```bash
# 查看当前定时任务
crontab -l
```

---

## ⏰ 任务时间表

| 时间 | 任务 | 说明 |
|------|------|------|
| **每天 17:00** | TrendRadar 新闻生成 | 强制 AI 分析 |
| **每天 17:05** | TRnews 自动推送 | 推送新内容到 GitHub |
| **周日 09:00** | 周汇总新闻生成 | 周汇总版 + 强制 AI |
| **周日 09:05** | TRnews 周推送 | 推送周汇总内容 |

---

## 🔍 每个任务详解

### 任务 1：每天 17:00 - TrendRadar 新闻生成

```bash
0 17 * * * cd /home/sai/.openclaw/workspace-selfmng && bash skills/news-social-workflow/orchestrator.sh --force-ai >> memory/news-workflow/cron.log 2>&1
```

**做什么：**
1. ✅ 启动 TrendRadar 抓取全网热点
2. ✅ 强制 AI 分析（sig-pro 模型）
3. ✅ 生成 5 大分析板块
4. ✅ 生成各平台新闻稿（微信/微博/Twitter/知乎）
5. ✅ 生成小红书 + 今日头条稿件

**输出文件：**
```
data/2026-06-08/
├── ai-analysis-2026-06-08.md
├── news-2026-06-08.json
└── trendradar-html/*.html

reports/2026-06-08/
├── 2026-06-08-wechat.md
├── 2026-06-08-weibo.md
├── 2026-06-08-twitter.md
└── 2026-06-08-zhihu.md

platforms/
├── xiaohongshu/2026-06-08/
└── toutiao/2026-06-08/
```

**耗时：** 约 5 分钟

---

### 任务 2：每天 17:05 - TRnews 自动推送

```bash
5 17 * * * /home/sai/.openclaw/workspace-selfmng/TRnews/scripts/auto-push.sh >> TRnews/cron.log 2>&1
```

**做什么：**
1. ✅ 检查是否有新文件（数据/报告/稿件）
2. ✅ 拉取远程仓库最新状态
3. ✅ 添加新文件到 Git
4. ✅ Git 提交（带日期标签）
5. ✅ 推送到 GitHub

**检查逻辑：**
```bash
NEW_DATA=$(ls data/$DATE/*.md data/$DATE/*.json | wc -l)
NEW_REPORTS=$(ls reports/$DATE/*.md | wc -l)
NEW_PLATFORMS=$(ls platforms/*/$DATE/*.md | wc -l)
```

**如果无新文件：**
```
⚠️  没有新文件，跳过推送
```

**耗时：** 约 30 秒

---

### 任务 3：周日 09:00 - 周汇总新闻生成

```bash
0 9 * * 0 cd /home/sai/.openclaw/workspace-selfmng && bash skills/news-social-workflow/orchestrator.sh --weekly --force-ai >> memory/news-workflow/cron.log 2>&1
```

**做什么：**
1. ✅ 启动 TrendRadar 抓取
2. ✅ 强制 AI 分析
3. ✅ 生成周汇总版报告
4. ✅ 生成各平台稿件

**与日常版区别：**
- 数据范围更广（可能包含周末数据）
- 分析维度更详细
- 适合周总结

**耗时：** 约 5 分钟

---

### 任务 4：周日 09:05 - TRnews 周推送

```bash
5 9 * * 0 /home/sai/.openclaw/workspace-selfmng/TRnews/scripts/auto-push.sh >> TRnews/cron.log 2>&1
```

**做什么：**
1. ✅ 检查周汇总新文件
2. ✅ Git 提交
3. ✅ 推送到 GitHub

**耗时：** 约 30 秒

---

## 📊 完整执行流程

### 工作日（周一至周五）

```
17:00  TrendRadar 启动
       ↓
17:00  抓取全网热点（11 个平台）
       ↓
17:03  AI 分析（sig-pro 模型）
       ↓
17:04  生成新闻稿（4 个平台）
       ↓
17:04  生成小红书 + 头条稿件
       ↓
17:05  TRnews 自动推送启动
       ↓
17:05  检查新文件
       ↓
17:05  Git 提交
       ↓
17:05  推送到 GitHub
```

**总耗时：约 5 分钟**

---

### 周日

```
09:00  TrendRadar 周汇总启动
       ↓
09:00  抓取全网热点
       ↓
09:03  AI 分析（周汇总版）
       ↓
09:04  生成周汇总稿件
       ↓
09:05  TRnews 周推送启动
       ↓
09:05  Git 提交 + 推送
```

**总耗时：约 5 分钟**

---

## 📁 日志文件

| 日志 | 位置 | 说明 |
|------|------|------|
| 新闻工作流 | `memory/news-workflow/cron.log` | TrendRadar 执行日志 |
| TRnews 推送 | `TRnews/cron.log` | Git 推送日志 |
| TrendRadar | `memory/news-workflow/trendradar.log` | 详细抓取日志 |
| 稿件生成 | `memory/news-workflow/generate.log` | 稿件生成日志 |

---

## 🔧 手动执行

### 测试新闻生成
```bash
cd /home/sai/.openclaw/workspace-selfmng
bash skills/news-social-workflow/orchestrator.sh --force-ai
```

### 测试 TRnews 推送
```bash
/home/sai/.openclaw/workspace-selfmng/TRnews/scripts/auto-push.sh
```

### 查看定时任务
```bash
crontab -l
```

### 编辑定时任务
```bash
crontab -e
```

---

## 📈 监控

### 检查任务是否运行
```bash
# 查看最新日志
tail -20 /home/sai/.openclaw/workspace-selfmng/memory/news-workflow/cron.log
tail -20 /home/sai/.openclaw/workspace-selfmng/TRnews/cron.log

# 检查 Git 提交记录
cd /home/sai/.openclaw/workspace-selfmng/TRnews
git log --oneline -10
```

### 检查 GitHub 推送
```bash
# 访问仓库
https://github.com/SamuelPang/TRnews/commits/main
```

---

## ⚠️ 注意事项

1. **时间同步** — 确保服务器时间准确（Asia/Shanghai）
2. **网络稳定** — Git 推送需要网络连接
3. **存储空间** — 定期检查磁盘空间
4. **API Key** — 确保 AI API Key 有效
5. **GitHub 认证** — 如使用 HTTPS，需配置 credential helper

---

## 🎯 完整配置示例

```bash
# 完整 crontab 配置
cat > /tmp/trnews-crontab << 'EOF'
# TrendRadar 新闻稿自动化工作流 - 完整配置

# 每天下午 5:00 运行（强制 AI 分析，日常汇总模式）
0 17 * * * cd /home/sai/.openclaw/workspace-selfmng && bash skills/news-social-workflow/orchestrator.sh --force-ai >> memory/news-workflow/cron.log 2>&1

# 周日早上 9:00 运行（周汇总版，强制 AI 分析）
0 9 * * 0 cd /home/sai/.openclaw/workspace-selfmng && bash skills/news-social-workflow/orchestrator.sh --weekly --force-ai >> memory/news-workflow/cron.log 2>&1

# TRnews 自动推送 - 每次新闻生成后 5 分钟执行
5 17 * * * /home/sai/.openclaw/workspace-selfmng/TRnews/scripts/auto-push.sh >> TRnews/cron.log 2>&1

# TRnews 周推送 - 周日早上 9:05（周汇总后）
5 9 * * 0 /home/sai/.openclaw/workspace-selfmng/TRnews/scripts/auto-push.sh >> TRnews/cron.log 2>&1
EOF

crontab /tmp/trnews-crontab
```

---

*Last updated: 2026-06-08*
