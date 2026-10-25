#!/usr/bin/env bash
#
# 매일 00:00 launchd(LaunchAgent) 및 crontab으로 실행:
# 네이버 블로그 · 티스토리 · 워드프레스 3대 채널 일별 포스팅(.md, .html) 및
# 각 작업실 대시보드(blog/*/index.html)와 멀티 포털(index.html)을 자동 생성/갱신합니다.
#
# 맥이 슬립(잠자기) 상태여도 launchd의 StartCalendarInterval에 의해 깨어나는 즉시 실행되며,
# 실행 중 맥이 다시 잠들지 않도록 caffeinate로 슬립을 방지합니다.
#
set -euo pipefail

# 실행 PATH 보강 (cron/launchd 환경 필수)
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

PROJECT_DIR="/Users/user/CursorProjects/ai-blog-notes"
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

cd "$PROJECT_DIR"

# 배치 실행 도중 맥이 유휴 슬립으로 들어가지 않도록 10분간 슬립 차단
caffeinate -i -t 600 &

echo "========================================================"
echo "🕒 [$(date '+%Y-%m-%d %H:%M:%S')] 멀티 블로그(네이버·티스토리·워드프레스) 00시 자동화 배치 시작"
echo "========================================================"

# caffeinate -is: 파이썬 통합 배치가 끝날 때까지 시스템 및 디스플레이 절전 방지
# (daily_naver_batch.py 내부에서 네이버 -> 티스토리 -> 워드프레스 -> 가이드 뷰어 -> Git 커밋/푸시까지 순차 실행)
caffeinate -is /usr/bin/python3 "$PROJECT_DIR/tools/daily_naver_batch.py"

echo "========================================================"
echo "🎉 [$(date '+%Y-%m-%d %H:%M:%S')] 멀티 블로그(네이버·티스토리·워드프레스) 00시 자동화 배치 종료"
echo "========================================================"
