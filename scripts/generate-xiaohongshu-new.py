#!/usr/bin/env python3
"""
生成符合新规则的小红书文稿（5 篇独立笔记结构）
参考 6 月 8 日有流量版本的结构
"""

import json
import sqlite3
import os
import sys
from datetime import datetime

# 配置
WORKSPACE = "/home/sai/.openclaw/workspace-selfmng"
TRNEWS_DIR = f"{WORKSPACE}/TRnews"
TRENDRADAR_DIR = f"{WORKSPACE}/workspace/TrendRadar"
DATE = datetime.now().strftime("%Y-%m-%d")

AI_ANALYSIS_FILE = f"{TRNEWS_DIR}/data/{DATE}/ai-analysis-{DATE}.md"
NEWS_JSON_FILE = f"{TRNEWS_DIR}/data/{DATE}/news-{DATE}.json"
TRENDRADAR_DB = f"/home/sai/.openclaw/workspace/TrendRadar/output/news/{DATE}.db"

OUTPUT_DIR = f"{TRNEWS_DIR}/platforms/xiaohongshu/{DATE}"
OUTPUT_FILE = f"{OUTPUT_DIR}/{DATE}-xiaohongshu-new.md"


def read_ai_analysis():
    """读取 AI 分析文件"""
    if not os.path.exists(AI_ANALYSIS_FILE):
        print(f"❌ AI 分析文件不存在：{AI_ANALYSIS_FILE}")
        return None
    
    with open(AI_ANALYSIS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析各板块
    sections = {
        'core_trend': '',
        'public_opinion': '',
        'anomaly': '',
        'strategy': '',
        'source_overview': ''
    }
    
    current_section = None
    for line in content.split('\n'):
        if line.startswith('## 核心热点态势'):
            current_section = 'core_trend'
        elif line.startswith('## 舆论风向争议'):
            current_section = 'public_opinion'
        elif line.startswith('## 异动与弱信号'):
            current_section = 'anomaly'
        elif line.startswith('## 研判策略建议'):
            current_section = 'strategy'
        elif line.startswith('## 独立源点速览'):
            current_section = 'source_overview'
        elif line.startswith('#'):
            continue
        
        if current_section:
            sections[current_section] += line + '\n'
    
    return sections


def get_top_news():
    """获取 Top 新闻"""
    if not os.path.exists(TRENDRADAR_DB):
        print(f"⚠️ TrendRadar 数据库不存在：{TRENDRADAR_DB}")
        return []
    
    conn = sqlite3.connect(TRENDRADAR_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT platform_id, title, rank, url 
        FROM news_items 
        WHERE rank <= 10
        ORDER BY rank ASC
        LIMIT 20
    """)
    
    news = cursor.fetchall()
    conn.close()
    
    return news


def generate_note1_hot_daily(sections, top_news):
    """生成笔记 1：AI 热点日报"""
    core_trend = sections.get('core_trend', '')[:500]
    
    # 提取热点
    hotspots = []
    if '1.' in core_trend:
        lines = core_trend.split('\n')
        for line in lines:
            if '1.' in line or '2.' in line or '3.' in line:
                hotspots.append(line.strip())
    
    news_lines = []
    for platform, title, rank, url in top_news[:5]:
        news_lines.append(f"- 【{platform}】Rank {rank}: {title[:40]}")
    
    return f"""## 笔记 1：AI 热点日报

**封面标题：**
```
🤖 {DATE} 热点日报
AI 帮你抓重点
```

**封面图建议：**
- 风格：简洁 + 科技感
- 配色：蓝色系
- 元素：AI 图标 + 数据图表

**正文内容：**

```
📱 {DATE} 热点日报｜AI 帮你抓重点

宝子们！今天的热搜有点复杂，我用 AI 帮大家梳理了重点，3 分钟 get 全网热点✨

━━━━━━━━━━━━━━━━━━━━

🔥 今日最热：AI 资本化 + 美联储鹰派

1️⃣ AI 资本化成为核心引擎
💰 证监会支持 AI 上市
📈 00 后股民暴富案例
→ 科技股迎来新机遇

2️⃣ 美联储鹰派转向
🏦 沃什讲话细节发酵
📉 美股债双杀
→ 市场避险情绪浓厚

3️⃣ 芯片技术突破
🔬 液冷技术刷新纪录
📊 芯片指数逆市收涨
→ 技术红利释放

━━━━━━━━━━━━━━━━━━━━

💬 网友都在聊什么？

{chr(10).join(news_lines)}

━━━━━━━━━━━━━━━━━━━━

⚠️ 这些信号要注意

{sections.get('anomaly', '')[:300]}

━━━━━━━━━━━━━━━━━━━━

💡 AI 小建议

{sections.get('strategy', '')[:400]}

━━━━━━━━━━━━━━━━━━━━

📊 数据来源
TrendRadar AI 热点分析系统
监测 11 个平台：头条/百度/知乎/微博/抖音等

━━━━━━━━━━━━━━━━━━━━

💬 互动时间
你今天最关注哪个热点？评论区聊聊👇

#热点日报 #AI 分析 #今日热点 #科技新闻 #投资理财
```

**标签：**
```
#热点日报 #AI 分析 #今日热点 #科技新闻 #投资理财 #美联储 #芯片
```

**配图建议：**
```
图 1：封面（标题 + 日期）
图 2：核心热点 3 点（卡片式）
图 3：平台热点对比（表格）
图 4：风险提示（警示图标）
图 5：AI 建议（清单）
```

---
"""


def generate_note2_ai_capital(sections, top_news):
    """生成笔记 2：AI 资本化"""
    return f"""## 笔记 2：AI 资本化

**封面标题：**
```
💰 AI 上市潮来了！
00 后股民暴富
```

**封面图建议：**
- 风格：金融 + 科技感
- 元素：K 线图+AI 机器人
- 配色：绿色系（涨）

**正文内容：**

```
💰 AI 资本化成为核心引擎

家人们！今天 AI 监测到重大信号：
证监会支持 AI 上市 +00 后股民暴富案例 💥

━━━━━━━━━━━━━━━━━━━━

🔥 核心热点

【AI 资本化】
✓ 证监会支持 AI 企业上市
✓ 00 后股民暴富案例出现
✓ AI 并购政策即将落地

【市场反应】
📈 科技股受关注
📉 传统行业承压
💰 资金流向 AI 赛道

━━━━━━━━━━━━━━━━━━━━

💬 网友观点

【乐观派】
✓ AI 是未来，值得投资
✓ 政策利好，机会难得
✓ 00 后已经赚到了

【谨慎派】
✗ 估值过高，泡沫风险
✗ 技术不成熟，不确定性大
✗ 美联储加息，压制成长股

━━━━━━━━━━━━━━━━━━━━

💡 我的建议

【投资者】
▫️ 关注 AI 并购政策落地
▫️ 警惕美联储加息影响
▫️ 分散配置，降低风险

【打工人】
▫️ 关注 AI 行业就业机会
▫️ 学习 AI 技能提升竞争力
▫️ 理性看待暴富案例

━━━━━━━━━━━━━━━━━━━━

💬 互动时间

你会投资 AI 股票吗？
评论区说说你的看法👇

#AI 投资 #资本市场 #科技股 #00 后 #暴富
```

**标签：**
```
#AI 投资 #资本市场 #科技股 #00 后 #暴富 #投资理财 #股票
```

**配图建议：**
```
图 1：封面（标题 + 表情）
图 2：核心热点（对比图）
图 3：网友观点（两派）
图 4：数据监测（图表）
图 5：建议清单
```

---
"""


def generate_note3_investment_warning(sections, top_news):
    """生成笔记 3：投资警示"""
    return f"""## 笔记 3：投资警示

**封面标题：**
```
📈 {DATE} 投资警示
这三个风险点要注意
```

**封面图建议：**
- 风格：金融 + 警示
- 配色：红色系
- 元素：图表 + 警告图标

**正文内容：**

```
📈 {DATE} 投资警示

今天 AI 监测到 3 个重要信号，投资者一定要关注⚠️

━━━━━━━━━━━━━━━━━━━━

⚠️ 风险 1：美联储加息压制

【AI 信号】
美联储鹰派转向维持榜首高位横盘

【关键信息】
🏦 沃什讲话细节持续发酵
📉 美股债双杀
💰 成长股估值承压

【建议】
警惕加息对科技股的影响📉

━━━━━━━━━━━━━━━━━━━━

⚠️ 风险 2：AI 文章同质化

【AI 信号】
AI 代码认可度高与 AI 文章同质化形成悖论

【关键信息】
🤖 AI 技术认可度高
📝 AI 内容质量下降
⚖️ 认知冲突明显

【建议】
关注真正有技术的企业⚠️

━━━━━━━━━━━━━━━━━━━━

⚠️ 风险 3：芯片分化加剧

【AI 信号】
芯片指数逆市收涨与黄金下挫形成对比

【关键信息】
🔬 液冷技术刷新纪录
📊 美股芯片反弹
📉 日韩熔断

【建议】
✅ 关注技术突破企业
✅ 警惕泡沫风险
✅ 分散配置

━━━━━━━━━━━━━━━━━━━━

💡 AI 策略建议

【短期】
▫️ 关注 AI 并购政策
▫️ 警惕加息影响
▫️ 增加现金储备

【中期】
▫️ 布局 AI 产业链
▫️ 关注数字资产保护
▫️ 分散地域配置

━━━━━━━━━━━━━━━━━━━━

💬 互动时间

你今天有关注哪些投资热点？
评论区聊聊👇

#投资理财 #股市分析 #美联储 #AI 投资
```

**标签：**
```
#投资理财 #股市分析 #美联储 #AI 投资 #避险 #投资策略
```

**配图建议：**
```
图 1：封面（警示图标）
图 2：风险 1（美联储）
图 3：风险 2（AI 同质化）
图 4：风险 3（芯片）
图 5：策略建议（清单）
```

---
"""


def generate_note4_digital_asset(sections, top_news):
    """生成笔记 4：数字资产"""
    return f"""## 笔记 4：数字资产

**封面标题：**
```
🎮 游戏账号能继承了？
数字资产法律确权
```

**封面图建议：**
- 风格：法律 + 科技
- 元素：法槌 + 游戏手柄
- 配色：紫色系

**正文内容：**

```
🎮 游戏账号能继承了？

今天 AI 监测到一个重要判决：
母亲继承离世儿子 87 个游戏账号，法院支持 ⚖️

━━━━━━━━━━━━━━━━━━━━

📰 事件回顾

【案件背景】
母亲欲继承离世儿子 87 个游戏账号
平台拒绝，法院支持母亲

【法律意义】
✓ 数字资产首次获司法支持
✓ 格式条款被认定无效
✓ 新兴权益保护趋势

━━━━━━━━━━━━━━━━━━━━

💬 网友热议

【支持方】
✓ 数字资产也是财产
✓ 应该可以继承
✓ 保护家属权益

【担忧方】
✗ 账号安全问题
✗ 隐私保护问题
✗ 平台规则冲突

━━━━━━━━━━━━━━━━━━━━

💡 我的建议

【玩家】
▫️ 记录账号信息
▫️ 告知家属账号情况
▫️ 考虑写入遗嘱

【平台】
▫️ 明确账号继承政策
▫️ 提供家属继承流程
▫️ 保护隐私和安全

━━━━━━━━━━━━━━━━━━━━

💬 互动时间

你有考虑过数字资产继承吗？
评论区说说你的想法👇

#数字资产 #游戏账号 #法律 #继承
```

**标签：**
```
#数字资产 #游戏账号 #法律 #继承 #遗嘱 #玩家 #权益保护
```

**配图建议：**
```
图 1：封面（法槌 + 游戏）
图 2：事件回顾（时间线）
图 3：网友观点（两派）
图 4：数据监测（图表）
图 5：建议清单
```

---
"""


def generate_note5_ai_tool(sections, top_news):
    """生成笔记 5：AI 工具推荐"""
    return f"""## 笔记 5：AI 工具推荐

**封面标题：**
```
🤖 TrendRadar AI
帮你抓全网热点
```

**封面图建议：**
- 风格：科技感
- 元素：AI 机器人 + 热点图标
- 配色：蓝色 + 紫色

**正文内容：**

```
🤖 这个 AI 工具太香了！
帮你抓全网热点，每天 3 分钟 get 重点

最近发现一个超好用的 AI 热点分析工具
TrendRadar AI 🌟

━━━━━━━━━━━━━━━━━━━━

✨ 它能做什么？

1️⃣ 全网监测
📊 11 个平台实时抓取
- 今日头条
- 百度热搜
- 知乎
- 微博
- 抖音
- 华尔街见闻
- 财联社
- 澎湃新闻
- B 站热搜
- 凤凰网
- 贴吧

2️⃣ AI 深度分析
🧠 5 大分析板块：
- 核心热点态势
- 舆论风向争议
- 异动与弱信号
- 研判策略建议
- 独立源点速览

3️⃣ 自动整理
📝 一键生成：
- 深度报告
- 投资警示
- 职场分析
- 社会热点追踪

━━━━━━━━━━━━━━━━━━━━

💡 使用场景

【打工人】
▫️ 通勤路上 3 分钟 get 热点
▫️ 了解行业动态
▫️ 避免聊天没话题

【投资者】
▫️ 捕捉市场信号
▫️ 发现投资机会
▫️ 规避潜在风险

【内容创作者】
▫️ 找选题灵感
▫️ 追热点创作
▫️ 提高内容质量

━━━━━━━━━━━━━━━━━━━━

🌟 推荐理由

✓ 免费使用
✓ 数据全面
✓ 分析深度
✓ 更新及时
✓ 无广告干扰

━━━━━━━━━━━━━━━━━━━━

💬 互动时间

你平时怎么了解热点？
有没有好用的工具推荐？👇

#AI 工具 #热点分析 #效率工具
```

**标签：**
```
#AI 工具 #热点分析 #效率工具 #工具推荐 #TrendRadar
```

**配图建议：**
```
图 1：封面（AI 机器人）
图 2：11 个平台（logo 墙）
图 3：5 大分析板块（卡片）
图 4：使用场景（4 个图标）
图 5：实测效果（数据）
```

---
"""


def generate_publish_guide():
    """生成发布建议"""
    return f"""## 发布建议

### 发布节奏
```
早上 8:00 - 笔记 1（AI 热点日报）
         → 通勤时段，吸引流量

中午 12:00 - 笔记 2（AI 资本化）
         → 午休时间，投资者活跃

下午 16:00 - 笔记 3（投资警示）
         → 收盘后，投资者活跃

晚上 20:00 - 笔记 4（数字资产）
         → 休闲阅读时段

晚上 22:00 - 笔记 5（AI 工具推荐）
         → 睡前种草
```

### 配图规范
```
✅ 尺寸：3:4（1242x1656px）
✅ 格式：JPG/PNG
✅ 数量：每篇 4-6 张
✅ 风格：统一配色 + 字体
```

### 互动策略
```
✅ 每篇设置互动问题
✅ 及时回复评论（前 2 小时）
✅ 引导点赞 + 收藏
✅ 使用热门话题标签
✅ 适当使用 emoji 增加可读性
```

### 注意事项
```
⚠️ 避免过度营销
⚠️ 内容真实有价值
⚠️ 遵守平台规则
⚠️ 不发布敏感内容
⚠️ 保持更新频率
```
"""


def main():
    print(f"==========================================")
    print(f"📱 生成小红书文稿（新结构）")
    print(f"📅 日期：{DATE}")
    print(f"==========================================")
    
    # 读取 AI 分析
    print("\n📖 读取 AI 分析...")
    sections = read_ai_analysis()
    if not sections:
        print("❌ AI 分析读取失败")
        return 1
    
    print(f"✅ AI 分析读取成功")
    
    # 获取 Top 新闻
    print("\n🔍 获取 Top 新闻...")
    top_news = get_top_news()
    print(f"✅ 获取到 {len(top_news)} 条新闻")
    
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 生成文稿
    print("\n✍️ 生成文稿...")
    content = "# 小红书图文稿件\n\n---\n\n"
    content += generate_note1_hot_daily(sections, top_news)
    content += generate_note2_ai_capital(sections, top_news)
    content += generate_note3_investment_warning(sections, top_news)
    content += generate_note4_digital_asset(sections, top_news)
    content += generate_note5_ai_tool(sections, top_news)
    content += generate_publish_guide()
    
    # 写入文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 文稿生成成功：{OUTPUT_FILE}")
    print(f"📊 文件大小：{os.path.getsize(OUTPUT_FILE)} 字节")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
