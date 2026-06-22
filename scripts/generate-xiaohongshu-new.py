#!/usr/bin/env python3
"""
生成符合新规则的小红书文稿（5 篇独立笔记结构）
根据当天 AI 分析动态生成内容
"""

import json
import sqlite3
import os
import sys
import re
from datetime import datetime

# 配置
WORKSPACE = "/home/sai/.openclaw/workspace-selfmng"
TRNEWS_DIR = f"{WORKSPACE}/TRnews"
TRENDRADAR_DIR = "/home/sai/.openclaw/workspace/TrendRadar"
DATE = datetime.now().strftime("%Y-%m-%d")

AI_ANALYSIS_FILE = f"{TRNEWS_DIR}/data/{DATE}/ai-analysis-{DATE}.md"
NEWS_JSON_FILE = f"{TRNEWS_DIR}/data/{DATE}/news-{DATE}.json"
TRENDRADAR_DB = f"{TRENDRADAR_DIR}/output/news/{DATE}.db"

OUTPUT_DIR = f"{TRNEWS_DIR}/platforms/xiaohongshu/{DATE}"
OUTPUT_FILE = f"{OUTPUT_DIR}/{DATE}-xiaohongshu-new.md"


def read_ai_analysis():
    """读取 AI 分析文件并解析各板块"""
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


def extract_hotspots(core_trend):
    """从核心热点态势中提取热点"""
    hotspots = []
    
    # 提取微观领域的热点
    micro_match = re.search(r'【微观领域】\n(.*?)(?=##|\Z)', core_trend, re.DOTALL)
    if micro_match:
        micro_text = micro_match.group(1)
        # 提取数字列表项
        items = re.findall(r'\d+\. (.*?)(?=\n\d+\.|\n\n|##|\Z)', micro_text, re.DOTALL)
        for item in items:
            item = item.strip()
            if item:
                hotspots.append(item[:150])  # 限制长度
    
    return hotspots if hotspots else ["热点内容待提取"]


def extract_strategy(strategy_text):
    """提取策略建议"""
    suggestions = []
    
    # 提取数字列表项
    items = re.findall(r'\d+\. (.*?)(?=\n\d+\.|\n\n|##|\Z)', strategy_text, re.DOTALL)
    for item in items:
        item = item.strip()
        if item:
            suggestions.append(item[:200])
    
    return suggestions if suggestions else ["建议内容待提取"]


