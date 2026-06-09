#!/bin/bash
# 检查新闻稿生成各阶段的数据传递

DATE=$(date +%Y-%m-%d)
TRENDRADAR_DIR="/home/sai/.openclaw/workspace/TrendRadar"
NEWS_DIR="/home/sai/.openclaw/workspace-selfmng/skills/news-social-workflow"
TRNEWS_DIR="/home/sai/.openclaw/workspace-selfmng/TRnews"

echo "=========================================="
echo "📊 新闻稿生成数据传递检查"
echo "📅 日期：$DATE"
echo "=========================================="

echo ""
echo "阶段 1: TrendRadar 抓取"
echo "━━━━━━━━━━━━━━━━━━━━━━"
HTML_COUNT=$(ls $TRENDRADAR_DIR/output/html/$DATE/*.html 2>/dev/null | wc -l)
DB_EXISTS=$(test -f $TRENDRADAR_DIR/output/news/$DATE.db && echo "✅ 存在" || echo "❌ 不存在")
echo "HTML 报告：$HTML_COUNT 个"
echo "数据库：$DB_EXISTS"

echo ""
echo "阶段 2: AI 分析提取"
echo "━━━━━━━━━━━━━━━━━━━━━━"
AI_FILE="$TRNEWS_DIR/data/$DATE/ai-analysis-2026-06-09.md"
if [ -f "$AI_FILE" ]; then
    SECTIONS=$(grep "^## " $AI_FILE | wc -l)
    echo "AI 分析文件：✅ 存在"
    echo "分析板块数：$SECTIONS"
    echo "板块列表:"
    grep "^## " $AI_FILE | sed 's/^/  - /'
else
    echo "AI 分析文件：❌ 不存在"
fi

echo ""
echo "阶段 3: 新闻详情匹配"
echo "━━━━━━━━━━━━━━━━━━━━━━"
NEWS_JSON="$TRNEWS_DIR/data/$DATE/news-$DATE.json"
if [ -f "$NEWS_JSON" ]; then
    NEWS_COUNT=$(python3 -c "import json; data=json.load(open('$NEWS_JSON')); print(len(data.get('news_details', [])))")
    echo "新闻详情文件：✅ 存在"
    echo "匹配新闻数：$NEWS_COUNT"
else
    echo "新闻详情文件：❌ 不存在"
fi

echo ""
echo "阶段 4: 稿件生成"
echo "━━━━━━━━━━━━━━━━━━━━━━"
PLATFORMS=("xiaohongshu" "toutiao" "wechat" "weibo" "twitter" "zhihu")
for platform in "${PLATFORMS[@]}"; do
    FILE="$TRNEWS_DIR/platforms/$platform/$DATE/2026-06-09-$platform.md"
    if [ -f "$FILE" ]; then
        LINES=$(wc -l < $FILE)
        echo "$platform: ✅ 存在 ($LINES 行)"
    else
        echo "$platform: ❌ 不存在"
    fi
done

echo ""
echo "=========================================="
echo "🔍 数据依赖检查"
echo "=========================================="

echo ""
echo "检查 1: AI 分析是否 100% 来自 HTML"
HTML_AI=$(grep -c "ai-block" $TRENDRADAR_DIR/output/html/$DATE/*.html 2>/dev/null | tail -1)
AI_FILE_AI=$(grep -c "## " $AI_FILE 2>/dev/null || echo 0)
echo "  HTML 中的 AI 区块：$HTML_AI"
echo "  AI 分析文件板块：$AI_FILE_AI"

echo ""
echo "检查 2: 稿件是否包含非 AI 内容"
XHS_FILE="$TRNEWS_DIR/platforms/xiaohongshu/$DATE/2026-06-09-xiaohongshu.md"
if [ -f "$XHS_FILE" ]; then
    TEMPLATE_KEYWORDS=$(grep -c "封面图建议\|配图建议\|发布建议\|注意事项" $XHS_FILE 2>/dev/null || echo 0)
    echo "  小红书稿件中的模板关键词：$TEMPLATE_KEYWORDS"
    if [ $TEMPLATE_KEYWORDS -gt 0 ]; then
        echo "  ⚠️  稿件包含非 AI 生成的模板内容"
    else
        echo "  ✅ 稿件 100% 来自 AI 分析"
    fi
fi

echo ""
echo "=========================================="
echo "✅ 检查完成"
echo "=========================================="
