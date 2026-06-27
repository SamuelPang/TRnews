#!/bin/bash
# TRnews 每日报告脚本
# 每天自动运行，发送新闻稿执行报告到 Discord

set -e

# 修复 cron 的 PATH 问题
export PATH="/home/sai/.npm-global/bin:$PATH"

TRNEWS_DIR="/home/sai/.openclaw/workspace-selfmng/TRnews"
DATE=$(date +%Y%m%d)
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_DIR="$TRNEWS_DIR/logs"
LOG_FILE="$LOG_DIR/trnews-daily-reporter_${DATE}.log"

# Discord 配置
DISCORD_ACCOUNT="wallej"
DISCORD_TARGET="channel:1477848399028945078"  # Current channel ID

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$LOG_FILE"
}

# 发送 Discord 报告
send_discord_report() {
    local message="$1"
    
    log "发送 Discord 报告..."
    
    openclaw message send \
        --channel discord \
        --account "$DISCORD_ACCOUNT" \
        --target "$DISCORD_TARGET" \
        --message "$message" 2>&1 | tee -a "$LOG_FILE"
    
    log "✅ Discord 报告发送完成"
}

# 生成 TRnews 执行报告
generate_trnews_report() {
    log "========================================"
    log "生成 TRnews 执行报告"
    log "========================================"
    
    local cron_log="$TRNEWS_DIR/complete-cron.log"
    local summary_file="$TRNEWS_DIR/reports/$DATE/summary.md"
    local ai_analysis="$TRNEWS_DIR/data/$DATE/ai-analysis-$DATE.md"
    
    # 运行完整流程
    log "开始运行 TRnews 完整流程..."
    
    local exit_code=0
    bash "$TRNEWS_DIR/scripts/complete-pipeline.sh" >> "$LOG_FILE" 2>&1 || exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        log_error "TRnews 流程执行失败，退出码：$exit_code"
    else
        log "✅ TRnews 流程执行成功"
    fi
    
    # 解析执行结果
    local status="✅ 执行成功"
    local trendradar_status="❌"
    local ai_analysis_status="❌"
    local稿件数量=0
    local git_push_status="❌"
    
    # 检查 TrendRadar 状态
    if grep -q "✅ TrendRadar 运行完成" "$LOG_FILE" 2>/dev/null; then
        trendradar_status="✅"
    fi
    
    # 检查 AI 分析状态
    if [ -f "$ai_analysis" ]; then
        ai_analysis_status="✅"
        local sections=$(grep "^## " "$ai_analysis" 2>/dev/null | wc -l || echo "0")
        log "AI 分析板块数：$sections"
    fi
    
    # 统计稿件数量
    local article_count=0
    if [ -d "$TRNEWS_DIR/reports/$DATE" ]; then
        article_count=$(ls "$TRNEWS_DIR/reports/$DATE/"*.md 2>/dev/null | wc -l || echo "0")
    fi
    
    # 检查 Git 推送
    if grep -q "✅ 推送完成" "$LOG_FILE" 2>/dev/null; then
        git_push_status="✅"
    fi
    
    # 获取 GitHub 链接
    local github_url="https://github.com/SamuelPang/TRnews"
    if grep -oP 'https://github.com/[^"\s]+' "$LOG_FILE" 2>/dev/null | tail -1 | grep -q "github.com"; then
        github_url=$(grep -oP 'https://github.com/[^"\s]+' "$LOG_FILE" 2>/dev/null | tail -1)
    fi
    
    # 构建报告消息
    local message="📰 TRnews 新闻稿自动化系统 - 每日报告

📅 日期：$(date '+%Y-%m-%d')
📊 状态：$status

🔧 执行状态:
  • TrendRadar 抓取：$trendradar_status
  • AI 分析生成：$ai_analysis_status
  • 稿件生成：$article_count 篇
  • Git 推送：$git_push_status

📂 文件位置:
  • 报告：$TRNEWS_DIR/reports/$DATE/
  • 数据：$TRNEWS_DIR/data/$DATE/
  • 日志：$LOG_FILE

🔗 GitHub: $github_url

🤖 Wall-E-j 自动新闻系统"

    # 发送报告
    send_discord_report "$message"
    
    log "✅ TRnews 报告已发送"
    return $exit_code
}

# 主函数
main() {
    # 确保日志目录存在
    mkdir -p "$LOG_DIR"
    
    log "========================================"
    log "TRnews 每日报告器启动"
    log "时间：$TIMESTAMP"
    log "========================================"
    
    generate_trnews_report
    exit $?
}

main