def extract_anomaly(anomaly_text):
    """提取异动与弱信号"""
    signals = []
    
    # 提取关键信号
    patterns = [
        r'【跨平台温差】(.*?)(?=【|##|\Z)',
        r'【轨迹突变】(.*?)(?=【|##|\Z)',
        r'【弱信号捕捉】(.*?)(?=##|\Z)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, anomaly_text, re.DOTALL)
        if match:
            signal = match.group(1).strip()
            if signal:
                signals.append(signal[:200])
    
    return signals if signals else ["信号内容待提取"]


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


def generate_note1_hot_daily(sections, top_news, hotspots, suggestions):
    """生成笔记 1：AI 热点日报 - 根据当天 AI 分析动态生成"""
    
    # 构建热点列表
    hotspots_text = ""
    for i, hotspot in enumerate(hotspots[:3], 1):
        # 提取热点关键词
        keywords = re.findall(r'「(.*?)」', hotspot)
        keyword_str = " + ".join(keywords[:2]) if keywords else "热点"
        
        hotspots_text += f"""
{i}️⃣ {keyword_str}
"""
        # 从热点描述中提取关键信息
        if "世界杯" in hotspot:
            hotspots_text += """🏆 世界杯话题持续霸榜
📺 国民级关注度
→ 体育情绪价值顶格

"""
        elif "AI" in hotspot or "英伟达" in hotspot or "芯片" in hotspot:
            hotspots_text += """💰 AI 资本周期关注
📊 财务匹配争议
→ 技术泡沫论调抬头

"""
        elif "马宁" in hotspot or "裁判" in hotspot:
            hotspots_text += """🇨🇳 中国裁判高位横盘
🏅 民族自豪感
→ 国民关注度持续

"""
        else:
            hotspots_text += """📊 热度持续
📈 多平台高位
→ 话题发酵中

"""
    
    news_lines = []
    for platform, title, rank, url in top_news[:5]:
        news_lines.append(f"- 【{platform}】Rank {rank}: {title[:40]}")
    
    # 构建策略建议
    strategy_text = ""
    for i, suggestion in enumerate(suggestions[:3], 1):
        # 根据建议类型添加 emoji
        if "投资者" in suggestion:
            strategy_text += f"👉 {i}. {suggestion}\n"
        elif "品牌方" in suggestion:
            strategy_text += f"👉 {i}. {suggestion}\n"
        elif "公众" in suggestion:
            strategy_text += f"👉 {i}. {suggestion}\n"
        else:
            strategy_text += f"👉 {i}. {suggestion}\n"
    
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

🔥 今日最热：{hotspots[0][:30] if hotspots else '热点待提取'}

{hotspots_text}━━━━━━━━━━━━━━━━━━━━

💬 网友都在聊什么？

{chr(10).join(news_lines)}

━━━━━━━━━━━━━━━━━━━━

⚠️ 这些信号要注意

{sections.get('anomaly', '')[:400]}

━━━━━━━━━━━━━━━━━━━━

💡 AI 小建议

{strategy_text}━━━━━━━━━━━━━━━━━━━━

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
#热点日报 #AI 分析 #今日热点 #科技新闻 #投资理财
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


def generate_note2_topic(sections, hotspots, topic_name, topic_desc):
    """生成专题笔记"""
    return f"""## 笔记 2：{topic_name}

**封面标题：**
```
💡 {topic_name}
{topic_desc[:20]}
```

**封面图建议：**
- 风格：科技感
- 元素：相关图标
- 配色：蓝色系

**正文内容：**

```
💡 {topic_name}

家人们！今天 AI 监测到重要信号：
{topic_desc[:50]} 💥

━━━━━━━━━━━━━━━━━━━━

🔥 核心热点

{sections.get('core_trend', '')[:400]}

━━━━━━━━━━━━━━━━━━━━

💬 网友观点

【乐观派】
✓ 长期看好
✓ 政策利好
✓ 机会难得

【谨慎派】
✗ 估值风险
✗ 不确定性大
✗ 需要观望

━━━━━━━━━━━━━━━━━━━━

💡 我的建议

【投资者】
▫️ 关注政策落地
▫️ 分散配置
▫️ 降低风险

【打工人】
▫️ 学习相关技能
▫️ 提升竞争力
▫️ 理性看待

━━━━━━━━━━━━━━━━━━━━

💬 互动时间

你怎么看这个话题？
评论区说说你的看法👇

#{topic_name.replace(' ', '')} #投资 #趋势
```

**标签：**
```
#{topic_name.replace(' ', '#')} #趋势 #分析
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


def generate_note3_investment_warning(sections, suggestions):
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

⚠️ 风险 1：AI 板块风险

【AI 信号】
AI 资本支出信贷饱和风险

【关键信息】
🤖 技术泡沫论调抬头
📈 财务不匹配争议
⚖️ 机构博弈加剧

【建议】
警惕纯应用层 AI 泡沫📉

━━━━━━━━━━━━━━━━━━━━

⚠️ 风险 2：地缘政治风险

【AI 信号】
地缘政治对能源/航运影响

【关键信息】
🌍 中东局势关注
🚢 能源价格波动
⚠️ 供应链冲击

【建议】
规避相关高风险资产⚠️

━━━━━━━━━━━━━━━━━━━━

⚠️ 风险 3：市场波动风险

【AI 信号】
财报季前夕市场博弈升级

【关键信息】
📊 英伟达股东大会
💰 芯片超级周期
📉 回调机会

【建议】
✅ 关注回调机会
✅ 分散配置
✅ 降低风险敞口

━━━━━━━━━━━━━━━━━━━━

💡 AI 策略建议

【短期】
▫️ 警惕 AI 资本支出风险
▫️ 关注芯片回调机会
▫️ 增加现金储备

【中期】
▫️ 布局真正有技术的企业
▫️ 关注地缘政治影响
▫️ 分散地域配置

━━━━━━━━━━━━━━━━━━━━

💬 互动时间

你今天有关注哪些投资热点？
评论区聊聊👇

#投资理财 #股市分析 #避险 #投资策略
```

**标签：**
```
#投资理财 #股市分析 #避险 #投资策略 #基金 #股票
```

**配图建议：**
```
图 1：封面（警示图标）
图 2：风险 1（AI 板块）
图 3：风险 2（地缘政治）
图 4：风险 3（市场波动）
图 5：策略建议（清单）
```

---
"""


def generate_note4_social_topic(sections, hotspots):
    """生成笔记 4：社会话题"""
    return f"""## 笔记 4：社会话题

**封面标题：**
```
🌍 {DATE} 社会关注
这些话题值得聊
```

**封面图建议：**
- 风格：社会 + 人文
- 元素：人群 + 话题图标
- 配色：暖色系

**正文内容：**

```
🌍 {DATE} 社会话题

今天 AI 监测到重要社会话题：
{hotspots[0][:40] if hotspots else '话题待提取'} 💬

━━━━━━━━━━━━━━━━━━━━

📰 热点回顾

【核心热点】
{sections.get('core_trend', '')[:300]}

【情绪光谱】
{sections.get('public_opinion', '')[:300]}

━━━━━━━━━━━━━━━━━━━━

💬 网友热议

【支持方】
✓ 长期看好
✓ 值得关注
✓ 积极影响

【担忧方】
✗ 潜在风险
✗ 需要观察
✗ 谨慎态度

━━━━━━━━━━━━━━━━━━━━

💡 我的建议

【公众】
▫️ 关注官方信息
▫️ 理性看待话题
▫️ 做好防护准备

【品牌方】
▫️ 关注社会情绪
▫️ 避免蹭热点
▫️ 正面引导

━━━━━━━━━━━━━━━━━━━━

💬 互动时间

你怎么看这个话题？
评论区说说你的想法👇

#社会话题 #热点追踪 #民生关注
```

**标签：**
```
#社会话题 #热点追踪 #民生关注 #话题讨论
```

**配图建议：**
```
图 1：封面（话题图标）
图 2：热点回顾（时间线）
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

中午 12:00 - 笔记 2（专题深度）
         → 午休时间，深度阅读

下午 16:00 - 笔记 3（投资警示）
         → 收盘后，投资者活跃

晚上 20:00 - 笔记 4（社会话题）
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
    
    # 提取热点和建议
    print("\n🔍 提取热点和建议...")
    hotspots = extract_hotspots(sections.get('core_trend', ''))
    suggestions = extract_strategy(sections.get('strategy', ''))
    anomalies = extract_anomaly(sections.get('anomaly', ''))
    
    print(f"✅ 提取到 {len(hotspots)} 个热点")
    print(f"✅ 提取到 {len(suggestions)} 条建议")
    
    # 获取 Top 新闻
    print("\n🔍 获取 Top 新闻...")
    top_news = get_top_news()
    print(f"✅ 获取到 {len(top_news)} 条新闻")
    
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 生成文稿
    print("\n✍️ 生成文稿...")
    content = "# 小红书图文稿件\n\n---\n\n"
    
    # 笔记 1：AI 热点日报（动态生成）
    content += generate_note1_hot_daily(sections, top_news, hotspots, suggestions)
    
    # 笔记 2：专题深度（根据热点主题）
    topic_name = hotspots[0][:20] if hotspots else "专题深度"
    topic_desc = hotspots[0] if hotspots else "今日热点"
    content += generate_note2_topic(sections, hotspots, topic_name, topic_desc)
    
    # 笔记 3：投资警示
    content += generate_note3_investment_warning(sections, suggestions)
    
    # 笔记 4：社会话题
    content += generate_note4_social_topic(sections, hotspots)
    
    # 笔记 5：AI 工具推荐
    content += generate_note5_ai_tool(sections, top_news)
    
    # 发布建议
    content += generate_publish_guide()
    
    # 写入文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 文稿生成成功：{OUTPUT_FILE}")
    print(f"📊 文件大小：{os.path.getsize(OUTPUT_FILE)} 字节")
    
    # 显示生成的热点
    print("\n📋 生成的热点内容：")
    for i, hotspot in enumerate(hotspots[:3], 1):
        print(f"  {i}. {hotspot[:60]}...")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
