#!/usr/bin/env bash
#
# daily-naver-blog 배치를 cron → launchd(LaunchAgent)로 전환 설치.
# 멱등(idempotent): 여러 번 실행해도 안전. cron 항목 제거 + LaunchAgent 적재.
# initClaude/scripts/install-launchd.sh 아키텍처 준수.
#
set -euo pipefail

PROJECT_DIR="/Users/user/CursorProjects/ai-blog-notes"
PLIST_FILE="$PROJECT_DIR/scripts/launchd/com.user.daily-naver-blog.plist"
UID_NUM="$(id -u)"
LABEL="com.user.daily-naver-blog"

mkdir -p "$PROJECT_DIR/logs"
chmod +x "$PROJECT_DIR/scripts/daily-naver-blog.sh" "$PROJECT_DIR/tools/daily_naver_batch.py"

# 1) cron 항목 제거 (중복 실행 방지)
crontab -l 2>/dev/null | grep -v 'daily_naver_batch.py' | grep -v 'daily-naver-blog.sh' > /tmp/_cron.$$ || true
if [ -s /tmp/_cron.$$ ]; then
  crontab /tmp/_cron.$$
else
  crontab -r 2>/dev/null || true
fi
rm -f /tmp/_cron.$$

# 2) launchctl bootstrap 적재 (기존 등록이 있다면 bootout 후 재적재)
launchctl bootout "gui/$UID_NUM/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$UID_NUM" "$PLIST_FILE"
echo "loaded: $LABEL (매일 00:00 자정 실행)"

# 3) 검증
echo "--- launchctl list ---"
launchctl list | grep -iE 'daily-naver-blog' || echo "(등록 확인 실패)"
