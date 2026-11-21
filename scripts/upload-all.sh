#!/usr/bin/env bash
#
# 3대 블로그(네이버·티스토리·워드프레스) 원클릭 통합 자동 등록 도구
#
# 단 1번의 명령어로 세션 점검부터 3대 플랫폼 전체 정식 발행까지 완료합니다.
#
set -euo pipefail

PROJECT_DIR="/Users/user/CursorProjects/ai-blog-notes"
cd "$PROJECT_DIR"

PYTHON_BIN="python3 -u"

show_help() {
    echo "=========================================================="
    echo " 🚀 3대 블로그(네이버·티스토리·워드프레스) 통합 자동 등록 도구"
    echo "=========================================================="
    echo "사용법:"
    echo "  $0                  # 3대 플랫폼 전체 즉시 정식 발행 (단 1번의 명령어로 끝!)"
    echo "  $0 --publish|-p     # 3대 플랫폼 전체 즉시 정식 발행"
    echo "  $0 --test|-t        # 3대 플랫폼 1번 포스트 시험 발행"
    echo "  $0 --login|-l       # 3대 플랫폼 로그인 세션 통합 확인/재설정"
    echo "  $0 --draft|-d       # 3대 플랫폼 임시저장 모드로 등록"
    echo "=========================================================="
    exit 0
}

MODE="${1:-}"

case "$MODE" in
    --login|-l)
        $PYTHON_BIN tools/upload_all_playwright.py --login
        ;;
    --test|-t|--publish-test)
        $PYTHON_BIN tools/upload_all_playwright.py --test
        ;;
    --draft|-d)
        $PYTHON_BIN tools/upload_all_playwright.py --draft
        ;;
    --all|-a|--publish|-p|"")
        $PYTHON_BIN tools/upload_all_playwright.py --publish
        ;;
    *)
        show_help
        ;;
esac
