#!/bin/bash
# TRnews 自动推送脚本

set -e

TRNEWS_DIR="/home/sai/.openclaw/workspace-selfmng/TRnews"
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)

echo "=========================================="
echo "📰 TRnews 自动推送"
echo "📅 日期：$DATE"
echo "⏰ 时间：$TIMESTAMP"
echo "=========================================="

cd "$TRNEWS_DIR"

# 1. 拉取最新
echo ""
echo "📥 步骤 1: 拉取远程仓库..."
git pull origin main 2>/dev/null || echo "首次推送，跳过拉取"

# 2. 检查是否有新文件
echo ""
echo "🔍 步骤 2: 检查新文件..."
NEW_DATA=$(ls data/$DATE/*.md data/$DATE/*.json 2>/dev/null | wc -l)
NEW_REPORTS=$(ls reports/$DATE/*.md 2>/dev/null | wc -l)
NEW_PLATFORMS=$(ls platforms/xiaohongshu/$DATE/*.md platforms/toutiao/$DATE/*.md 2>/dev/null | wc -l)

echo "   新数据文件：$NEW_DATA 个"
echo "   新报告文件：$NEW_REPORTS 个"
echo "   新平台稿件：$NEW_PLATFORMS 个"

if [ $((NEW_DATA + NEW_REPORTS + NEW_PLATFORMS)) -eq 0 ]; then
    echo "⚠️  没有新文件，跳过推送"
    exit 0
fi

# 3. 添加文件
echo ""
echo "➕ 步骤 3: 添加文件到 Git..."
git add .

# 4. 提交
echo ""
echo "💾 步骤 4: Git 提交..."
git commit -m "📰 $DATE 新闻报告更新" || echo "无变更"

# 5. 推送
echo ""
echo "🚀 步骤 5: 推送到 GitHub..."
git push origin main

echo ""
echo "=========================================="
echo "✅ 推送完成！"
echo "🔗 https://github.com/SamuelPang/TRnews"
echo "=========================================="
