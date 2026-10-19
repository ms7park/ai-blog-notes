#!/usr/bin/env bash
#
# daily-naver-blog LaunchAgent 등록 해제 스크립트
#
set -euo pipefail

UID_NUM="$(id -u)"
LABEL="com.user.daily-naver-blog"

DEST="$HOME/Library/LaunchAgents"

launchctl bootout "gui/$UID_NUM/$LABEL" 2>/dev/null || true
rm -f "$DEST/$LABEL.plist" 2>/dev/null || true
echo "unloaded: $LABEL"

# cron 항목도 정리
crontab -l 2>/dev/null | grep -v 'daily_naver_blog' | grep -v 'daily-naver-blog' > /tmp/_cron.$$ || true
if [ -s /tmp/_cron.$$ ]; then
  crontab /tmp/_cron.$$
else
  crontab -r 2>/dev/null || true
fi
rm -f /tmp/_cron.$$
echo "cron and launchd unregistered successfully."
