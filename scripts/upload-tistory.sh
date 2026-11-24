#!/usr/bin/env bash
#
# 티스토리 블로그 Playwright 자동 등록 원클릭 도구
#
set -euo pipefail

PROJECT_DIR="/Users/user/CursorProjects/ai-blog-notes"
cd "$PROJECT_DIR"

PYTHON_BIN="python3 -u"

show_help() {
    echo "=========================================================="
    echo " 🚀 티스토리 블로그 Playwright 자동 등록 도구"
    echo "=========================================================="
    echo "사용법:"
    echo "  $0                  # 오늘 작성된 모든 글 즉시 정식 공개 발행 (기본값)"
    echo "  $0 --publish|-a     # 오늘 작성된 모든 글 즉시 정식 공개 발행"
    echo "  $0 --test|-t        # 1번 포스트 즉시 공개 발행 시험"
    echo "  $0 --draft          # 임시저장 모드로 등록"
    echo "  $0 --private-all    # 오늘 작성된 글 비공개로 일괄 발행"
    echo "  $0 --login|-l       # 티스토리(카카오) 로그인 창 띄우기"
    echo "  $0 --keep-alive|-k  # 티스토리 세션 유효성 점검 및 갱신(킵얼라이브)"
    echo "=========================================================="
    exit 0
}

MODE="${1:-}"

case "$MODE" in
    --login|-l)
        echo "🌐 티스토리(카카오) 로그인 창을 엽니다..."
        $PYTHON_BIN tools/setup_tistory_login.py
        ;;
    --keep-alive|-k)
        echo "💓 티스토리 세션 킵얼라이브 확인 중..."
        $PYTHON_BIN tools/keep_tistory_alive.py
        ;;
    --test|-t|--publish-test|-p)
        echo "🚀 1번 포스트를 티스토리에 즉시 정식 공개 발행합니다..."
        $PYTHON_BIN tools/upload_tistory_playwright.py --single=1 --mode=publish
        ;;
    --draft|-d)
        echo "📝 포스트를 티스토리에 임시저장합니다..."
        $PYTHON_BIN tools/upload_tistory_playwright.py --all --mode=draft
        ;;
    --private-all)
        echo "🔒 오늘 작성된 포스트를 티스토리에 비공개로 발행합니다..."
        $PYTHON_BIN tools/upload_tistory_playwright.py --all --mode=private
        ;;
    --all|-a|--publish|--publish-all|-P|"")
        echo "🚀 오늘 작성된 포스트를 티스토리에 즉시 정식 공개 발행(PUBLISH)합니다..."
        $PYTHON_BIN tools/upload_tistory_playwright.py --all --mode=publish
        ;;
    *)
        show_help
        ;;
esac
