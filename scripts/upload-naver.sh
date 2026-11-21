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
    echo "  $0 --login          # 최초 1회 네이버 로그인 창 띄우기"
    echo "  $0 --test           # 1번 포스트 임시저장 시험 등록"
    echo "  $0 --all            # 오늘 작성된 30편 전체 임시저장 등록"
    echo "  $0 --publish-test   # 1번 포스트 실제 발행 시험"
    echo "=========================================================="
    exit 0
}

MODE="${1:-}"

case "$MODE" in
    --login|-l)
        echo "🌐 네이버 로그인 창을 엽니다..."
        $PYTHON_BIN tools/setup_browser_login.py
        ;;
    --test|-t)
        echo "📝 1번 포스트를 네이버 블로그에 시험 등록(임시저장)합니다..."
        $PYTHON_BIN tools/upload_naver_playwright.py --single=1 --mode=draft
        ;;
    --all|-a)
        echo "📚 오늘 작성된 30편 전체를 네이버 블로그에 안전하게 임시저장합니다..."
        $PYTHON_BIN tools/upload_naver_playwright.py --all --mode=draft
        ;;
    --publish-test|-p)
        echo "🚀 1번 포스트를 네이버 블로그에 실제 정식 발행합니다..."
        $PYTHON_BIN tools/upload_naver_playwright.py --single=1 --mode=publish
        ;;
    *)
        show_help
        ;;
esac
