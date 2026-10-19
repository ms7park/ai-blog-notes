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

DEST="$HOME/Library/LaunchAgents"
BOOTSTRAP_TARGET="$PLIST_FILE"

# 1) LaunchAgent plist 설치 (영속성 확보)
if [ -w "$DEST" ]; then
  cp "$PLIST_FILE" "$DEST/$LABEL.plist"
  BOOTSTRAP_TARGET="$DEST/$LABEL.plist"
  echo "✅ $DEST/$LABEL.plist 복사 완료 (재부팅 시 자동 로드 영구 보장)"
else
  echo "⚠️ $DEST 디렉토리에 일반 사용자 쓰기 권한이 없습니다. (소유자: $(ls -ld "$DEST" | awk '{print $3}'))"
  echo "   재부팅 후 LaunchAgent 자동 로드를 영구 보장하려면 아래 명령어를 터미널에서 1회 실행하세요:"
  echo "   👉 sudo chown -R $(id -un):staff ~/Library/LaunchAgents && ./scripts/install-launchd.sh"
fi

# 2) launchctl bootstrap 적재 (기존 등록이 있다면 bootout 후 재적재)
launchctl bootout "gui/$UID_NUM/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$UID_NUM" "$BOOTSTRAP_TARGET"
echo "✅ launchd 적재 완료: $LABEL (매일 00:00 자정 및 절전 해제 시 실행)"

# 3) Crontab 이중 안전망(Dual Backup) 등록
#    - 시스템 재부팅 후 LaunchAgent가 풀리는 상황을 완벽 방지하는 보조 스케줄러
#    - 배치 내부 fcntl 파일 락 및 중복 체크로 동시/중복 실행 충돌 방지
crontab -l 2>/dev/null | grep -v 'daily_naver_batch.py' | grep -v 'daily-naver-blog.sh' > /tmp/_cron.$$ || true
echo "0 0 * * * $PROJECT_DIR/scripts/daily-naver-blog.sh >> $PROJECT_DIR/logs/launchd.out 2>> $PROJECT_DIR/logs/launchd.err" >> /tmp/_cron.$$
crontab /tmp/_cron.$$
rm -f /tmp/_cron.$$
echo "✅ crontab 이중 백업 등록 완료 (매일 00:00 자정 실행, 재부팅 자동 지속)"

# 4) 검증
echo "--- 스케줄러 등록 상태 검증 ---"
launchctl list | grep -iE 'daily-naver-blog' || echo "(launchctl 등록 확인 실패)"
crontab -l | grep -iE 'daily-naver-blog' || echo "(crontab 등록 확인 실패)"
