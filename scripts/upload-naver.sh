#!/usr/bin/env bash
#
# 네이버 블로그 Playwright 자동 등록 원클릭 도구
#
set -euo pipefail

PROJECT_DIR="/Users/user/CursorProjects/ai-blog-notes"
cd "$PROJECT_DIR"

PYTHON_BIN="python3 -u"

show_help() {
    echo "=========================================================="
    echo " 🚀 네이버 블로그 Playwright 자동 등록 도구"
    echo "=========================================================="
    echo "사용법:"
    echo "  $0                  # 오늘 작성된 모든 글 즉시 정식 발행 (기본값)"
    echo "  $0 --publish|-a     # 오늘 작성된 모든 글 즉시 정식 발행"
    echo "  $0 --test|-t        # 1번 포스트 즉시 정식 발행 시험"
    echo "  $0 --draft          # 임시저장 모드로 등록"
    echo "  $0 --login|-l       # 최초 1회 네이버 로그인 창 띄우기"
    echo "=========================================================="
    exit 0
}

MODE="${1:-}"

case "$MODE" in
    --login|-l)
        echo "🌐 네이버 로그인 창을 엽니다..."
        $PYTHON_BIN tools/setup_browser_login.py
        ;;
    --test|-t|--publish-test|-p)
        echo "🚀 1번 포스트를 네이버 블로그에 즉시 정식 발행합니다..."
        $PYTHON_BIN tools/upload_naver_playwright.py --single=1 --mode=publish
        ;;
    --draft|-d)
        echo "📝 포스트를 네이버 블로그에 임시저장합니다..."
        $PYTHON_BIN tools/upload_naver_playwright.py --all --mode=draft
        ;;
    --all|-a|--publish|--publish-all|-P|"")
        echo "🚀 오늘 작성된 포스트를 네이버 블로그에 즉시 정식 발행(PUBLISH)합니다..."
        $PYTHON_BIN tools/upload_naver_playwright.py --all --mode=publish
        ;;
    *)
        show_help
        ;;
esac
        show_help
        ;;
esac
