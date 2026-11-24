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
    echo " 🚀 멀티 블로그 자동 등록 도구 (계정 보호 강화 모드)"
    echo "=========================================================="
    echo "사용법:"
    echo "  $0                  # 티스토리·워드프레스 정식 자동 발행 (네이버 자동 제외: 계정보호)"
    echo "  $0 --publish|-p     # 티스토리·워드프레스 정식 자동 발행"
    echo "  $0 --include-naver  # 네이버 1편 안전 발행 포함 (보호조치 방지 1편 제한)"
    echo "  $0 --reserve        # 네이버 포함 시 예약 발행 모드 적용"
    echo "  $0 --test|-t        # 1번 포스트 시험 발행"
    echo "  $0 --login|-l       # 로그인 세션 통합 확인"
    echo "  $0 --draft|-d       # 임시저장 모드로 등록"
    echo "=========================================================="
    exit 0
}

MODE="${1:-}"

case "$MODE" in
    --login|-l)
        $PYTHON_BIN tools/upload_all_playwright.py --login --skip-naver
        ;;
    --login-all)
        $PYTHON_BIN tools/upload_all_playwright.py --login --include-naver
        ;;
    --test|-t|--publish-test)
        $PYTHON_BIN tools/upload_all_playwright.py --test --skip-naver
        ;;
    --draft|-d)
        $PYTHON_BIN tools/upload_all_playwright.py --draft --skip-naver
        ;;
    --include-naver)
        $PYTHON_BIN tools/upload_all_playwright.py --publish --include-naver
        ;;
    --reserve)
        $PYTHON_BIN tools/upload_all_playwright.py --publish --include-naver --naver-reserve
        ;;
    --all|-a|--publish|-p|"")
        # 기본값: 네이버 계정 보호(보호조치 방지)를 위해 네이버는 Playwright 자동화에서 안전하게 제외하고,
        # 티스토리와 워드프레스만 전자동 정식 발행합니다.
        # 네이버는 100% 안전한 1-Click 서식 복사(./scripts/copy-naver.sh)를 사용합니다.
        $PYTHON_BIN tools/upload_all_playwright.py --publish --skip-naver
        echo ""
        echo "=========================================================="
        echo " 🛡️ [네이버 계정 보호 안내]"
        echo " 네이버 어뷰징 탐지(아이디 보호조치)를 원천 방지하기 위해"
        echo " 네이버는 Playwright 자동 등록에서 기본 제외되었습니다."
        echo " 👉 네이버 오늘 글 등록: ./scripts/copy-naver.sh (30초 1-Click 수동 등록)"
        echo "=========================================================="
        ;;
    *)
        show_help
        ;;
esac
