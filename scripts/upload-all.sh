#!/usr/bin/env bash
#
# 3대 블로그(네이버·티스토리·워드프레스) 원클릭 통합 자동 등록 도구
#
# [안전 강화 업데이트]
# 네이버 계정 보호(보호조치 방지)를 위해 네이버는 기본 1편 안전 등록이 적용됩니다.
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
    echo "  $0                  # 3대 플랫폼 정식 발행 (네이버는 1편 안전 등록)"
    echo "  $0 --publish|-p     # 3대 플랫폼 정식 발행"
    echo "  $0 --skip-naver     # 네이버 제외, 티스토리·워드프레스만 자동 발행 (추천)"
    echo "  $0 --reserve        # 네이버 등록 시 예약 발행 모드 적용"
    echo "  $0 --test|-t        # 3대 플랫폼 1번 포스트 시험 발행"
    echo "  $0 --login|-l       # 3대 플랫폼 로그인 세션 통합 확인"
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
    --skip-naver)
        $PYTHON_BIN tools/upload_all_playwright.py --publish --skip-naver
        ;;
    --reserve)
        $PYTHON_BIN tools/upload_all_playwright.py --publish --naver-reserve
        ;;
    --all|-a|--publish|-p|"")
        $PYTHON_BIN tools/upload_all_playwright.py --publish
        ;;
    *)
        show_help
        ;;
esac
