#!/usr/bin/env bash
#
# 네이버 블로그 Playwright 안티디텍트 안전 등록 도구 (방안 C)
#
# 네이버 계정 보호(보호조치 방지)를 위해 기본 브라우저 화면 표시(Headless=False) 및
# 1회 최대 1~2편 안전 제한, 무작위 타이핑/지연이 적용됩니다.
#
set -euo pipefail

PROJECT_DIR="/Users/user/CursorProjects/ai-blog-notes"
cd "$PROJECT_DIR"

PYTHON_BIN="python3 -u"

show_help() {
    echo "=========================================================="
    echo " 🛡️ 네이버 블로그 Playwright 안티디텍트 안전 등록 도구"
    echo "=========================================================="
    echo "사용법:"
    echo "  $0                  # 오늘 작성된 상위 1편 안전 정식 발행 (기본값)"
    echo "  $0 --publish|-p     # 오늘 작성된 상위 1편 안전 정식 발행"
    echo "  $0 --reserve|-r     # 즉시 발행 대신 '예약 발행'으로 등록"
    echo "  $0 --test|-t        # 1번 포스트 안전 정식 발행 시험"
    echo "  $0 --single 2       # 2번 포스트만 단건 등록"
    echo "  $0 --draft|-d       # 임시저장(Draft) 모드로 등록"
    echo "  $0 --login|-l       # 네이버 1회 브라우저 로그인 세션 생성"
    echo "=========================================================="
    exit 0
}

MODE="${1:-}"

case "$MODE" in
    --login|-l)
        echo "🌐 네이버 로그인 창을 엽니다..."
        $PYTHON_BIN tools/setup_browser_login.py
        ;;
    --test|-t|--publish-test)
        echo "🚀 1번 포스트를 네이버 블로그에 안전 정식 발행합니다..."
        $PYTHON_BIN tools/upload_naver_playwright.py --single=1 --mode=publish
        ;;
    --reserve|-r)
        echo "⏰ 포스트를 네이버 블로그에 '예약 발행' 모드로 등록합니다..."
        $PYTHON_BIN tools/upload_naver_playwright.py --limit=1 --mode=publish --reserve
        ;;
    --single)
        NUM="${2:-1}"
        echo "🚀 ${NUM}번 포스트를 네이버 블로그에 안전 정식 발행합니다..."
        $PYTHON_BIN tools/upload_naver_playwright.py --single="$NUM" --mode=publish
        ;;
    --draft|-d)
        echo "📝 포스트를 네이버 블로그에 임시저장합니다..."
        $PYTHON_BIN tools/upload_naver_playwright.py --limit=1 --mode=draft
        ;;
    --all|-a|--publish|-p|"")
        echo "🚀 오늘 작성된 포스트 중 1편을 네이버 블로그에 안전 정식 발행합니다..."
        $PYTHON_BIN tools/upload_naver_playwright.py --limit=1 --mode=publish
        ;;
    *)
        show_help
        ;;
esac
